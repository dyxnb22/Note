# Go 语言基础与工程习惯

Go 用 package 组织代码，编译快、标准库强、语法刻意克制。优先写清晰小函数和零值可用的 struct；用 `gofmt`、`go vet`、`go test` 作为日常最低检查。

理解 slice（数组片段，含指针/长度/容量）、map（引用语义，非并发安全）、struct（值语义）和 pointer。slice append 可能扩容并返回新底层数组，因此函数需要返回更新后的 slice。接口由使用方定义，小接口更易测试。

`#go #basics #engineering`
