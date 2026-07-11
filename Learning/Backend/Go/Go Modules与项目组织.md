# Go Modules 与项目组织

`go.mod` 定义模块路径和依赖版本；使用 `go mod tidy` 保持依赖干净。不要随意在业务代码中暴露第三方库类型，否则升级会扩散。

典型项目可按 `cmd/`（可执行入口）、`internal/`（私有实现）、`pkg/`（确有外部复用价值的库）组织。依赖方向应从 transport → service → repository，领域逻辑不依赖 HTTP 或数据库具体实现。

`#go #modules #project-structure`
