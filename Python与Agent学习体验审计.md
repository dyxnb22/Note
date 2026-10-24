# Python 与 Agent 学习体验审计

日期：2026-10-23。版本：阅读路线与完整案例补充后的复审。

当前范围：Python 14 篇、Agent 27 篇，共 41 篇；补充检查根目录入口、共享订单案例的说明、数据与 4 份 Python 源文件。本次结论针对补充后的版本，替代前一版审计的改造前统计。

按用户要求，整改建议不包含自测题、练习题或答题环节。建议集中在作者补充讲解、明确阅读范围、完善示例与改善失败输出。

## 当前判断

现在已经有可以顺着阅读、找到代码并运行的学习主线。对会其他语言、转入 Python，以及会 Python、初次接触工具调用的读者，材料的可用性明显提高。

最值得继续处理的是三件事：阅读路线列出的先修知识与代码实际使用的知识对齐；说明现有 Agent 案例主要展示工具循环，补上观察改变后续动作的具体过程；让失败结果与轨迹能够帮助读者定位原因。

Python 零基础路线仍有小的先修缺口。后端服务、异步运行和生产交付方向目前以机制讲解为主，共享订单案例尚未把这些方向连接成完整服务。它们可以继续作为按需查阅的内容，不必为了篇幅对称而全部扩写。

语言方面，局部措辞已不是主要障碍。部分进阶章节仍有提纲感，原因是连续压缩多个概念与约束，缺少同一问题从出现到处理的完整解释。专业词多、边界说明多，并不能用来判断文本是否由 AI 生成。

## 这轮实际检查了什么

采用基于文本的读者任务走查，区分四类读者：Python 零基础、有其他语言经验、首次开发 Agent、已有工程经验回来查阅。没有进行真实读者访谈或观察实验，认知负担与阅读感受属于审计推断。

本轮完成：

- 扫描全部 41 篇的章节、显式内部链接、阅读入口与案例衔接；重点精读新路线、案例代码、先修衔接、错误处理和服务专题。
- 用 Python 3.12.13 在独立临时目录中执行正常、否定、不可见订单、轮数耗尽、输入文件缺失与轨迹目录缺失等路径。
- 用本地 Provider 样本检查额外参数的反馈、调用 ID 缺失时留下的轨迹；比较 A、B 两个订单的动作序列。
- 静态分析 FastAPI 三段示例的 app 赋值与路由注册位置。
- 复算余弦、RRF、温度采样、KV Cache 和容量估算中的数字。

本轮未安装 FastAPI、Pydantic、Textual 等第三方依赖，未进行真实模型调用，也没有重新逐条核验全部外部协议与 API 文档。上轮的 Python 3.14 运行记录仍保留在案例说明中，本轮执行重点使用 3.12。未做 Obsidian 桌面或手机界面的实际渲染测试。

### 当前结构与链接事实

| 项目 | Python | Agent |
|---|---:|---:|
| Markdown 篇数 | 14 | 27 |
| 显式内部链接出现次数 | 46 | 63 |
| 没有显式内部出链的篇数 | 5 | 18 |

另将共享案例 README 纳入检查后，共检查了 116 处本地文件链接，未发现文件目标缺失或显式小节锚点不存在。

这些数字用于观察导航结构。23 篇没有内部出链，不意味着页面无法找到：阅读路线与文件树仍可进入它们。当前问题是从正文继续查相关机制、返回主线，以及从搜索结果进入长篇专题时，路径还不够细。

共享案例的 4 份 Python 文件合计 399 行。代码量本身不是质量问题；初读时需要说明先读哪部分主流程，哪些校验和适配代码可以后读。

## 上轮改进的复核

| 原来的问题 | 当前状态 | 本轮结论 |
|---|---|---|
| 缺少不同基础读者的学习入口 | 已补 Python 与 Agent 路线，根目录已连接 | 入口问题基本解决，下一步细化先修与小节位置 |
| 理论正文没有连接实际程序 | 已补两篇案例讲解，并连接共享源码 | 基础脚本与工具循环的实践衔接已建立 |
| 没有可直接启动的最小主线 | 本地只读案例可以运行 | 正常与主要业务失败路径可用 |
| 工具调用缺少具体消息形状 | 已展示 assistant 提案与 tool 结果的配对 | 比仅有职责表更容易理解 |
| 同步示例与异步接口容易混淆 | Agent 案例已解释两种接口的区别 | 该说明应保留 |
| mock 结果容易被理解为真实模型能力 | 路线与案例已明确脚本化范围、接口限制和未验证项 | 表述较诚实，没有把离线成功推广为模型效果 |
| 不希望加入自测 | 当前新路线和案例没有答题要求 | 本轮继续遵守 |

## 十二个维度的判断

| 维度 | 现有长处 | 仍需改善的地方 | 主要影响谁 |
|---|---|---|---|
| 读者定位 | 已按基础与目标分路线 | “首次接触 Python”的先修清单还不完整 | 零基础读者 |
| 入口与开场 | 能找到命令、代码和结果 | 需要解释第一次阅读源码的具体顺序 | 首次接触多文件程序的人 |
| 先修与依赖 | 类型、异步和进阶内容已有后置说明 | 类、实例、方法和基本继承没有进入案例前的必读清单 | Python 初学者 |
| 认知负担 | 基础与进阶大方向已分开 | 路线的小节范围与正文的细节层级还不完全对应 | 顺序自学的人 |
| 概念准确传达 | 对工具、状态、业务结果区分较严谨 | 固定三步案例尚未展示动态动作选择 | 首次理解 Agent 的人 |
| 示例完整性 | CLI 与只读工具循环完整 | FastAPI、Textual 等专题仍是片段，独立或组合方式未明确 | 后端／界面开发读者 |
| 失败时的可解释性 | 有失败状态与保留观察的设计 | 部分错误信息过于笼统，部分异常提案未进入轨迹 | 跑不通或调试的人 |
| 导航与查阅 | 路线汇总了主要主题 | 多数选读范围只指向文件，长篇专题缺少返回与关联入口 | 首读与回来查阅的人 |
| 术语与业务背景 | 同一订单场景减少了重复设定 | 租户、可见范围、规则版本等仍有背景预设 | 无后端经验的人 |
| 可信度与复现 | 本地结果、版本和未验证范围都有说明 | 真实模型、框架服务与平台差异尚未全部实跑 | 准备继续接入服务的人 |
| 语言与阅读节奏 | 新案例更具体，断言与边界较准确 | 进阶综述仍有概念连续堆叠，具体因果解释偏少 | 首次学习进阶主题的人 |
| 迁移与延伸 | 普通脚本与工具循环共享业务函数，便于对照 | 从该案例走向 HTTP、异步、持久化或动态选择的下一步还比较跳跃 | 希望继续独立实现的人 |

以上“影响”是基于材料和任务路径的推断，不是实际读者失败比例。

## 优先处理的问题

### 1. 失败信息不足，读者难以把结果对应到具体原因

**证据类型：实际执行与源代码确认。优先程度：高。**

有三处不同的问题。

**输入与输出故障被合并。**在正常查询 A 时，程序可以三轮完成。将 --data 指向不存在的文件，或把 --trace 指向不存在的父目录，两种情况都得到：

~~~json
{"status": "failed", "reason": "input_or_output_error"}
~~~

两者退出码都是 1，stderr 都为空。前者尚未读取订单，后者是在循环返回后保存轨迹失败，输出却没有说明发生在哪个阶段。

位置：[main 中的数据读取、运行与轨迹保存](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/AI/实践/order_assistant/agent.py:167>)、[合并的异常处理](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/AI/实践/order_assistant/agent.py:176>)。普通脚本也将不同数据错误归为“无法读取有效的订单数据”，见[脚本错误输出](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/AI/实践/order_assistant/query_orders.py:28>)。

**参数校验丢掉了具体原因。**校验函数已经能够指出字段缺失、额外字段、布尔类型或状态不合法，见[validate_arguments](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/AI/实践/order_assistant/agent.py:69>)；运行时捕获后只回填：

~~~json
{
  "status": "invalid_arguments",
  "message": "提案不符合参数或当前状态约定"
}
~~~

本轮用多传 tenant_id 的提案复现了这一结果。读者无法从反馈直接知道是哪个字段出错；模型也没有获得具体修正方向。案例说明中的“可以在剩余轮数修正”是允许继续的策略，当前反馈对修正的帮助仍然有限。

位置：[工具错误转换](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/AI/实践/order_assistant/agent.py:139>)、[案例对错误修正的说明](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Agent/案例_订单查询Agent.md:106>)。

**部分协议错误没有保留原始提案。**调用 ID 缺失时，轨迹只有 round、request_messages 和 provider_error，没有 proposal。源代码在 parse_call 成功后才记录提案，见[先解析再记录的顺序](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/AI/实践/order_assistant/agent.py:121>)。本轮本地 Provider 样本确认了这一点。

这会限制[故障定位章节](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Agent/08_评测与可观测/轨迹诊断与线上故障.md:13>)提出的“对照原始响应与执行事件寻找首个偏差”。成功轨迹足以解释正常路径，异常轨迹的证据不够完整。

**建议：**

- 分开记录数据读取失败与轨迹保存失败；给出安全、可定位的文件或阶段说明。
- 为参数错误保留稳定类别与字段位置，例如额外字段、类型错误、状态不匹配；避免仅返回一条通用文字。
- 对协议异常保留可安全记录的原始提案与解析阶段；敏感内容继续按日志规则处理。
- 在案例中直接展示一次“错误输入 → 具体反馈 → 修正后结果”的完整讲解，不要求读者答题。

### 2. 首次阅读路线漏列了案例已经使用的类知识

**证据类型：文本与源码确认。优先程度：对零基础读者高。**

[Python 首读路线](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Python/00_阅读路线.md:18>)列出了基本类型、容器、流程、函数、异常、模块和类型注解，没有列入类与对象。[Agent 的先修说明](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Agent/00_02_阅读路线.md:7>)同样没有提到类与实例。

实际代码包含：

- [OrderNotFound(Exception)](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/AI/实践/order_assistant/orders.py:10>)：类定义与基本继承。
- [ScriptedProvider](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/AI/实践/order_assistant/providers.py:19>)：初始化方法、实例属性和方法调用。
- [NoRedirect](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/AI/实践/order_assistant/providers.py:14>)：继承与方法覆盖。
- 命令行解析器、Path 和 Provider 实例的使用。

这些知识在[语言核心的“类与对象”](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Python/01_语言核心.md:506>)中已经存在，无需另写一套教程。当前缺口是路线没有把读者送到那里。

**建议：**在进入案例前补“类、实例、方法与基本继承”的最小阅读范围，并明确不必先读完所有对象协议。Agent 案例也应说明可以先略过 HTTP 适配器中的继承细节。

另外，首次出现 demo、private、tenant_id 时，可用一小段说明它们代表不同组织或数据范围。当前例子已经说明值的归属，但仍预设读者理解“租户”这个词。

### 3. 现有案例展示了工具循环，尚未展示观察改变后续选择

**证据类型：文本、源码与两条实际动作路径确认。优先程度：对 Agent 入门高。**

[基础架构](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Agent/01_基础架构/Agent基础与架构.md:5>)把自主性解释为在授权范围内依据反馈动态选择动作，并区分 Agent 与固定 Workflow。

当前案例的提示明确规定先查订单、再查规则、最后提交答案，见[SYSTEM](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/AI/实践/order_assistant/agent.py:42>)。脚本化 Provider 按成功观察数量选择这三步，见[脚本化决策](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/AI/实践/order_assistant/providers.py:31>)。

本轮实际比较：

~~~text
订单 A（pending）：lookup_order → lookup_policy → submit_answer
订单 B（shipped）：lookup_order → lookup_policy → submit_answer
~~~

两次改变的是参数与最终结论，工具序列相同。运行时有继续、失败与停止分支，但这还不能展示模型如何依据不同信息选择另一种取证路径。

现有讲解已经诚实说明脚本化 Provider 不具备真实模型推理能力，也说明普通函数可以完成订单查询。这些说明是长处，应继续保留。需要补的是概念到示例的对应关系。

**建议：**把当前案例明确定位为“工具调用循环与运行控制的完整实现”。随后补一条有具体观察差异的完整分支，例如缺少物流证据时查询物流、信息已经充分时提交结论，并展示两条逐轮记录。

该补充应由作者完整讲解路径为什么变化。不能仅因为多运行了一个固定 if 分支，就把它当作已验证真实模型能够自主规划的证据。

### 4. 专题片段的独立性不清楚，后端路线仍有组合断点

**证据类型：静态代码分析；第三方框架未实跑。优先程度：对首次开发服务的读者中高。**

[后端阅读路线](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Python/00_阅读路线.md:40>)已经组织了 Pydantic、FastAPI 与后端服务的顺序，读者因此容易期待能拼出第一个服务。

FastAPI 专题的三段代码分别创建 app：

| 位置 | 创建的对象与路由 |
|---|---|
| [应用与路由](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Python/专题_FastAPI.md:18>) | app = FastAPI()，随后注册 /items/{item_id} |
| [依赖注入](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Python/专题_FastAPI.md:56>) | 再次创建 app，注册 /status |
| [生命周期](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Python/专题_FastAPI.md:82>) | 又创建带 lifespan 的 app，没有注册前两段路由 |

各段可以独立说明机制。若按顺序拼进同一文件，app 名字会绑定到最后的实例，前面注册在旧实例上的路由不会因此迁移。这是由代码结构与对象绑定关系得出的静态结论，本轮未安装 FastAPI 实跑 HTTP 请求。

[Textual 首例](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Python/专题_Textual与TUI.md:15>)也只定义应用类，没有启动调用。它可以作为组件组合片段，读者需要知道还缺少入口。

**建议：**先明确每块是“独立示例”“局部片段”还是“可顺序拼接”。后端方向优先补一份共用 orders.py 的最小服务文件，给出依赖、文件名、启动命令与一次请求响应。

共享订单案例已经补齐 CLI 与工具循环，不能把它视为 HTTP、异步、数据库事务和容器交付也已完整覆盖。后续案例按实际目标选一个方向展开即可。

### 5. 路线能导航到文件，还不够精确地导航到本次该读的位置

**证据类型：链接与正文扫描。优先程度：中。**

[Python 首读表](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Python/00_阅读路线.md:18>)要求读语言核心里的多个指定部分，链接却主要停在整篇文件顶部。该篇目前接近 800 行，读者仍要自己找起止位置。

[Agent 路线](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Agent/00_02_阅读路线.md:18>)使用“前几节”描述 Prompt 与 State 的阅读范围，没有明确读到哪个小节。[Pydantic 首读范围](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Python/00_阅读路线.md:45>)列出五个标题，仍缺少逐项跳转。

[语言进阶](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Python/02_语言进阶与异步.md>)、[Pydantic](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Python/专题_Pydantic.md>)、[FastAPI](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Python/专题_FastAPI.md>)等长篇或专题没有显式内部出链。通过搜索直接进入正文的人，不容易看见自己处于哪条路线，也不容易回到配套案例。

**建议：**

- 为路线中明确选读的段落加小节链接，写清本次读到哪里即可。
- 长篇专题提供简短的“首次阅读范围”和返回路线／案例入口。
- 概念重复处保留当前场景的必要说明，再链接到主解释位置，不必为增加链接把每个术语都重复定义。

文件和小节目标都存在，当前属于导航颗粒度与查阅成本问题，不应再报告成“没有学习路线”或“链接坏了”。

### 6. 进阶章节的说明密度适合复习，首次学习仍需要因果展开

**证据类型：文本确认与读者体验推断。优先程度：中，按目标处理。**

[生产与交付](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Python/07_生产与交付.md>)在 63 行内讨论构建输入、多阶段镜像、持久数据、探针、信号、Worker、尾延迟与回退。每个结论都有用途，首次接触这些主题时却需要更多背景，才能理解为什么在这里引入该机制。

[工程基础](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Python/04_工程基础.md>)与新案例已经解释了函数和模块的分工；src 布局、安装产物、HTTP 生命周期、事务与部署还缺少与同一份程序的实际连接。

**建议：**继续保留精简综述作为查阅页。在选定方向的完整案例中，用具体现象带出机制，例如“工作目录导入成功、安装产物缺模块”“路由返回后资源何时释放”。每次补足一条因果链，避免平均扩写所有章节。

语言润色优先处理含义模糊、术语首次出现无解释、同一段同时切换多个层次的位置。无需把所有边界词删掉，也无需为了通俗而省略准确限制。

## 平台、真实模型与版本的阅读预期

以下是适用范围说明，不全部作为缺陷处理。

### 命令路径有平台预设

两篇案例的 --trace 使用 /tmp 路径，适合当前 macOS／Linux 命令环境。共享 README 没有单独标明这条命令的平台条件。

本轮在本机复现了父目录不存在时的通用 I/O 错误；没有在 Windows 上实跑。根据路径写入方式，其他系统或自定义目录同样需要父目录可写且已存在。

可以改用案例目录中的相对轨迹路径，或按平台说明保存位置。这一项对当前 Mac 使用者影响较小，对分享给其他平台的读者影响较大。

### 真实模型接入尚未验证，但文档已说明

[可选模型接口](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/AI/实践/order_assistant/README.md:61>)明确列出端点、模型标识、密钥与支持的协议子集，也说明尚未调用真实模型。这个边界应保留。

当前可以确认本地循环与部分适配逻辑，不能确认任意标注“兼容”的服务都能直接使用。资料的定位宜保持为可接入的示例，实现能力与服务实测结果分开记录。

### 算例值得保留

本轮复算与文本一致的例子包括：

| 算例 | 本轮核对结果 | 对读者的价值 |
|---|---|---|
| [点积与余弦](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Agent/06_RAG与知识库/RAG与检索.md:50>) | 点积 A=10、B=1；A 的余弦约 0.707、B=1 | 看得见向量长度与方向造成的差异 |
| [RRF 融合](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Agent/06_RAG与知识库/RAG与检索.md:81>) | k=60 时，b≈0.03252，高于 a≈0.01639、c≈0.01613 | 能具体理解两路支持怎样影响排名 |
| [温度采样](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Agent/10_模型与推理/01_模型与推理基础.md:35>) | T=1 约为 0.665／0.245／0.090；T=0.5 约为 0.867／0.117／0.016 | 用数字说明分布变集中 |
| [KV Cache](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Agent/10_模型与推理/01_模型与推理基础.md:64>) | 单序列约 0.5 GiB；八个同长度序列约 4 GiB | 公式、单位与量级能够对应 |
| [容量估算](</Users/diaoyuxuan/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes/Learning/Agent/09_工程化与系统设计/01_生产工程与系统设计.md:59>) | 6 次请求／秒乘 4 秒为 24；乘 8 秒为 48 | 把业务任务拆为内部负载 |

这里核对的是给定条件下的计算，不代表实际检索质量、模型效果或服务吞吐已经验证。

## 四类读者的使用结论

| 读者 | 当前能得到什么 | 主要卡点 | 优先改善 |
|---|---|---|---|
| Python 零基础 | 能找到起步方式、看到完整脚本与结果 | 类知识漏入先修，业务术语有预设，选读段落需要自己定位 | 补最小先修与小节链接 |
| 有其他语言经验 | 能高效比较对象、参数、类型、迭代和异步差异 | 进阶内容密度高，专题查阅关系不够集中 | 保留精简说明，补返回与关联入口 |
| 首次开发 Agent | 能理解提案、工具结果、调用 ID、轮数与完成校验 | 看不到动态动作选择；异常反馈与轨迹不足 | 补分支讲解和具体错误信息 |
| 已有工程经验 | 能用来检查权限、幂等、状态、恢复和容量取舍 | 继续落到 HTTP、异步或部署时仍需自行组织实现 | 按所选方向补完整工程案例，不强制全部展开 |

## 建议的处理顺序

| 顺序 | 工作 | 相对成本 | 修订结果应直接呈现什么 |
|---|---|---|---|
| 1 | 对齐类知识等先修与实际案例 | 小 | 案例前可直达所需语法，明确可暂缓的部分 |
| 1 | 改善参数错误、文件错误与协议异常轨迹 | 小到中 | 同一份记录能说明失败阶段、具体约束与已有观察 |
| 2 | 明确工具循环案例的教学目标，补一条观察改变路径的讲解 | 中 | 两条具体轨迹与选择依据，不把脚本化结果当作模型能力 |
| 2 | 标注专题片段是否独立；按需补最小 HTTP 服务 | 小到中 | 一份可启动文件、启动命令与请求响应 |
| 3 | 细化小节导航与长篇专题的返回入口 | 小 | 不用在数百行正文里反复寻找本次选读段落 |
| 3 | 按选定工程方向补因果解释与平台说明 | 中 | 现象、实现、结果和适用范围连在一起 |

本轮更新审计结论与证据，以上新发现尚未修订正文或代码。后续改善以这些具体阅读障碍为依据，不建议继续对全部 41 篇做同一套措辞替换，也不建议为了“完整”无差别增加篇幅。
