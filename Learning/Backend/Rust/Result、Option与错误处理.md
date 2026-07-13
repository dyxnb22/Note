# Result、Option 与错误处理

## 1. 两种核心枚举

```rust
enum Option<T> {
    Some(T),
    None,
}

enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

`Option` 表示值可能不存在；`Result` 表示操作可能失败。它们把异常情况放进类型签名，调用者必须选择处理、传播或转换方式。

## 2. 匹配与组合

```rust
match config.get("port") {
    Some(value) => println!("port={value}"),
    None => println!("using default"),
}
```

常用方法：

- `Option::map`：有值时转换。
- `and_then`：串联可能失败的转换。
- `unwrap_or`、`unwrap_or_else`：提供默认值。
- `ok_or`：把 `Option` 转成 `Result`。
- `Result::map_err`：转换错误类型。
- `Result::and_then`：串联可能失败的操作。
- `is_ok`、`is_err`、`is_some`：只检查状态。

不要用 `is_some()` 后再 `unwrap()`，如果要取值通常使用 `if let` 或 `match`。

## 3. `?` 运算符

`?` 在成功时取出值，在失败时提前返回错误：

```rust
fn read_port(text: &str) -> Result<u16, ParseIntError> {
    let port = text.parse::<u16>()?;
    Ok(port)
}
```

它要求当前函数的错误类型可以接收被传播的错误，通常通过 `From` 或 `thiserror` 的 `#[from]` 实现转换。

`?` 不是忽略错误；它是明确地把错误交给上层。边界函数要在合适的位置添加上下文，并决定如何展示给用户。

## 4. 自定义错误

库代码应定义可匹配的错误类型：

```rust
#[derive(Debug)]
pub enum ConfigError {
    MissingField(&'static str),
    InvalidPort(u16),
    Io(std::io::Error),
}

impl From<std::io::Error> for ConfigError {
    fn from(error: std::io::Error) -> Self {
        Self::Io(error)
    }
}
```

生产项目中常用 `thiserror` 派生库错误，应用入口常用 `anyhow` 携带上下文。关键边界仍应保留稳定、可测试的错误分类，而不是把所有错误都变成字符串。

错误类型应回答：发生了什么类别的错误；调用者能否恢复；是否需要重试；哪些细节应该记录但不展示。

## 5. `panic!`、`unwrap` 与 `expect`

`panic!` 表示程序遇到了不应继续的状态，不是普通业务错误。`unwrap`/`expect` 在 `None` 或 `Err` 时 panic。

可以接受的场景：

- 测试中验证“不应失败”的前置条件。
- 程序启动时读取编译期保证存在的资源。
- 明确证明某个分支不可能到达，并在代码中留下理由。

不适合的场景：网络、文件、用户输入、配置、数据库、模型响应等外部边界。

## 6. 错误层次与上下文

在底层保留根因，在边界添加语义上下文：

```rust
fn load_config(path: &Path) -> anyhow::Result<Config> {
    let text = std::fs::read_to_string(path)
        .with_context(|| format!("read config {}", path.display()))?;
    let config = toml::from_str(&text)
        .with_context(|| format!("parse config {}", path.display()))?;
    Ok(config)
}
```

用户看到的错误要稳定、可行动且不泄露秘密；日志或诊断链可以包含文件路径、请求 ID 和根因，但也要脱敏。

## 7. 重试与错误分类

不是所有错误都应该重试：

- 可重试：暂时网络错误、限流、服务暂时不可用。
- 不应重试：格式错误、权限拒绝、参数错误、资源不存在。
- 需要策略：超时、连接断开、事务提交未知状态。

重试必须有上限、退避、取消能力，并考虑操作是否幂等。把 `Result` 处理成无限重试是常见故障来源。

## 8. 练习

实现配置加载函数：区分文件不存在、权限错误、格式错误和字段非法；为每种错误写测试；给命令行用户提供简洁信息，同时保留可调试的根因链。

`#rust #result #option #error-handling #panic`
