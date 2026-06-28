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

<table header-row="true">
<tr>
<td>错误</td>
<td>常见原因</td>
<td>排查方向</td>
</tr>
<tr>
<td>`SyntaxError`</td>
<td>语法错误、括号/引号没闭合</td>
<td>看报错行附近</td>
</tr>
<tr>
<td>`NameError`</td>
<td>变量没定义、拼写错</td>
<td>检查变量名</td>
</tr>
<tr>
<td>`TypeError`</td>
<td>类型不匹配、函数参数错误</td>
<td>打印 type、检查函数签名</td>
</tr>
<tr>
<td>`ValueError`</td>
<td>值格式不对，例如 `int("abc")`</td>
<td>检查输入值</td>
</tr>
<tr>
<td>`KeyError`</td>
<td>dict key 不存在</td>
<td>用 `.get()` 或先看 keys</td>
</tr>
<tr>
<td>`IndexError`</td>
<td>list 下标越界</td>
<td>检查 list 长度</td>
</tr>
<tr>
<td>`AttributeError`</td>
<td>对象没有这个属性或方法</td>
<td>打印对象类型</td>
</tr>
<tr>
<td>`ModuleNotFoundError`</td>
<td>包没装、环境不对</td>
<td>检查 venv / pip</td>
</tr>
<tr>
<td>`FileNotFoundError`</td>
<td>文件路径错误</td>
<td>打印当前目录和路径</td>
</tr>
</table>
