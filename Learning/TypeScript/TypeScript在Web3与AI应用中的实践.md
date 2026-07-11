# TypeScript 在 Web3 与 AI 应用中的实践

Web3 中 TypeScript 负责 ABI 类型、钱包交互、交易状态和链上读取；链上返回值、RPC 错误和用户签名都属于不可信边界。AI 应用中它常负责流式 UI、工具参数 schema、会话状态和服务端 SDK 编排。

两类场景共同原则：运行时 schema 校验、明确状态机、可取消请求、幂等写操作、敏感信息不进前端日志。TypeScript 提供协作安全网，但权限判断必须在可信服务端执行。

`#typescript #web3 #ai #practice`
