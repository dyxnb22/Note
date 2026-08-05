# Rust 通用知识与 Agent 路线

这套笔记面向希望用 Rust 编写可靠后端、命令行工具和网络服务的开发者。
内容分成两部分：Rust 语言核心，以及建立在语言之上的通用后端实践。

## 学习路线

建议按下面的顺序学习，不必一次读完：

1. [01_Rust基础语法与控制流](01_Rust基础语法与控制流.md)
2. [02_Rust所有权、借用与生命周期](02_Rust所有权、借用与生命周期.md)
3. [03_Struct、Enum、Trait与泛型](03_Struct、Enum、Trait与泛型.md)
4. [04_集合、字符串与迭代器](04_集合、字符串与迭代器.md)
5. [05_Result、Option与错误处理](05_Result、Option与错误处理.md)
6. [06_模块、可见性与测试](06_模块、可见性与测试.md)
7. [07_Cargo、Crate与项目组织](07_Cargo、Crate与项目组织.md)
8. [08_智能指针与内部可变性](08_智能指针与内部可变性.md)
9. [09_文件系统、进程与网络IO](09_文件系统、进程与网络IO.md)
10. [10_Serde、配置与日志](10_Serde、配置与日志.md)
11. [11_并发安全与Async基础](11_并发安全与Async基础.md)
12. [12_Tokio与异步网络服务](12_Tokio与异步网络服务.md)
13. [13_Web服务与数据库](13_Web服务与数据库.md)
14. [14_Rust性能模型与适用边界](14_Rust性能模型与适用边界.md)
15. [15_宏、unsafe与FFI](15_宏、unsafe与FFI.md)
16. [16_Rust Agent工程化](16_Rust%20Agent工程化.md)

## 按目标裁剪

- Agent Runtime/Harness：完成 01–07、09–12，再进入 16；13–14 按服务化和性能需要补充，15 按需。
- 通用后端：完成 01–14；只有原生边界确有需要时进入 15。
- CLI/系统工具：完成 01–10，再按并发和嵌入需求选择 11–15。

Rust Agent 的跨目录顺序、Go 后端并行主线与验收产物见：[Rust Agent 与 Go 后端学习地图](../../00_Navigation/Rust-Agent与Go后端学习地图.md)。可运行的第一阶段见：[rust-agent-runtime](../../Agent/实践/rust-agent-runtime/README.md)。

## 每个阶段都要做什么

- 读完概念后，自己写一个最小例子，不要只抄代码。
- 用 `cargo check`、`cargo test`、`cargo fmt` 和 `cargo clippy` 检查结果。
- 遇到编译错误，先理解所有权、类型或 trait 约束，再决定是否调整设计。
- 给每个练习补正常路径、错误路径和边界条件。
- 先使用标准库，确有需求时再引入第三方 crate。

## 常用命令

```bash
cargo new hello-rust
cargo new --lib my-library
cargo check
cargo build
cargo build --release
cargo run
cargo test
cargo test test_name
cargo fmt --all
cargo clippy --all-targets --all-features -- -D warnings
cargo doc --open
```

## 推荐练习顺序

1. 命令行猜数字：变量、输入、`match`、错误处理。
2. 文本统计器：`String`、`&str`、`HashMap`、迭代器。
3. Todo 库：模块、struct、enum、trait、单元测试和集成测试。
4. 文件索引器：路径、文件读取、错误传播、并发。
5. JSON HTTP 服务：Serde、Tokio、请求处理、日志和数据库。
6. Agent Runtime：Tool Registry、有限循环、预算、取消、Trace 和恢复。

## 判断是否真正掌握

能够解释：一个值现在由谁拥有；一个引用能活多久；一个错误在哪里被处理；一个 trait 为什么放在那个边界；一个 async 任务在哪里等待；一个请求失败后资源是否释放。

这套笔记是知识地图，不是 Rust 参考手册。遇到具体 API 时，应同时查看 `rustc --explain`、标准库文档和 crate 的官方文档。

当前正式路线以 Edition 2024 为基准；语言语义参考 [The Rust Programming Language](https://doc.rust-lang.org/book/)，Async 参考 [Async Book](https://rust-lang.github.io/async-book/)。具体 Crate API 随版本变化，实践项目应锁定依赖并记录验证版本。

`#rust #backend #systems #async #cargo`
