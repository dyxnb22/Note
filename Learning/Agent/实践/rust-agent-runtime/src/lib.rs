use std::collections::{BTreeMap, HashMap, VecDeque};
use std::error::Error;
use std::fmt::{self, Display, Formatter};
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};

pub type Arguments = BTreeMap<String, String>;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ToolSpec {
    pub name: String,
    pub description: String,
    pub required: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ToolCall {
    pub name: String,
    pub arguments: Arguments,
}

impl ToolCall {
    fn fingerprint(&self) -> String {
        // 指纹用于识别同一工具和参数的重复调用；生产实现还应固定参数序列化规范。
        let arguments = self
            .arguments
            .iter()
            .map(|(key, value)| format!("{key}={value}"))
            .collect::<Vec<_>>()
            .join("&");
        format!("{}?{arguments}", self.name)
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ModelOutput {
    Final(String),
    ToolCall(ToolCall),
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Message {
    User(String),
    ToolResult { tool_name: String, output: String },
}

pub trait Model {
    fn next(&mut self, history: &[Message]) -> Result<ModelOutput, AgentError>;
}

pub trait Tool: Send + Sync {
    fn spec(&self) -> ToolSpec;
    fn call(&self, arguments: &Arguments) -> Result<String, ToolError>;
}

#[derive(Default)]
pub struct ToolRegistry {
    tools: HashMap<String, Arc<dyn Tool>>,
}

impl ToolRegistry {
    pub fn register<T: Tool + 'static>(&mut self, tool: T) -> Result<(), AgentError> {
        let name = tool.spec().name;
        // 工具名冲突会让模型看到的能力和实际执行目标不确定，注册阶段直接拒绝。
        if self.tools.contains_key(&name) {
            return Err(AgentError::DuplicateTool(name));
        }
        self.tools.insert(name, Arc::new(tool));
        Ok(())
    }

    fn get(&self, name: &str) -> Option<Arc<dyn Tool>> {
        self.tools.get(name).cloned()
    }

    pub fn specs(&self) -> Vec<ToolSpec> {
        let mut specs = self
            .tools
            .values()
            .map(|tool| tool.spec())
            .collect::<Vec<_>>();
        specs.sort_by(|left, right| left.name.cmp(&right.name));
        specs
    }
}

#[derive(Debug, Clone, Copy)]
pub struct Limits {
    pub max_steps: usize,
    pub max_tool_calls: usize,
    pub max_repeated_call: usize,
}

impl Default for Limits {
    fn default() -> Self {
        Self {
            max_steps: 8,
            max_tool_calls: 6,
            max_repeated_call: 2,
        }
    }
}

#[derive(Debug, Clone, Default)]
pub struct CancellationToken(Arc<AtomicBool>);

impl CancellationToken {
    pub fn cancel(&self) {
        // 这是协作式取消：Runtime 在模型调用和工具调用边界检查，不能撤销已提交副作用。
        self.0.store(true, Ordering::Release);
    }

    pub fn is_cancelled(&self) -> bool {
        self.0.load(Ordering::Acquire)
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum TraceEvent {
    StepStarted { step: usize },
    ToolCalled { step: usize, name: String },
    ToolCompleted { step: usize, name: String },
    Finished { step: usize },
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RunResult {
    pub final_output: String,
    pub steps: usize,
    pub tool_calls: usize,
    pub trace: Vec<TraceEvent>,
}

pub struct AgentRuntime<M> {
    model: M,
    tools: ToolRegistry,
    limits: Limits,
    cancellation: CancellationToken,
}

impl<M: Model> AgentRuntime<M> {
    pub fn new(model: M, tools: ToolRegistry, limits: Limits) -> Self {
        Self {
            model,
            tools,
            limits,
            cancellation: CancellationToken::default(),
        }
    }

    pub fn with_cancellation(mut self, cancellation: CancellationToken) -> Self {
        self.cancellation = cancellation;
        self
    }

    pub fn run(&mut self, prompt: impl Into<String>) -> Result<RunResult, AgentError> {
        let mut history = vec![Message::User(prompt.into())];
        let mut trace = Vec::new();
        let mut tool_calls = 0;
        let mut repeated_calls: HashMap<String, usize> = HashMap::new();

        for step in 1..=self.limits.max_steps {
            self.check_cancelled()?;
            trace.push(TraceEvent::StepStarted { step });

            match self.model.next(&history)? {
                ModelOutput::Final(final_output) => {
                    trace.push(TraceEvent::Finished { step });
                    return Ok(RunResult {
                        final_output,
                        steps: step,
                        tool_calls,
                        trace,
                    });
                }
                ModelOutput::ToolCall(call) => {
                    tool_calls += 1;
                    // 预算在执行前检查，避免一个恶意/失控模型耗尽整个任务资源。
                    if tool_calls > self.limits.max_tool_calls {
                        return Err(AgentError::LimitExceeded("tool calls"));
                    }

                    let fingerprint = call.fingerprint();
                    let repeated = repeated_calls.entry(fingerprint).or_default();
                    *repeated += 1;
                    if *repeated > self.limits.max_repeated_call {
                        return Err(AgentError::RepeatedToolCall(call.name));
                    }

                    let tool = self
                        .tools
                        .get(&call.name)
                        .ok_or_else(|| AgentError::UnknownTool(call.name.clone()))?;
                    trace.push(TraceEvent::ToolCalled {
                        step,
                        name: call.name.clone(),
                    });
                    // 工具前再次检查取消，覆盖模型返回后到真正副作用之间的窗口。
                    self.check_cancelled()?;
                    let output = tool.call(&call.arguments).map_err(AgentError::Tool)?;
                    trace.push(TraceEvent::ToolCompleted {
                        step,
                        name: call.name.clone(),
                    });
                    history.push(Message::ToolResult {
                        tool_name: call.name,
                        output,
                    });
                }
            }
        }

        Err(AgentError::LimitExceeded("steps"))
    }

    fn check_cancelled(&self) -> Result<(), AgentError> {
        if self.cancellation.is_cancelled() {
            Err(AgentError::Cancelled)
        } else {
            Ok(())
        }
    }
}

#[derive(Debug)]
pub enum AgentError {
    Cancelled,
    DuplicateTool(String),
    LimitExceeded(&'static str),
    Model(String),
    RepeatedToolCall(String),
    Tool(ToolError),
    UnknownTool(String),
}

impl Display for AgentError {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> fmt::Result {
        match self {
            Self::Cancelled => write!(formatter, "run cancelled"),
            Self::DuplicateTool(name) => write!(formatter, "duplicate tool: {name}"),
            Self::LimitExceeded(limit) => write!(formatter, "{limit} limit exceeded"),
            Self::Model(message) => write!(formatter, "model failed: {message}"),
            Self::RepeatedToolCall(name) => write!(formatter, "repeated tool call: {name}"),
            Self::Tool(error) => write!(formatter, "tool failed: {error}"),
            Self::UnknownTool(name) => write!(formatter, "unknown tool: {name}"),
        }
    }
}

impl Error for AgentError {}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ToolError(pub String);

impl Display for ToolError {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> fmt::Result {
        formatter.write_str(&self.0)
    }
}

impl Error for ToolError {}

pub struct ScriptedModel {
    outputs: VecDeque<ModelOutput>,
}

impl ScriptedModel {
    pub fn new(outputs: impl IntoIterator<Item = ModelOutput>) -> Self {
        Self {
            outputs: outputs.into_iter().collect(),
        }
    }
}

impl Model for ScriptedModel {
    fn next(&mut self, _history: &[Message]) -> Result<ModelOutput, AgentError> {
        self.outputs
            .pop_front()
            .ok_or_else(|| AgentError::Model("script exhausted".to_owned()))
    }
}

pub struct SumTool;

impl Tool for SumTool {
    fn spec(&self) -> ToolSpec {
        ToolSpec {
            name: "sum".to_owned(),
            description: "Add two signed integers".to_owned(),
            required: vec!["a".to_owned(), "b".to_owned()],
        }
    }

    fn call(&self, arguments: &Arguments) -> Result<String, ToolError> {
        // Tool 边界负责参数存在性和类型校验；Model 传入的字符串不能直接信任。
        let parse = |name: &str| {
            arguments
                .get(name)
                .ok_or_else(|| ToolError(format!("missing argument: {name}")))?
                .parse::<i64>()
                .map_err(|_| ToolError(format!("argument {name} must be an integer")))
        };
        Ok((parse("a")? + parse("b")?).to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn sum_call() -> ModelOutput {
        ModelOutput::ToolCall(ToolCall {
            name: "sum".to_owned(),
            arguments: BTreeMap::from([
                ("a".to_owned(), "20".to_owned()),
                ("b".to_owned(), "22".to_owned()),
            ]),
        })
    }

    #[test]
    fn completes_after_a_tool_call() {
        let model = ScriptedModel::new([sum_call(), ModelOutput::Final("42".to_owned())]);
        let mut tools = ToolRegistry::default();
        tools.register(SumTool).unwrap();
        let mut runtime = AgentRuntime::new(model, tools, Limits::default());

        let result = runtime.run("add the numbers").unwrap();
        assert_eq!(result.final_output, "42");
        assert_eq!(result.steps, 2);
        assert_eq!(result.tool_calls, 1);
    }

    #[test]
    fn stops_repeated_tool_calls() {
        let model = ScriptedModel::new([sum_call(), sum_call(), sum_call()]);
        let mut tools = ToolRegistry::default();
        tools.register(SumTool).unwrap();
        let mut runtime = AgentRuntime::new(model, tools, Limits::default());

        let error = runtime.run("loop forever").unwrap_err();
        assert!(matches!(error, AgentError::RepeatedToolCall(name) if name == "sum"));
    }

    #[test]
    fn observes_cancellation_before_starting() {
        let cancellation = CancellationToken::default();
        cancellation.cancel();
        let model = ScriptedModel::new([ModelOutput::Final("never".to_owned())]);
        let mut runtime = AgentRuntime::new(model, ToolRegistry::default(), Limits::default())
            .with_cancellation(cancellation);

        assert!(matches!(runtime.run("stop"), Err(AgentError::Cancelled)));
    }

    #[test]
    fn rejects_unknown_tools() {
        let model = ScriptedModel::new([ModelOutput::ToolCall(ToolCall {
            name: "shell".to_owned(),
            arguments: Arguments::new(),
        })]);
        let mut runtime = AgentRuntime::new(model, ToolRegistry::default(), Limits::default());

        let error = runtime.run("run a command").unwrap_err();
        assert!(matches!(error, AgentError::UnknownTool(name) if name == "shell"));
    }
}
