# 专题：Textual 与 TUI

> Textual 是基于 Rich 的 Python 终端界面框架。以下以 Textual 6.x 为背景，讲消息怎样驱动组件、后台工作怎样回到界面，以及怎样测试。

## 核心架构与 MessagePump

- MessagePump 提供消息投递与处理机制。应用通过 post_message 提交消息，由组件处理，内部队列交给框架管理。组件也可以调用普通方法，涉及共享状态时仍需处理并发竞争。
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

- 复杂界面可以把事件转换和状态更新放到 Presenter 或 Reducer 中，单独测试；组件负责输入和显示。简单界面直接写在组件里就够。

## Widget 生命周期

| 阶段 | 发生什么 |
|---|---|
| `__init__` | 初始化组件对象 |
| compose | 声明界面里放哪些子组件 |
| Mount | 组件挂载到组件树后收到的事件，可在 on_mount 中继续初始化 |
| Unmount | 组件被移除时收到的事件，可用于清理自行持有的外部资源 |

所属组件退出时，框架会请求取消关联的 Worker；线程 Worker 等工作仍需主动响应取消。

- `compose()` 是声明式 API，用来描述要组合的子组件；`mount()` 在运行时追加组件。两者可配合使用，先声明固定布局，再按需要插入新组件。

## 事件系统

- 对支持冒泡的消息，处理后还可能继续传递给父节点。需要终止传递时调用 `message.stop()`，例如避免同一次提交被父子组件重复处理。
- `prevent_default()` 阻止同一消息继续调用基类上的处理器；`stop()` 用于停止冒泡。两者控制的阶段不同，不能互相替代。
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

- 自行缓冲事件时，区分可合并的进度消息和必须保留的状态变化，后者不能丢弃。容量和是否持久化由应用设置。

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
- 派生属性例如 total，要先声明为 reactive，再定义 `compute_total` 方法，框架才会在响应式状态变化时重算它。只给一个普通方法加 compute_ 前缀，不会自动让它关联到某个属性。
- var 适合保存内部状态：默认赋值不会触发重绘，但仍会验证值、通知观察方法。
- reactive 默认会请求刷新。
- 原地修改属性里的列表或字典，不等于给属性重新赋值。需要按场景主动通知变化或刷新。
- data_bind 建立单向的数据绑定：源属性变化更新目标属性，修改目标不会自动反向更新源。

## Worker 系统

- 用 `run_worker(...)` 或 `@work` 启动 Worker，执行耗时操作。例如在同一管理范围内，给新 Worker 指定 search 组和 `exclusive=True`，就会请求取消已有的 search 组 Worker。它不提供业务互斥：旧任务或线程可能稍后才响应取消，期间仍可能与新任务同时运行。
- 异步 Worker 用于异步 I/O，线程 Worker 用于同步阻塞操作。将长操作交给 Worker，让消息处理器尽快返回，否则该组件的下一条消息仍需等待当前处理器结束。纯 Python 的 CPU 密集计算通常还需考虑多进程等方式，单纯增加线程未必能利用多核。
- 线程 Worker 更新 UI 通常应通过 app.call_from_thread；post_message 是明确线程安全的消息入口。不要把任意 call_later 调用假设为跨线程安全。
- Worker 的状态为 `PENDING → RUNNING → SUCCESS / ERROR / CANCELLED`。
- 调用 `worker.cancel()` 请求取消。
- 默认情况下，Worker 出错可能导致应用退出。需要自己处理错误时，设置 `exit_on_error=False` 并处理状态事件，不能假定框架只会记一条错误日志。
- `get_current_worker()` 在任务内部检查 `worker.is_cancelled`，长循环里主动让出并响应取消。

## 用事件与状态测试界面

界面测试覆盖事件处理、状态更新、后台查询和退出清理。点击按钮后，等待查询完成，再检查结果是否对应当前选择。

App.run_test 提供不依赖交互终端的应用测试环境，Pilot 模拟点击和按键，计时默认仍使用真实时间。网络行为和终端兼容性通过相应集成测试验证。

快照检查显示内容，状态断言检查数据变化。除正常结果外，还覆盖空结果、查询失败、旧请求迟到和退出清理。

## Web 部署

- Textual 应用也可以经浏览器访问：逻辑运行在服务端，浏览器显示界面并传回输入。
- 它适合运维工具、离线或内网应用、数据仪表盘，以及有表单和表格的交互式 CLI，也可用于远程 SSH。以图形或 3D 为主的界面、营销站、依赖 SEO 的页面，通常应选择其他技术。

## 为什么迟到结果会覆盖用户的新选择？

假设用户先选择 A，随后切换到 B；B 查询先完成，A 查询后完成。如果每个返回值都直接覆盖显示，最后界面会显示已经过时的 A。

每切换一次选择，就把请求编号加一，让查询记下启动时的编号。结果回来后，只有编号仍与当前一致，才更新界面。这个递增编号也叫请求代次。取消旧 Worker 可以减少浪费，但旧任务未必立即停止，编号检查仍能挡住迟到结果。

| 时点 | 当前选择 | 返回结果 | 界面应显示 |
|---|---|---|---|
| 发起 A 查询 | A | 尚无 | A 的加载状态 |
| 切换并发起 B | B | 尚无 | B 的加载状态 |
| B 先完成 | B | B | B |
| A 迟到 | B | A | 继续显示 B |

查询服务把结果交回组件时，同时带上请求代次。组件退出时清理持有的 Worker、订阅和客户端；远端业务任务是否取消，由任务控制逻辑决定。

## 参考资料

- [Textual 响应式属性与单向绑定](https://textual.textualize.io/guide/reactivity/#data-binding)
- [Textual Worker 取消、错误和线程边界](https://textual.textualize.io/guide/workers/)
- [Textual 挂载事件](https://textual.textualize.io/events/mount/)
