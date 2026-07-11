# HTTP 服务与中间件

HTTP handler 应只做解析、认证、调用服务和映射响应；业务规则放 service 层。中间件适合日志、request id、认证、恢复、限流等横切逻辑，但顺序会影响语义。

设置 server 的 read/write/idle timeout，限制请求体大小，校验输入并返回稳定错误码。不要把内部错误细节直接返回用户；日志保留 request id 和安全的上下文。优雅关闭时停止接收新连接并等待在途请求。

`#go #http #middleware #api`
