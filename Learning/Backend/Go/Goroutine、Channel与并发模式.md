# Goroutine、Channel 与并发模式

goroutine 很轻量，但不是免费；每个都需要生命周期和退出路径。channel 用于传递所有权/协调，mutex 用于保护共享状态；不要把 channel 当成任何问题的默认答案。

常见模式是 worker pool、fan-out/fan-in、pipeline。所有发送/接收都要考虑阻塞、关闭责任和取消：通常由发送方关闭 channel，接收方用 `ok` 判断结束。用 `go test -race` 检查数据竞争。

`#go #goroutine #channel #concurrency`
