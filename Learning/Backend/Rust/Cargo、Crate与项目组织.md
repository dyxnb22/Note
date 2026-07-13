# Cargo、Crate 与项目组织

## 1. 基本概念

- **Cargo**：构建、依赖、测试、文档和发布工具。
- **package**：一个 `Cargo.toml`，可以包含一个 library crate、一个 binary crate 或多个 binary crate。
- **crate**：编译单元。`src/lib.rs` 是 library crate，`src/main.rs` 是默认 binary crate。
- **workspace**：多个 package 的共同构建和依赖管理边界。

典型项目：

```text
my-app/
  Cargo.toml
  Cargo.lock
  src/
    main.rs
```

library + binary 项目：

```text
my-app/
  Cargo.toml
  src/
    lib.rs
    main.rs
```

把核心逻辑放在 `lib.rs`，`main.rs` 只负责读取配置、启动和退出码，通常更容易测试和复用。

## 2. `Cargo.toml`

```toml
[package]
name = "my-app"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { version = "1", features = ["derive"] }

[dev-dependencies]
assert_cmd = "2"
```

- `[dependencies]`：编译和运行需要的依赖。
- `[dev-dependencies]`：测试、示例或 benchmark 使用的依赖。
- `[build-dependencies]`：构建脚本使用的依赖。
- `features`：可选编译能力，不等于运行时配置。

版本号遵循 Cargo 的语义版本兼容规则。应用应提交 `Cargo.lock`，库通常也可以提交它以保持 CI 和本地测试一致。

## 3. 常用命令

```bash
cargo new app
cargo new --lib library
cargo init
cargo check
cargo build
cargo build --release
cargo run -- arg1
cargo test
cargo test module::test_name
cargo fmt --all
cargo clippy --all-targets --all-features -- -D warnings
cargo doc --open
cargo tree
cargo metadata --format-version 1
```

`cargo check` 通常比完整编译快，适合频繁反馈；`cargo build --release` 使用优化配置，不能用来替代测试。

## 4. workspace

```toml
[workspace]
resolver = "2"
members = ["crates/app", "crates/domain"]

[workspace.package]
edition = "2021"
```

workspace 统一锁文件、目标目录和常用元数据，但 package 仍有自己的 `Cargo.toml`。workspace 不等于微服务，也不意味着运行时一定有多个进程。

## 5. 依赖管理

引入依赖前先问：标准库是否足够；依赖是否维护；是否增加编译时间；是否改变安全边界；是否需要锁定 feature；是否有许可证约束。

使用依赖时优先限定 feature：

```toml
tokio = { version = "1", default-features = false, features = ["rt-multi-thread", "macros", "time"] }
```

不要为了一个小函数引入庞大框架。定期用 `cargo tree -i package-name` 查反向依赖，用 `cargo audit` 等工具检查已知漏洞。

## 6. profile 与构建产物

```toml
[profile.release]
lto = "thin"
codegen-units = 1
strip = "symbols"
```

优化设置应通过基准测试决定。`target/` 是构建产物，不应提交；`Cargo.lock` 是否提交取决于 package 类型和团队发布策略，但应用通常应提交。

## 7. 代码质量工具

- `rustfmt`：统一格式，不负责判断设计是否正确。
- `clippy`：提供常见错误和可读性建议；不要机械地关闭所有 lint。
- `cargo test`：执行单元、集成、文档测试。
- `cargo doc`：检查公开 API 是否有清晰文档。

格式化和 lint 应在提交或 CI 中固定执行，避免依赖个人编辑器设置。

## 8. 组织原则

按领域或职责拆分模块，而不是按文件大小拆分。优先让数据和不变量靠近其操作；公开 API 小而稳定；适配外部库的代码集中在边界；不要过早创建名为 `utils` 的杂物模块。

## 练习

创建一个 workspace，包含一个 library 和一个 binary。binary 调用 library 的公开函数；为 library 写单元、集成和文档测试；配置 clippy 为 warning 当作 error，并解释哪些依赖属于普通、开发和可选依赖。

`#rust #cargo #crate #workspace #project-structure`
