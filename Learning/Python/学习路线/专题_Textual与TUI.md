# 专题:Textual 与 TUI

> Textual 是 Python 生态中现代 TUI 框架的代表,基于 Rich 构建,采用异步消息驱动架构。本专题覆盖其核心设计模式、事件系统、响应式数据绑定、Worker 与测试策略。通用的有界事件队列、Presenter/Reducer 分层原则也适用于其他终端 UI。

## 核心架构与 MessagePump

- Textual 采用异步消息驱动架构,所有组件(App、Screen、Widget)都继承自 `MessagePump`。
- MessagePump 维护一个异步消息队列,事件和消息通过 `post_message()` 入队,由 asyncio Task 按序处理。这保证了:消息处理的顺序性、UI 不会被长时间阻塞、组件间通过消息通信而非直接调用。
- 核心类层次:`MessagePump → DOMNode → Widget → Screen → App`。
- 为什么需要 Presenter/Reducer 层:Presenter 把事件转换为纯状态,UI 框架只负责采集输入和渲染。这样业务权限不进入 UI,状态转换可以脱离终端测试,实时运行和历史回放也能使用同一个投影逻辑。

## Widget 生命周期

- `__init__()` 实例化对象,设置 ID、classes。
- `compose()` 返回子 Widget 列表,声明式定义组件树。
- `Mount` 事件:Widget 被挂载到 DOM,`_is_mounted = True`。
- 运行阶段:处理事件、更新渲染。
- `Unmount` 事件:从 DOM 移除,清理定时器和 Worker。
- `compose()` 是声明式 API,`mount()` 是命令式 API,两者可配合使用。

## 事件系统

- 事件默认冒泡到父组件:子组件处理完后,若消息 `bubble=True`,自动传给父组件的消息队列。
- 停止冒泡:在处理器中调用 `message.stop()`。例如 `Input` 组件处理按键后停止冒泡,避免父组件重复处理。
- `prevent_default()` 阻止后续基类处理器调用,但不影响冒泡。
- `@on(MessageType, selector)` 是消息处理器装饰器:`selector` 是 CSS 选择器,过滤只处理匹配的 Widget(如 `@on(Button.Pressed, ".confirm")` 只处理 class 为 confirm 的按钮)。相比命名约定 `on_button_pressed`,装饰器语法更灵活,支持选择器过滤和多消息处理。
- 有界事件队列中的事件要分类:增量文本、进度等瞬态信息在过载时可以合并或丢弃;状态转移、审批、错误和完成事件属于权威信息,必须背压、持久化或保证可恢复。队列大小、关闭、取消和消费者变慢时的策略都应明确。

## 响应式数据绑定

- `reactive` 属性赋值时自动触发 `refresh()` 更新 UI。
- 赋值链路:先调用 `validate_*` 校验,再调用 `watch_*` 响应变化(接收 old/new 值)。
- `compute_*` 计算派生值。
- `var` 是简化版 reactive,不触发 UI 刷新。
- `data_bind()` 可将父子 Widget 的 reactive 属性绑定,实现数据同步。

## CSS 系统(TCSS)

- 语法类似 Web CSS,但针对终端优化:支持 `grid`、`horizontal`、`vertical` 等终端布局。
- `scrollbar-gutter`、`text-opacity` 等属性是终端特有。
- 特异性计算包含 `is_user_css` 和 `!important` 标志。
- 样式通过描述符(Descriptor)系统应用,赋值时自动触发验证和刷新。
- 选择器支持 ID、class、type 和伪类(`:focus`、`:hover` 等)。

## Worker 系统

- Worker 用于在后台执行耗时操作,避免阻塞 UI;`run_worker()` 或 `@work` 装饰器创建。
- 异步 Worker 运行协程,适合 I/O 密集任务;线程 Worker(`thread=True`)运行同步函数,适合 CPU 密集或不支持异步的库。
- 线程 Worker 不能直接操作 UI,需通过 `call_from_thread()` 回调主线程。
- Worker 有 PENDING→RUNNING→SUCCESS/ERROR/CANCELLED 状态机。

## 测试与部署

- Textual 内置基于 pytest 的测试框架:`async with App.run_test() as pilot` 启动,`pilot` 可模拟点击、按键和等待渲染。
- 快照测试(Snapshot Testing)把渲染结果输出为 SVG,做视觉回归,能捕获布局和样式变化;测试应覆盖事件处理、状态变化、Worker 生命周期和边界情况。
- `textual serve app.py` 启动内置 Web 服务器,通过 WebSocket 把 TUI 渲染到浏览器:Python 进程在服务端,浏览器只显示渲染结果;鼠标和键盘事件经 WebSocket 传输,交互接近原生终端,适合跨平台和远程访问。
- 适用场景:DevOps/运维工具(远程 SSH)、离线/内网环境、数据仪表盘(实时更新)、CLI 增强(交互式表单、表格)。不适合:图形/3D 应用、营销网站、需要 SEO 的页面。Textual 是终端优先,Web 框架是浏览器优先,两者定位不同。
