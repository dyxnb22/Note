# 专题：Textual 与 TUI

> Textual 是基于 Rich 的 Python 终端界面框架。本专题介绍消息、组件、响应式属性、Worker 和测试。框架机制应结合实际依赖版本核对。

## 核心架构与 MessagePump

- MessagePump 提供消息投递与处理机制。post_message 提交消息，由组件的消息处理流程消费；内部队列属于实现细节，应用代码应使用公开接口。消息机制不会自动消除共享状态竞争，也不妨碍普通方法调用。
- `App` 和 `Widget` 都继承自 `DOMNode`，而 `DOMNode` 继承自 `MessagePump`。`Screen` 是 `Widget` 的子类；`App` 本身不是 `Widget`。

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button
from textual.containers import Vertical


class TodoApp(App):
    CSS = "Vertical { padding: 1 2; }"  # 内联 TCSS

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Button("Add", id="add", variant="primary")
        yield Footer()
```

- 界面复杂后，可以将事件转换与状态更新移到独立的 Presenter 或 Reducer 中。组件负责采集输入和展示结果，状态逻辑则可脱离终端进行测试。简单界面不必预先增加这一层。

## Widget 生命周期

- `__init__` 初始化组件对象；compose 产出要组合的子组件；组件挂载到应用的组件树后收到 Mount 事件，可在 on_mount 中执行挂载后的初始化。Unmount 表示组件被移除，可用于清理自行持有的外部资源。关联 Worker 由框架在所属组件退出时请求取消，线程等工作仍需协作停止。
- `compose()` 是声明式 API，`mount()` 是命令式追加，两者可配合(先静态骨架、后动态插入)。

## 事件系统

- 对支持冒泡的消息，处理后还可能继续传递给父节点。需要终止传递时调用 `message.stop()`，例如避免同一次提交被父子组件重复处理。
- `prevent_default()` 用于阻止相应的默认处理；`stop()` 用于停止冒泡。两者控制的阶段不同，不能互相替代。
- `@on(MessageType, selector)` 根据消息类型和选择器注册处理器。例如，`@on(Button.Pressed, "#confirm")` 只处理指定按钮的点击消息。
- 相比 `on_button_pressed` 等命名约定，装饰器可以更直接地表达消息来源条件。

```python
from textual import on
from textual.app import App
from textual.widgets import Button, Input


class MyApp(App):
    @on(Button.Pressed, "#confirm")
    def confirm(self) -> None:
        pass  # 此段只展示消息处理器声明。

    @on(Input.Submitted)
    def submitted(self) -> None:
        pass
```

- 需要自行设计事件缓冲时，应区分可合并的进度消息和必须保留的状态变化。这里讨论的是应用的事件处理策略，不表示 Textual 的内部队列天然具备你需要的容量限制或持久化能力。

## 响应式数据绑定

```python
from textual.reactive import reactive, var
from textual.widget import Widget


class Panel(Widget):
    count: reactive[int] = reactive(0)
    cache: var[dict] = var(dict)  # 默认不触发重绘，每个实例创建独立字典

    def watch_count(self, old: int, new: int) -> None:
        self.last_change = (old, new)  # 观察变化；reactive 自己负责默认刷新。

    def validate_count(self, value: int) -> int:  # 赋值前拦截
        return max(0, value)
```

- 响应式属性可以在赋值时执行验证、通知观察方法，并按配置触发界面更新。验证负责检查或调整值，观察方法则处理值变化后的逻辑。
- 声明派生 reactive 属性并提供对应的 compute_* 方法后，框架可在响应式状态变化时重算；不是给任意普通方法加上 compute_ 前缀就建立绑定。
- var 默认不因赋值自动重绘，但仍有响应式验证和观察能力，适合内部状态。reactive 默认会请求刷新；直接修改属性里列表或字典的内部内容不等于给属性重新赋值，需要按场景主动通知或刷新。
- data_bind 建立单向的数据绑定：源属性变化更新目标属性，修改目标不会自动反向更新源。

## Worker 系统

- 耗时操作放 Worker，不阻塞 UI：`run_worker(...)` 或 `@work` 装饰器；`exclusive=True` 会取消同一管理范围、同一组里的既有 Worker；不是只按函数名判断，也不是数据库互斥锁。取消具有协作性质，仍需处理旧任务或线程未立刻停止的情况。
- 异步 Worker 适合异步 I/O；线程 Worker 可用于同步阻塞操作。纯 Python 的 CPU 密集计算通常不能仅靠增加线程获得多核执行收益。
- 线程 Worker 更新 UI 通常应通过 app.call_from_thread；post_message 是明确线程安全的消息入口。不要把任意 call_later 调用假设为跨线程安全。
- 状态机：`PENDING → RUNNING → SUCCESS / ERROR / CANCELLED`；取消用 `worker.cancel()`，默认 Worker 异常可能退出应用；需要自行处理时配置 `exit_on_error=False` 并处理状态事件，不应假设默认只记录错误。
- `get_current_worker()` 在任务内部检查 `worker.is_cancelled`，长循环里主动让出并响应取消。

## 测试

App.run_test() 以无界面模式运行应用，提供 pilot 模拟点击和按键，并通过异步等待让界面处理消息。下面包含组件、点击处理与断言，不会启动交互终端窗口，也不会把真实定时器自动变成虚拟时钟。

```python
import asyncio
from textual import on
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Button, Static


class CountPanel(Static):
    count = reactive(0)

    def render(self) -> str:
        return str(self.count)


class CountApp(App):
    def compose(self) -> ComposeResult:
        yield CountPanel()
        yield Button("加一", id="confirm")

    @on(Button.Pressed, "#confirm")
    def increment(self) -> None:
        self.query_one(CountPanel).count += 1


async def check_click():
    app = CountApp()
    async with app.run_test() as pilot:
        await pilot.click("#confirm")
        assert app.query_one(CountPanel).count == 1


asyncio.run(check_click())
```

- 测试覆盖：事件处理、状态变化、Worker 生命周期(含取消)、边界输入。
- SVG 快照测试需要相应的测试插件，按官方文档安装，并与锁定的 Textual 版本配套使用。

## Web 部署

- Textual 生态也提供通过浏览器访问终端界面的能力。应用逻辑运行在服务端，浏览器负责显示并传回输入。
- 部署组件和命令可能随版本变化，实施时应查阅对应版本的文档。本专题不将某个命令作为所有版本通用的部署方式。
- 适用：DevOps/运维工具(远程 SSH 场景依然可用)、离线/内网环境、数据仪表盘、CLI 增强(交互式表单、表格)。不适合：图形/3D、营销站、需要 SEO 的页面。Textual 是终端优先，Web 框架是浏览器优先，定位不同。

## 参考资料

- [Textual 响应式属性与单向绑定](https://textual.textualize.io/guide/reactivity/#data-binding)

- [Textual Worker 取消、错误和线程边界](https://textual.textualize.io/guide/workers/)
- [Textual 挂载事件](https://textual.textualize.io/events/mount/)
