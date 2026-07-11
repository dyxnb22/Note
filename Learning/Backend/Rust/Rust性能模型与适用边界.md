# Rust 性能模型与适用边界

Rust 的“零成本抽象”指良好抽象不必带来运行时额外开销，不代表任何 Rust 程序自动更快。性能来自算法、I/O、内存布局、并发模型与测量。release 构建、criterion benchmark 和 flamegraph 是基本工具。

适合 Rust 的场景：高并发网络服务、系统工具、性能敏感组件、可信边界、区块链基础设施。若团队迭代速度、生态成熟度或业务复杂度更重要，Go/Java/Python 可能更合适；语言选择是约束权衡。

`#rust #performance #tradeoff`
