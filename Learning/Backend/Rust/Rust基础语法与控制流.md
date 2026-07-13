# Rust 基础语法与控制流

## 1. 最小程序

```rust
fn main() {
    println!("hello, Rust!");
}
```

`main` 是二进制程序入口。`println!` 后面的 `!` 表示它是宏，不是普通函数调用。

Rust 使用分号结束大多数语句，但代码块的最后一个表达式可以省略分号并作为返回值：

```rust
fn plus_one(value: i32) -> i32 {
    value + 1
}
```

## 2. 变量、可变性与常量

变量默认不可变。需要重新赋值时显式使用 `mut`：

```rust
let name = "Ada";
let mut count = 0;
count += 1;
```

`const` 必须写类型，值必须在编译期可计算；常量没有固定的运行时地址。`static` 表示整个程序生命周期内存在的全局值，使用时需要更谨慎。

变量遮蔽允许用同一个名字绑定一个新值，也可以改变类型：

```rust
let spaces = "   ";
let spaces = spaces.len();
```

遮蔽和 `mut` 不同：遮蔽产生新绑定，旧绑定不再直接可用；`mut` 修改的是同一个绑定指向的值。

## 3. 基本类型

- 整数：`i8`、`i16`、`i32`、`i64`、`i128`、`isize`，以及对应的无符号类型。
- 浮点数：`f32`、`f64`。
- 布尔：`bool`。
- 字符：`char`，表示一个 Unicode 标量值，占 4 字节，不等于一个 UTF-8 字节。
- 元组：`(T1, T2)`，长度固定，可以用 `.0`、`.1` 访问。
- 数组：`[T; N]`，长度编译期固定。
- 切片：`&[T]`、`&str`，表示连续数据的一段借用视图。

整数默认通常推断为 `i32`，但依赖上下文。不要依赖隐式数值转换：`u32` 和 `usize` 之间需要显式转换，并考虑溢出。

```rust
let bytes: usize = 4;
let limit = bytes as u64;
```

## 4. 函数与表达式

函数参数必须写类型，返回类型写在 `->` 后面。Rust 没有隐式返回；最后一个无分号表达式是返回值。

```rust
fn area(width: u32, height: u32) -> u32 {
    width * height
}

fn checked_area(width: u32, height: u32) -> Option<u32> {
    width.checked_mul(height)
}
```

`if` 是表达式，所有分支必须返回兼容类型：

```rust
let label = if count == 0 { "empty" } else { "ready" };
```

## 5. 循环

```rust
for item in items {
    println!("{item}");
}

while condition() {
    work();
}

let result = loop {
    if let Some(value) = try_read() {
        break value;
    }
};
```

`break value` 可以把循环变成表达式。循环标签用于跳出嵌套循环：

```rust
'outer: for row in rows {
    for cell in row {
        if cell == target {
            break 'outer;
        }
    }
}
```

## 6. `match` 与模式

`match` 必须覆盖所有可能情况。它不仅用于枚举，也可以匹配整数、元组、引用和结构体：

```rust
match number {
    0 => println!("zero"),
    1..=9 => println!("small"),
    n if n < 0 => println!("negative: {n}"),
    _ => println!("other"),
}
```

常见模式：

```rust
if let Some(name) = optional_name {
    println!("{name}");
}

let (left, right) = pair;
let Config { host, port, .. } = config;
```

`if let` 适合只关心一种情况；需要处理全部情况时优先使用 `match`。

## 7. 闭包与函数指针

闭包可以捕获环境，参数和返回类型常能推断：

```rust
let factor = 2;
let double = |value: i32| value * factor;
```

根据捕获方式，闭包实现 `Fn`、`FnMut` 或 `FnOnce`：

- `Fn`：可以多次调用，只读借用捕获值。
- `FnMut`：可以多次调用并修改捕获值。
- `FnOnce`：调用时消费捕获值，可能只能调用一次。

闭包不是自动异步的；`async` 闭包/代码会产生 Future，必须被执行器驱动。

## 8. 常见陷阱

- 把 `String` 当作可以按整数下标访问的字符数组；UTF-8 字符长度不固定。
- 忘记整数运算可能溢出；debug 和 release 模式的行为不同。
- 让 `match` 的 `_` 掩盖了本应显式处理的新状态。
- 过早使用 `clone` 绕过借用问题，而不先确认所有权设计。
- 把宏当成运行时反射；宏主要在编译期生成代码。

## 练习

写一个函数，接收一组整数，返回最大值、最小值和平均值；空输入返回自定义错误。要求分别用普通循环和迭代器实现，并为负数、溢出和空输入写测试。

`#rust #syntax #control-flow #pattern-matching`
