# 文件系统、进程与网络 I/O

## 1. 路径

`Path`/`PathBuf` 处理路径，类似 `str`/`String` 的借用与拥有关系：

```rust
use std::path::{Path, PathBuf};

fn config_path(root: &Path) -> PathBuf {
    root.join("config.toml")
}
```

不要用字符串拼接路径；不同平台的分隔符、盘符和绝对路径规则不同。`Path::join` 也不会自动证明结果位于某个根目录内，边界程序仍需做路径策略检查。

## 2. 文件读取与写入

```rust
let text = std::fs::read_to_string("notes.txt")?;
std::fs::write("output.txt", text.as_bytes())?;
```

大文件使用 `File` + `BufReader`/`BufWriter`，避免一次性读入全部内容：

```rust
use std::io::{BufRead, BufReader};
use std::fs::File;

let file = File::open(path)?;
for line in BufReader::new(file).lines() {
    let line = line?;
    process(line);
}
```

写入时要考虑临时文件、权限、磁盘满、部分写入、flush 和原子替换。`write` 成功不一定代表数据已经持久化到物理介质；需要耐久性时研究 `sync_all` 和平台语义。

## 3. 文件类型和链接

`metadata`、`symlink_metadata`、`canonicalize` 各有不同跟随链接的行为。符号链接、硬链接、junction、设备文件和 FIFO 的语义不能混为一谈。

检查后再打开文件之间可能存在 TOCTOU（检查与使用之间状态改变）窗口。对安全边界要求高的代码，应使用平台提供的目录相对打开、no-follow 或句柄相对 API，并在执行时复验；单纯字符串规范化不是完整防护。

## 4. 权限与平台差异

Unix 权限、Windows ACL、macOS 沙盒和文件标志不同。不要假设所有平台都支持相同的权限、锁和原子替换语义。跨平台代码应列出支持矩阵，对无法满足要求的平台显式报错。

## 5. 进程

```rust
use std::process::Command;

let output = Command::new("git")
    .args(["status", "--short"])
    .current_dir(repo)
    .env_clear()
    .output()?;
```

`Command::new` + `args` 传递的是程序和 argv，不等于 shell 字符串。不要把不可信输入拼接成 `sh -c`/`cmd /C`。固定程序、完整参数、工作目录、环境、stdin/stdout/stderr 和退出码。

`output()` 会等待并收集全部输出；可能需要 `spawn()`、流式读取、输出上限和超时。子进程终止、孤儿进程、子进程树、信号和 Windows job object 都是平台相关问题。

## 6. 网络基础

阻塞 TCP 的最小形态：

```rust
use std::net::TcpListener;

let listener = TcpListener::bind("127.0.0.1:8080")?;
for stream in listener.incoming() {
    let stream = stream?;
    handle(stream)?;
}
```

真实服务需要处理连接生命周期、半关闭、读写超时、消息边界、缓冲、背压、TLS、认证和优雅关闭。TCP 是字节流，不保留应用层消息边界。

## 7. I/O 错误与资源生命周期

文件、socket、子进程和锁都应使用 RAII，在离开作用域时释放。错误传播不能遗忘清理；复杂资源要明确“创建成功但后续步骤失败”时的状态。

对每个外部 I/O 定义：超时、最大输入/输出、取消行为、重试规则、日志脱敏和连接关闭方式。

## 8. 同步还是异步

- 简单 CLI、少量文件和短任务：同步标准库通常更清晰。
- 大量并发连接或同时等待多个外部服务：异步 runtime 更合适。
- CPU 密集任务：线程池或进程，不是单纯加 `async`。

异步库和同步库不要在同一调用链里随意混用；必要时用明确的 blocking 边界。

## 练习

写一个文件统计 CLI：按流式方式读取文件，输出行数和字节数；再增加一个固定 argv 的子进程调用；为不存在文件、非 UTF-8、超时和超大输出定义错误。

`#rust #filesystem #process #tcp #io #platform`
