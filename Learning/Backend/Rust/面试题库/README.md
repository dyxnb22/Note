# Rust 面试题库

这是一份 Rust 面试题库，按所有权/类型、并发/Async、工程、系统设计和项目表达组织。

## 推荐顺序

1. [[00_复习路线与答题模板]]、[[00_主题速答卡]]
2. [[01_所有权与类型系统]]：ownership、borrow、lifetime、trait、错误和智能指针。
3. [[02_并发、Async与工程]]：线程、Send/Sync、Future、Pin、Tokio、取消、Cargo、unsafe 和性能。
4. [[03_编码与系统设计]]：算法、Result、Worker Pool、文件索引、网络服务和工具执行器。

## 覆盖范围

- 语言与类型：语法、模式、所有权、生命周期、struct/enum、trait、`Vec`、`HashMap`、`HashSet`、`BTreeMap`、`BTreeSet` 和错误。
- 工程与运行时：模块、Cargo、Serde、日志、线程、Future、Tokio、取消和背压。
- 系统能力：文件/进程/网络、Web、数据库、性能、宏、unsafe、FFI 和安全边界。
- 表达：算法、Worker Pool、工具执行器、Checkpoint、恢复和项目选型。

## 答题边界

- Rust 编译器证明的是类型/内存/部分并发安全，不是业务一致性、权限、性能和远端副作用。
- 回答要区分语言语义、标准库、Tokio/crate 行为和目标 Edition/版本。

## 实践验收

- 语言与集合：用 `cargo check` 和 `cargo test` 验证所有权、字符串边界、哈希集合和有序集合的选择。
- 异步与并发：用有界 channel、取消、超时和可控事件测试 Worker Pool，确认任务和资源都能结束。
- 工程与安全：用 `cargo fmt`、`cargo clippy`、性能 profile 和最小 FFI 实验验证工具链、观测和安全边界。
- 这些实验是验收路径，不把旧课程中的示例代码重新复制进题库；具体实现应留在对应项目或实践目录。
