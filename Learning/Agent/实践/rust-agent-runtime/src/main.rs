use std::collections::BTreeMap;

use rust_agent_runtime::{
    AgentRuntime, Limits, ModelOutput, ScriptedModel, SumTool, ToolCall, ToolRegistry,
};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let model = ScriptedModel::new([
        ModelOutput::ToolCall(ToolCall {
            name: "sum".to_owned(),
            arguments: BTreeMap::from([
                ("a".to_owned(), "20".to_owned()),
                ("b".to_owned(), "22".to_owned()),
            ]),
        }),
        ModelOutput::Final("The result is 42.".to_owned()),
    ]);

    let mut tools = ToolRegistry::default();
    tools.register(SumTool)?;

    let mut runtime = AgentRuntime::new(model, tools, Limits::default());
    let result = runtime.run("Add 20 and 22")?;
    println!("final: {}", result.final_output);
    println!("steps: {}, tool calls: {}", result.steps, result.tool_calls);
    for event in result.trace {
        println!("trace: {event:?}");
    }
    Ok(())
}
