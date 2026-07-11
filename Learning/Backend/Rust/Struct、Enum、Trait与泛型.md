# Struct、Enum、Trait 与泛型

struct 建模数据，enum 建模有限状态及其携带的数据；`Option<T>` 与 `Result<T,E>` 是 enum。优先让非法状态无法被构造，例如用 enum 而非多个互相矛盾的 bool。

trait 定义共享行为，泛型用 trait bound 限制能力。静态分发（泛型）通常零开销但会增加编译/二进制体积；`dyn Trait` 是动态分发，适合异构集合和插件边界。组合 trait 比大而全的继承层级更清晰。

`#rust #struct #enum #trait #generic`
