# Cargo、Crate 与项目组织

Cargo 管理构建、依赖、测试和格式化。`Cargo.toml` 中区分普通、开发和可选依赖；提交 `Cargo.lock` 的应用可获得可重复构建。使用 `cargo fmt`、`cargo clippy`、`cargo test` 作为 CI 基础。

crate 的公开 API 应谨慎，默认私有；模块按领域或能力划分，不按文件大小。库层不依赖 HTTP 框架，二进制入口负责配置、日志和依赖装配。

`#rust #cargo #crate #project-structure`
