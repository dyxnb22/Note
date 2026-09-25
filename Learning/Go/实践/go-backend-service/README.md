# Go Backend Service

这是 [Go 后端面试题库：编码与系统设计](../../面试题库/04_编码题与系统设计.md) 对应的阶段 0 可运行基线：标准库 HTTP Server、Handler/Service/Repository 分层、内存幂等、请求超时、稳定错误响应、并发安全与优雅关闭。

## 运行

要求 Go 1.26 或更高版本：

```bash
go test ./...
go test -race ./...
go run ./cmd/api
```

另开终端：

```bash
curl -i -X POST http://127.0.0.1:8080/orders \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: demo-001' \
  -d '{"customer_id":"customer-1","amount_cents":1999}'

curl -i http://127.0.0.1:8080/orders/ord-1
```

使用相同 `Idempotency-Key` 和相同请求再次创建，应返回同一个订单且状态码为 `200`；第一次创建返回 `201`。同一个键携带不同客户或金额时返回 `409`，避免把不同业务请求静默合并。

## 当前边界

- Repository 只保存在内存，进程重启后数据消失。
- 请求超时只能取消遵守 Context 的调用；不能撤销已提交的外部副作用。
- Request ID 只用于响应关联，尚未接入结构化 Trace。
- 这是课程基线，不是已经完成 PostgreSQL、鉴权、指标、Outbox 和部署的生产服务。

## 后续任务

1. 按主文档阶段 1 添加可控慢 Repository，测试取消与 SIGTERM。
2. 用 PostgreSQL 和唯一约束替换内存 Repository。
3. 添加库存客户端、Outbox Publisher 和故障测试。
4. 添加结构化日志、OpenTelemetry、负载测试和 pprof 报告。

完成每一阶段后保留命令、环境、原始输出和失败记录，不把“写了代码”直接标记为“生产可用”。
