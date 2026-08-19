# Python

本目录现在保留 Python 的面试入口和实践入口。语言、工程、HTTP、FastAPI、运行时、Debug 与代码组织等知识已经合并进 [Python 面试题库](./面试题库/README.md)。

## 进入方式

- 面试与系统化复习：先读 [Python 面试题库](./面试题库/README.md)。
- 可运行练习：进入 [Python 基础练习](./实践/Python基础练习/README.md)。
- Agent、RAG 和工具协议：进入 [Agent 面试题库](../Agent面试题库/README.md)。

## Python 题库覆盖

- 语言与运行时：对象、容器、函数、异常、迭代器、GIL、GC、asyncio 和性能。
- 工程与 Web：依赖、配置、`pyproject.toml`、类型标注与 `mypy`、HTTP、FastAPI、数据库、缓存、任务、测试和观测。
- 编码与项目：算法、并发、限流、调试、系统设计和项目深挖。

实践目录下的练习和 Notebook 保持独立，不作为题库页面处理。

## 实践验收

- 在 [Python 基础练习](./实践/Python基础练习/README.md) 和 Notebook 中验证语法、对象、容器和控制流。
- 在题库工程题中用干净虚拟环境执行格式、lint、`python -m mypy src`（适用时）和测试；命令与 Python/依赖版本应写入项目合同。
- FastAPI、异步任务和外部模型调用要用测试服务器、Fake/Mock 和可控事件验证超时、取消、重试、重复副作用和资源释放。
