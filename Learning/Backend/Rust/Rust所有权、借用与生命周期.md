# Rust 所有权、借用与生命周期

## 1. 所有权规则

Rust 的每个值都有一个所有者。所有者离开作用域时，值被自动释放。核心规则：

1. 每个值只有一个所有者。
2. 同一时间可以有多个不可变借用，或一个可变借用。
3. 引用必须始终指向有效的值。

```rust
let first = String::from("hello");
let second = first; // String 的所有权移动到 second
// first 不能再使用
```

移动避免了两个变量在作用域结束时重复释放同一块堆内存。

实现 `Copy` 的简单类型会复制而不是移动，例如整数、布尔、字符和只包含 `Copy` 字段的元组：

```rust
let a = 1;
let b = a;
println!("{a} {b}");
```

## 2. 函数传参与返回

传参默认遵守移动或复制规则：

```rust
fn consume(text: String) {}
fn borrow(text: &str) {}

let owned = String::from("data");
borrow(&owned);
consume(owned);
```

如果函数需要把值交还，可以返回它，但多数只读操作更适合借用。返回新创建的拥有值是安全的；不能返回指向函数局部变量的引用。

## 3. 借用

```rust
fn append_suffix(text: &mut String) {
    text.push_str("!");
}

let mut value = String::from("hi");
let view = &value;
println!("{view}");
append_suffix(&mut value); // 不可变借用结束后才可变借用
```

借用规则是编译期约束，不是运行时锁。它保护的是别名与可变性的组合，但不自动保证业务逻辑正确。

## 4. 借用检查器的解决顺序

遇到 borrow checker 错误时，按这个顺序排查：

1. 减少借用范围，把表达式拆成多个步骤。
2. 让读取阶段和修改阶段分开。
3. 改变函数签名，明确谁拥有值。
4. 必要时复制小而廉价的数据。
5. 只有共享所有权确有业务含义时才引入智能指针。

不要把 `clone()` 当作默认修复；先判断复制是否改变了数据一致性和成本。

## 5. 生命周期

生命周期描述引用必须持续有效的范围，不会延长值本身的生命周期。

```rust
fn longer<'a>(left: &'a str, right: &'a str) -> &'a str {
    if left.len() >= right.len() { left } else { right }
}
```

`'a` 表示返回引用的有效期不能超过两个输入引用中较短的那个。它不是线程、内存或垃圾回收机制。

大多数函数不需要手写生命周期，因为编译器能通过省略规则推断。常见需要显式标注的情况：多个输入引用且返回引用依赖它们、结构体持有引用、实现 trait 的引用关系不明显。

## 6. 结构体持有引用

```rust
struct Parser<'a> {
    input: &'a str,
}
```

这表示 `Parser` 不能活得比 `input` 更久。很多业务类型更适合拥有 `String` 或 `PathBuf`，用所有权换取更简单的生命周期和独立存活能力。

## 7. 部分移动与模式匹配

从结构体中移动一个非 `Copy` 字段后，整个结构体不能再作为整体使用，但仍可能使用没有被移动的字段。借用模式可以避免移动：

```rust
let name = String::from("Ada");
let record = (name, 42);
let (ref name_ref, age) = record;
println!("{name_ref} {age}");
```

现代代码也常用 `match &value` 或 `match value.as_ref()` 明确只借用匹配内容。

## 8. `'static` 的含义

`'static` 表示引用在整个程序生命周期内有效，字符串字面量就是典型例子。拥有的数据也可以被转成 `'static`，但这通常意味着数据被泄漏或被任务永久持有，不应为了消除编译错误随意使用。

## 9. 常见误区

- 生命周期不是手动释放时间，也不是“把变量活得更久”。
- `&mut T` 不代表线程安全；跨线程还要满足 `Send`/`Sync`。
- `Rc`/`Arc` 解决的是所有权共享，不会自动解决内部可变性。
- `clone` 可以解决类型问题，却可能掩盖错误的所有权设计。

## 练习

分别实现三个函数：返回字符串中最长的切片、原地删除空白字符、把一个 `Vec<String>` 消费成长度统计。写出每个函数的所有权选择，并解释为什么不能返回局部 `String` 的引用。

`#rust #ownership #borrowing #lifetime`
