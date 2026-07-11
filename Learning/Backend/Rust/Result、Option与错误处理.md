# Result、Option 与错误处理

`Option` 表示可能不存在，`Result` 表示可能失败。应用边界可用 `?` 向上传播并加上下文；库代码应定义可匹配的错误类型。`unwrap/expect` 仅用于已证明不可能失败的场景或测试，不能代替错误处理。

错误分为可预期业务错误和异常基础设施错误。面向用户的错误信息要稳定且不泄漏内部细节；日志记录根因链和 request context。`thiserror` 适合库错误，`anyhow` 常适合应用入口的上下文传播。

`#rust #result #option #error-handling`
