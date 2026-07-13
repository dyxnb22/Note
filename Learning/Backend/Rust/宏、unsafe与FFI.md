# 宏、unsafe 与 FFI

## 1. 宏的类别

- 声明宏 `macro_rules!`：按 token pattern 匹配并展开代码。
- 派生宏：为 struct/enum 生成 trait 实现。
- 属性宏：修改或生成带属性的项。
- 函数式过程宏：接收 token stream，生成 token stream。

宏在编译期操作语法，不是运行时反射。复杂宏会增加编译时间、错误定位难度和 API 隐式行为。

## 2. 声明宏示例

```rust
macro_rules! max_value {
    ($left:expr, $right:expr) => {{
        let left = $left;
        let right = $right;
        if left > right { left } else { right }
    }};
}
```

宏展开时要注意表达式求值次数、变量捕获、类型推断和卫生性。能用普通函数、trait 或泛型解决时，优先选择它们。

## 3. `unsafe`

`unsafe` 不会关闭所有 Rust 检查，只允许执行几类额外操作，例如解引用裸指针、调用 unsafe 函数、访问可变静态变量和实现 unsafe trait。调用者必须证明不变量。

```rust
// SAFETY: ptr 指向一个仍然有效、对齐且初始化的 i32。
unsafe {
    let value = *ptr;
}
```

安全封装的原则：

1. 尽量把 unsafe 代码缩到最小模块。
2. 在附近写出可验证的 SAFETY 注释。
3. 对边界、别名、生命周期、对齐、初始化和线程安全做测试。
4. 不让调用者为了使用安全 API 被迫理解内部 unsafe 细节。

`unsafe` 不是性能开关，也不是绕过 borrow checker 的常规办法。

## 4. FFI

FFI 连接 Rust 与 C 等语言。跨边界时要处理：

- ABI 和类型布局。
- 谁分配、谁释放内存。
- 字符串编码和 NUL 终止。
- 空指针、长度和错误码。
- 线程、回调和异常边界。
- 库版本和链接方式。

```rust
use std::ffi::CString;

let input = CString::new("hello")?;
// 传给 C API 前保证没有内部 NUL。
```

不要跨 FFI 边界传递 Rust 的 `String`、`Vec` 或 trait object，除非双方明确约定布局和所有权协议。

## 5. 宏和 unsafe 的评估

引入宏或 unsafe 前，记录：为什么安全 Rust 不足；边界不变量是什么；如何测试；如何在升级编译器或依赖后验证；失败时如何诊断。

## 练习

写一个 `macro_rules!` 生成简单日志调用，再把它改写为普通函数；比较 API、错误信息和求值行为。阅读一个标准库 unsafe 封装，尝试复述它维护的不变量。

`#rust #macros #unsafe #ffi #abi`
