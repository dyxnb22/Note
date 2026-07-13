# Struct、Enum、Trait 与泛型

## 1. `struct`

`struct` 用于把相关数据组合成有名字的类型：

```rust
#[derive(Debug, Clone, PartialEq)]
pub struct User {
    pub id: u64,
    pub name: String,
    active: bool,
}
```

字段可以有不同可见性。通过私有字段和构造函数维护不变量：

```rust
impl User {
    pub fn new(id: u64, name: String) -> Result<Self, UserError> {
        if name.trim().is_empty() {
            return Err(UserError::EmptyName);
        }
        Ok(Self { id, name, active: true })
    }
}
```

## 2. `enum`

`enum` 表示有限的几种可能，每个变体可以携带不同数据：

```rust
enum Message {
    Quit,
    Text(String),
    Move { x: i32, y: i32 },
}
```

它比多个互相矛盾的 `bool` 更适合表达状态。配合穷尽 `match`，新增变体会让编译器指出所有需要更新的分支。

```rust
fn describe(message: Message) -> String {
    match message {
        Message::Quit => "quit".into(),
        Message::Text(text) => format!("text: {text}"),
        Message::Move { x, y } => format!("move: {x},{y}"),
    }
}
```

## 3. `impl` 与方法

```rust
impl User {
    pub fn is_active(&self) -> bool { self.active }

    pub fn deactivate(&mut self) {
        self.active = false;
    }
}
```

- `&self`：只读借用。
- `&mut self`：可变借用。
- `self`：消费对象所有权。

没有 `self` 的关联函数类似构造函数，通过 `User::new` 调用。

## 4. trait

trait 描述一组行为，不等于继承：

```rust
trait Summary {
    fn summary(&self) -> String;

    fn short_summary(&self) -> String {
        self.summary().chars().take(20).collect()
    }
}
```

可以为不同类型实现同一个 trait，也可以给 trait 提供默认方法。孤儿规则限制了实现：要么 trait 属于当前 crate，要么被实现的类型属于当前 crate。

## 5. 泛型与 trait bound

```rust
fn largest<T: PartialOrd>(items: &[T]) -> Option<&T> {
    items.iter().max_by(|left, right| left.partial_cmp(right).unwrap())
}
```

更复杂的约束使用 `where`：

```rust
fn render<T>(value: &T) -> String
where
    T: std::fmt::Display,
{
    value.to_string()
}
```

泛型通常采用静态分发，编译器为具体类型生成专门代码；好处是性能和类型检查，代价是编译时间和代码体积可能增加。

## 6. `impl Trait` 与 `dyn Trait`

```rust
fn make_iterator() -> impl Iterator<Item = i32> {
    0..3
}

fn print_all(items: &[Box<dyn Summary>]) {
    for item in items {
        println!("{}", item.summary());
    }
}
```

`impl Trait` 隐藏一个确定的具体类型，通常静态分发；`dyn Trait` 使用 trait object，允许运行时保存不同具体类型，通常需要堆分配和动态分发。

选择原则：类型集合固定且性能敏感时用泛型或 enum；需要异构集合、运行时替换或稳定边界时考虑 `dyn Trait`。

## 7. 关联类型与泛型参数

```rust
trait IteratorLike {
    type Item;
    fn next(&mut self) -> Option<Self::Item>;
}
```

关联类型表示一个实现只有一种主要输出类型；泛型参数允许同一个类型针对多个类型参数实现 trait。选择哪一种取决于 API 是否允许同一实现存在多个版本。

## 8. Derive 与常见 trait

- `Debug`：调试输出。
- `Clone`：显式复制。
- `Copy`：隐式复制，要求字段都可 Copy。
- `PartialEq`/`Eq`：比较相等。
- `PartialOrd`/`Ord`：排序。
- `Default`：默认值。
- `Hash`：哈希集合或 map 的键。
- `Serialize`/`Deserialize`：通常由 Serde 派生。

不要为了方便给拥有大量资源或敏感数据的类型随意派生 `Clone`、`Debug` 或 `Serialize`。

## 练习

设计一个 `Repository<T>`，用 trait 表示存储行为；实现内存版和文件版。先用泛型写静态版本，再用 `Box<dyn Storage>` 支持运行时替换，比较两种 API 的差异。

`#rust #struct #enum #trait #generic #type-design`
