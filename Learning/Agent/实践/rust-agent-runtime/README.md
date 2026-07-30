# Rust Agent Runtime

这是 [Rust Agent 工程化](../../../Backend/Rust/16_Rust%20Agent工程化.md) 的阶段 A：一个无第三方依赖、可运行和可测试的确定性 Agent Runtime。

它演示：

- `ModelOutput` 有限结果类型；
- 动态 Tool Registry 与稳定 Tool Spec；
- Step/Tool 预算和重复调用检测；
- 协作式取消；
- 可检查的 Trace Event；
- 使用脚本模型进行确定性测试。

## 运行

要求 Rust 1.85 或更高版本、Edition 2024：

```bash
cargo fmt --all --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test
cargo run
```

预期 `cargo run` 输出最终结果、Step 数、Tool 调用数和 Trace。测试覆盖正常完成、重复调用、启动前取消和未知 Tool。

## 为什么暂时没有真实模型调用

第一阶段先证明 Runtime 不变量，不让网络、密钥和 Provider 差异掩盖状态机问题。`ScriptedModel` 不是模型 Mock 的最终形态，而是可重复测试 Agent Loop 的控制器。

## 后续阶段

1. 新增 `provider` 模块：Tokio + HTTP/SSE，映射到现有 `ModelOutput`。
2. 把字符串参数升级为 Serde DTO 与 JSON Schema，在 Tool 边界完成解析和业务校验。
3. 新增受限文件、Patch 和进程 Tool；加入审批、路径和输出限制。
4. 把 Trace 写成版本化事件，增加 Checkpoint、Resume 和任务 Eval。

接入真实 Provider 时，密钥只从环境或秘密系统读取；测试使用 Fixture/本地 Stub，不要求 CI 访问外部模型。
