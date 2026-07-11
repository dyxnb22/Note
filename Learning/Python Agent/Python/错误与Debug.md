# 错误与Debug
Debug 的核心不是背错误，而是建立排查顺序：先看错误类型，再看堆栈，再定位环境、输入、依赖、网络、配置或代码逻辑。

## 1. Debug 基本流程

```plain text
复现问题
→ 读完整报错
→ 找第一段自己代码位置
→ 看输入和配置
→ 缩小范围
→ 加日志或断点
→ 修复
→ 写测试或记录原因
```

不要只看最后一行，也不要看到红字就重装环境。

## 2. Python 常见错误

| 错误 | 常见原因 | 排查方向 |
| --- | --- | --- |
| `SyntaxError` | 语法错误、括号/引号没闭合 | 看报错行附近 |
| `NameError` | 变量没定义、拼写错 | 检查变量名 |
| `TypeError` | 类型不匹配、函数参数错误 | 打印 type、检查函数签名 |
| `ValueError` | 值格式不对，例如 `int("abc")` | 检查输入值 |
| `KeyError` | dict key 不存在 | 用 `.get()` 或先看 keys |
| `IndexError` | list 下标越界 | 检查 list 长度 |
| `AttributeError` | 对象没有这个属性或方法 | 打印对象类型 |
| `ModuleNotFoundError` | 包没装、环境不对 | 检查 venv / pip |
| `FileNotFoundError` | 文件路径错误 | 打印当前目录和路径 |
