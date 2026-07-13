# Serde、配置与日志

## 1. Serde 的角色

Serde 把 Rust 类型与外部数据格式之间的序列化/反序列化分开。它不验证业务逻辑，也不自动提供版本兼容策略。

```rust
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
struct User {
    id: u64,
    name: String,
}
```

JSON：

```rust
let json = serde_json::to_string(&user)?;
let user: User = serde_json::from_str(&json)?;
```

## 2. 外部 schema 与内部类型

外部输入是不可信的。反序列化成功只表示字段形状符合类型，不代表值满足业务约束：

```rust
#[derive(Deserialize)]
struct CreateUserInput {
    name: String,
}

impl TryFrom<CreateUserInput> for User {
    type Error = ValidationError;

    fn try_from(input: CreateUserInput) -> Result<Self, Self::Error> {
        User::new(input.name)
    }
}
```

把“解析”和“验证”分成两步，避免把任意可反序列化值当作已验证领域对象。

## 3. 常用属性

```rust
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Config {
    #[serde(default = "default_host")]
    host: String,
    #[serde(default = "default_port")]
    port: u16,
}
```

常用属性：`rename`、`rename_all`、`default`、`skip_serializing`、`skip_deserializing`、`flatten`、`untagged`、`deny_unknown_fields`。

要谨慎使用 `untagged`：多个变体可能匹配歧义，错误信息也不够清晰。公共格式应考虑显式 tag、版本字段和未知字段策略。

## 4. 配置

配置来源常见顺序：默认值 → 配置文件 → 环境变量 → 命令行参数。必须明确优先级，并在启动时完成解析和验证，之后传递不可变配置。

配置中不应直接打印密码、token、私钥或完整连接字符串。秘密最好来自受控环境、系统钥匙串或秘密管理服务，而不是提交到仓库的文件。

不要让配置对象在程序运行中到处被修改；如果必须热更新，定义版本、并发和回滚语义。

## 5. 版本和兼容性

序列化格式应考虑：

- schema/version 字段。
- 缺失字段的默认值。
- 未知字段是忽略还是拒绝。
- 枚举变体新增时旧版本如何处理。
- 迁移失败时是否拒绝启动或拒绝恢复。

“能反序列化”不等于“兼容”；兼容策略需要 golden fixture 和迁移测试。

## 6. 日志与 tracing

`tracing` 适合异步和结构化上下文：

```rust
use tracing::{info, instrument};

#[instrument(skip(secret))]
fn handle(id: u64, secret: &str) {
    info!(user_id = id, "handling request");
}
```

日志字段应使用稳定键名，避免把大段用户输入直接拼进消息。请求 ID、任务 ID 和耗时有助于关联调用链；秘密、凭据和敏感内容必须脱敏或不记录。

`stdout`、`stderr` 和结构化日志应有清晰契约。面向机器的 JSON 输出不要被人类日志污染。

## 7. 观测不是业务状态

日志、指标和 tracing span 用于观察程序，不应成为唯一的业务事实来源。关键状态应保存在返回值、事件或持久化记录中；日志丢失时程序仍应保持正确语义。

## 8. 练习

设计一个带 `version` 的配置格式，支持 JSON 文件和环境变量覆盖；拒绝未知字段；校验端口和超时；用 tracing 输出请求 ID，但确认秘密不会出现在日志和错误文本中。

`#rust #serde #serialization #configuration #tracing #observability`
