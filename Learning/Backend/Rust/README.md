# Rust

本目录现在保留 Rust 的面试入口。语言核心、Cargo、IO、Serde、Async、Tokio、Web、数据库、性能、unsafe/FFI 和 Agent Runtime 已合并进 [Rust 面试题库](./面试题库/README.md)。

## 进入方式

- 面试与系统化复习：先读 [Rust 面试题库](./面试题库/README.md)。
- 写代码时使用 `cargo check`、`cargo test`、`cargo fmt` 和 `cargo clippy` 验证。
- 具体 crate/API 以项目锁定的 Rust Edition、工具链和依赖版本为准。

## Rust 题库覆盖

- 语言与类型：语法、模式、所有权、生命周期、struct/enum、trait、集合和错误。
- 工程与运行时：模块、Cargo、Serde、日志、线程、Future、Tokio、取消和背压。
- 系统能力：文件/进程/网络、Web、数据库、性能、宏、unsafe、FFI 和安全边界。
- Agent Runtime：Provider、Tool、权限、有限状态、预算、Checkpoint、恢复和评测。
