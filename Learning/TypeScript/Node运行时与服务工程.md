# Node.js 运行时与服务工程

本篇连接 TypeScript 类型系统与 Node.js 真实运行时。类型只在编译阶段提供约束；事件循环、模块加载、资源释放和网络失败决定服务在生产中的行为。

## 1. Node.js 运行模型

Node.js 的 JavaScript 默认运行在单个主线程上，异步 I/O 由事件循环和底层系统能力协调；部分文件、DNS、压缩和加密任务可能使用线程池。

“单线程”不等于一次只能处理一个连接，也不等于不会出现竞态：

- 多个异步任务可能交错修改共享状态。
- CPU 密集任务会阻塞事件循环。
- 多进程、Worker Thread 和外部服务会引入真正并行。

## 2. 事件循环

需要理解：

- Call Stack。
- Timer、I/O、Poll、Check 等阶段的作用边界。
- Promise/Microtask 与普通任务的调度差异。
- `process.nextTick` 过度使用可能饿死 I/O。

不要依赖细微执行顺序写业务逻辑；需要顺序时使用显式 `await`、队列、锁或状态机表达。

## 3. CPU 密集任务

大 JSON 处理、压缩、图像、加密或复杂循环可能阻塞事件循环，导致所有请求尾延迟上升。

处理方式：

- 分块并让出事件循环。
- 使用 Worker Thread。
- 使用子进程或任务队列。
- 下沉到原生库或专门计算服务。

优化前应测量 Event Loop Lag、CPU Profile 和实际调用栈。

## 4. Stream 与背压

Stream 允许分块处理大文件和网络数据，避免一次加载到内存。

- Readable：数据来源。
- Writable：数据目的地。
- Duplex：可读可写。
- Transform：读入后转换再输出。

当 `write()` 返回 `false` 时，应等待 `drain` 再继续。优先使用 `pipeline` 统一传播错误和关闭资源。忽视背压会造成内存持续增长。

## 5. Buffer、文本与二进制

Buffer 表示字节序列；字符串需要明确字符编码。工程中注意：

- UTF-8 字符可能跨多个字节块。
- Base64 是编码，不是加密。
- 比较签名等安全数据应使用恒定时间比较接口。
- 大 Buffer、切片和引用可能延长底层内存生命周期。

## 6. 模块系统

Node.js 同时存在 ESM 和 CommonJS：

- ESM 使用 `import/export`。
- CommonJS 使用 `require/module.exports`。
- `package.json` 的 `type`、文件扩展名和构建输出共同决定解释方式。

库发布时要明确 exports、types、Node 版本和是否同时提供 ESM/CJS。避免生成两个模块实例导致单例、类身份或全局状态不一致。

## 7. 包管理与供应链

npm、pnpm、yarn 都解决依赖安装和脚本执行，但锁文件语义和目录结构不同。

原则：

- 提交锁文件。
- CI 使用冻结锁文件安装。
- 区分 dependencies、devDependencies 和 peerDependencies。
- 不盲目执行来源不明的安装脚本。
- 做依赖、许可证、Secret 和制品扫描。
- 发布包前检查实际包含文件。

## 8. 配置与启动

配置在启动时完成解析和校验，缺失关键配置应快速失败。不要让业务代码到处读取 `process.env`。

启动顺序建议：

```text
加载配置 → 校验 → 初始化日志/Trace
→ 建立依赖客户端 → 注册路由 → 开始监听
```

退出时停止接收新请求，等待在途请求和任务，在期限内关闭数据库、HTTP Client 和遥测 Exporter。

## 9. HTTP 服务

无论使用原生 HTTP、Fastify、Express 还是其他框架，都应统一处理：

- 请求大小、解析和 Schema 校验。
- 认证、授权和租户。
- Timeout、AbortSignal 和取消传播。
- 稳定错误映射。
- Request ID、Trace 和结构化日志。
- 限流、幂等和重复提交。
- 健康检查与优雅退出。

不要把未处理 Promise Rejection 或异常继续留在未知状态的进程中；记录必要证据并按恢复策略退出或隔离请求。

## 10. 数据库与并发

连接池大小要结合数据库容量、服务副本和事务时间计算。每个请求持有连接过久会造成池排队。

事务回调中避免长时间网络调用。并发更新使用数据库约束、条件更新或版本号守住不变量，不能依赖单线程直觉。

## 11. 测试

测试层次：

- 纯函数和领域规则：单元测试。
- Schema、数据库、缓存和 HTTP Client：集成测试。
- API 合同：契约测试。
- 核心用户路径：少量端到端测试。
- Stream、取消和优雅退出：故障测试。

测试应检查未关闭 Handle、定时器和连接，避免测试进程因为资源泄漏无法退出。

## 12. 构建与发布

明确源码、类型声明、Source Map 和运行产物的边界：

- `tsc --noEmit` 用于类型检查。
- Bundler 适合应用或需要打包的场景，不一定适合所有 Node 服务。
- Source Map 需要与制品版本对应，并控制源码暴露权限。
- 容器中只放运行所需文件和生产依赖。
- 产物应携带版本和提交标识。

## 13. 可观测性与性能

至少观察：

- Event Loop Lag。
- 请求速率、错误和延迟分位数。
- Heap、RSS、GC 和对象分配。
- 活跃 Handle、连接池和队列。
- 下游调用与 Trace。

使用 CPU/Heap Profile 定位问题，不能根据“Node 单线程”直接得出扩容结论。

## 最小项目

实现一个 TypeScript API：

1. 使用 Schema 校验输入和配置。
2. 为所有下游调用设置 Timeout/AbortSignal。
3. 使用 Stream 上传或下载大文件并验证背压。
4. 接入数据库连接池、结构化日志和 Trace。
5. 实现 SIGTERM 优雅退出。
6. 做负载测试，观察 Event Loop Lag、p99 和内存。

## 验收清单

- 能解释事件循环、Microtask 和线程池的边界。
- CPU 密集任务不会阻塞所有请求。
- Stream 正确处理背压、错误和资源关闭。
- ESM/CJS、锁文件和发布产物边界清晰。
- Timeout、取消、连接池和优雅退出有测试。
- 类型检查、运行时校验和可观测性形成闭环。

## 来源与验证边界

运行时语义参考 Node.js、libuv 和 TypeScript 官方文档。事件循环阶段、模块兼容和工具链行为可能随版本变化，运行前应核对项目锁定的 Node/TypeScript 版本并用最小实验验证。

## 导航与关联

- [模块入口：TypeScript](./README.md)
- 同一路线：[TypeScript 工程基础](./TypeScript工程基础.md) · [前端应用工程](./前端应用工程.md)

`#typescript #nodejs #event-loop #stream #backend`
