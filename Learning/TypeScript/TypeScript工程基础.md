# TypeScript 工程基础

TypeScript 的核心价值不是“给 JavaScript 加注解”，而是用类型表达系统边界，让接口变更和重构可以被编译器检查。类型在编译后会消失，因此外部数据、权限和业务规则仍需要运行时验证。

## 1. 类型系统的主线

先掌握 primitive、object、array、tuple、literal、union、interface 和 type alias。实践中最重要的选择是：

- 用 `unknown` 接住尚未验证的值，用 `any` 等于主动退出类型检查。
- 用 union 表达“可能是几种形态”，用判别字段表达每种形态的业务含义。
- `interface` 适合稳定对象契约和声明合并；`type` 适合 union、映射与组合。
- 类型应表达不变量，不需要给编译器已经能推断的局部变量重复加注解。

```ts
type Job =
  | { kind: "queued"; id: string }
  | { kind: "running"; id: string; startedAt: Date }
  | { kind: "failed"; id: string; error: string }
  | { kind: "completed"; id: string; output: unknown };

function describe(job: Job): string {
  switch (job.kind) {
    case "queued":
      return `${job.id} is waiting`;
    case "running":
      return `${job.id} started at ${job.startedAt.toISOString()}`;
    case "failed":
      return `${job.id} failed: ${job.error}`;
    case "completed":
      return `${job.id} completed`;
    default: {
      const unreachable: never = job;
      return unreachable;
    }
  }
}
```

这个例子同时体现类型收窄、控制流分析和穷尽检查。新增状态但忘记处理时，编译器会在 `never` 处报错。

## 2. 收窄与外部边界

`typeof`、`in`、`instanceof`、判别字段和用户定义 type predicate 都能收窄类型，但类型守卫只证明你实际检查的条件。来自 HTTP、数据库、RPC、链上节点和模型输出的数据都应先视为 `unknown`。

```ts
type User = { id: string; email: string };

function isUser(value: unknown): value is User {
  if (typeof value !== "object" || value === null) return false;
  const record = value as Record<string, unknown>;
  return typeof record.id === "string" && typeof record.email === "string";
}
```

手写守卫适合很小的结构。复杂输入应使用 Zod、Valibot 或 JSON Schema，并把校验错误映射成稳定、可定位的字段错误。

Schema 不应“一套到处 optional”。至少区分 create、update、response 和 internal 模型；新增可选字段通常向后兼容，删除字段或改变语义需要版本与迁移策略。

## 3. 泛型与类型变换

泛型的作用是复用逻辑时保留调用者的具体信息：

```ts
function first<T>(items: readonly T[]): T | undefined {
  return items[0];
}

function byId<T extends { id: string }>(items: readonly T[]): Map<string, T> {
  return new Map(items.map((item) => [item.id, item]));
}
```

`keyof` 获取属性键，`typeof` 从值推导类型，mapped type 批量变换属性，conditional type 根据类型关系分支。`Partial`、`Pick`、`Omit` 和 `Record` 足以解决大多数业务问题。

复杂类型应有明确收益。若只有作者能解释一段条件类型，通常应该改成命名清楚的普通类型或把约束移到运行时。

## 4. 模块、配置与组织

ESM 是现代项目的优先选择，但必须区分 TypeScript 的编译期解析和 Node/浏览器的运行时解析。最低配置建议：

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noEmit": true
  }
}
```

具体选项要与运行时和构建器匹配。路径别名必须同时配置编译器、测试器、打包器和运行时，否则会出现“开发能过、部署失败”。

代码按领域而不是文件类型组织，避免巨型 `utils`。公开 barrel export 要克制：它会扩大公共 API，也可能隐藏循环依赖。

## 5. 异步、取消与错误

`async/await` 是 Promise 的语法形式；任何 `await` 都可能 reject。错误应在能补充业务语义或转换协议的位置处理，不能用空 `catch` 吞掉。

- 独立任务并行且任一失败就应终止：`Promise.all`。
- 需要收集每项成功和失败：`Promise.allSettled`。
- 超时与取消：使用 `AbortController`，并确保底层库真正接受 `signal`。
- 重试：只用于可重试错误，并确认操作幂等、设置次数和总时间预算。

```ts
async function fetchJson(url: string, timeoutMs = 5_000): Promise<unknown> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, { signal: controller.signal });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } finally {
    clearTimeout(timer);
  }
}
```

## 6. API 契约

接口设计从资源、动作、输入、输出、错误和版本策略开始。DTO 不是数据库实体，不应暴露仅供内部使用的字段。

特别明确以下语义：

- 分页是 offset、cursor 还是 keyset；
- 时间使用哪个时区和格式；
- 金额使用最小货币单位、decimal 字符串还是整数；
- `null`、缺省字段和空集合分别表示什么；
- 写操作如何传递幂等键；
- 错误码是否稳定、能否安全展示。

共享 TypeScript 类型能减少重复，但不能保证部署中的前后端版本一致。更可靠的做法是以 OpenAPI、JSON Schema、Protocol Buffers 等为契约源，再生成客户端并做兼容性检查。

## 7. 测试与重构

测试覆盖行为而不是实现细节：纯函数做单元测试，网络/数据库/schema 边界做集成测试，关键用户路径保留少量端到端测试。

重构遵循以下顺序：

1. 用测试和类型锁住当前行为。
2. 运行 `tsc --noEmit` 和测试建立基线。
3. 小步移动或改名，每一步保持可运行。
4. 删除临时兼容层和 `as any`。
5. 再次检查公共 API 和生成产物。

`as any` 不是修复；它是一个需要解释、限定范围并偿还的例外。

## 8. Web3 与 AI 应用

Web3 中常见边界是 ABI、RPC 返回值、钱包签名、交易状态和链上事件。AI 应用中常见边界是模型结构化输出、工具参数、流式事件、会话状态和 SDK 错误。

两类系统共有的设计原则：

- 外部数据先验证，再进入领域模型；
- 长操作可取消、可观察，写操作有幂等保护；
- 用状态机表达 pending、confirmed、failed 等生命周期；
- Secret、权限判断和高风险动作只存在于可信服务端；
- 前端日志不记录签名、Token、完整 Prompt 或个人数据。

TypeScript 能提高协作与重构安全性，但不能替代运行时校验、授权、审计和恢复机制。

## 验收清单

- `tsc --noEmit`、lint 和测试均通过。
- 外部输入的入口类型是 `unknown`，并有运行时校验。
- 没有用 `any`、非空断言或类型断言掩盖未验证数据。
- 异步边界有超时、取消和稳定的错误映射。
- 公共契约不直接泄漏数据库实体或第三方库类型。
- 类型、schema 和实际运行时行为不存在多份互相漂移的定义。

`#typescript #types #schema #async #testing #engineering`
