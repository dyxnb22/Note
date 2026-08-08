# Python 工程基础

这里负责 AI 应用之前的 Python 语言、工程、HTTP 和服务化能力；Agent、RAG 和工具协议回到 [Agent 知识库](../Agent/README.md)。完整跨目录路线见 [Python → AI → Agent 学习地图](../00_Navigation/AI-Python-Agent学习地图.md)。

## 问题地图

```text
01 核心语法 → 02 工程化 → 03 HTTP/API → 04 Agent 工程化
→ FastAPI/代码组织 → 05 运行时与性能 → 错误与 Debug
```

| 目标 | 入口 |
|---|---|
| Python 不熟 | [核心语法](./01_Python核心语法.md) → [工程化](./02_Python工程化.md) |
| 开始做 AI 项目 | [工程化](./02_Python工程化.md) → [HTTP/API](./03_HTTP与API调用.md) → [Agent 工程化补充](./04_Python%20Agent工程化补充.md) |
| 做 API 服务 | [FastAPI](./FastAPI.md) → [代码组织与设计模式](./Python代码组织与设计模式.md) |
| 排查线上问题 | [错误与 Debug](./错误与Debug.md) → [运行时与性能](./05_Python运行时与性能.md) |

## 怎么进入

Python 不熟时才从核心语法和基础练习开始；已经能写函数、模块、虚拟环境和基本测试时，直接从当前项目需要的工程化、HTTP/API 或 FastAPI 进入。做 Agent 不要求先读完整目录，只有遇到类型合同、异步、取消或重试问题时再看 [Agent 工程化补充](./04_Python%20Agent工程化补充.md)。运行时、性能和 Debug 始终按问题学习。

## 当前目标的完成标准

完成标准由项目决定，不要求重新做三套练习：命令行项目关注配置、错误和测试；HTTP 客户端关注超时、取消和资源关闭；API 服务再增加输入校验与端点测试。已有项目能证明对应能力时直接跳过。

## 边界与约定

`python` 代码块应通过语法解析；`text`/`pseudocode` 只是结构示意。完整可运行链路进入 [实践](./实践/Python基础练习/README.md)。语言、依赖、HTTP 和服务边界放在本目录；LLM、Agent、RAG、工具协议放在 `Agent/`。
