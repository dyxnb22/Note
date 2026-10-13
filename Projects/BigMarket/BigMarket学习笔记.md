# 网关（Gateway Service） done

## 一句话定位

Gateway 是系统对外的统一 HTTP 入口，监听 **8080**，按请求路径把流量转给 Auth、Admin、Chatbot 或 Market。客户端只需使用 Gateway 地址，不必直接依赖各微服务的地址和端口；Gateway 不处理抽奖、积分等业务。

    浏览器 / 内部服务 → Gateway :8080 → Auth / Admin / Chatbot / Market

一次正常 API 请求的处理顺序是：客户端请求 Gateway :8080 → WebFlux 收到请求 → CORS WebFilter → Path Predicate 匹配 Route → GlobalFilter 和路由级 GatewayFilter → 下游服务 → Gateway 返回响应。CORS 预检 OPTIONS 请求可能在 CORS 阶段直接得到响应。

## 1. 技术栈与运行配置

入口类 GatewayApplication 启动 Spring Boot。模块使用 Spring Cloud Gateway 和 WebFlux，并集成 Reactor Resilience4j、Actuator 和 Prometheus。

Gateway 基于 **WebFlux 响应式栈**，**用 Mono 和过滤器链异步处理请求，适合以网络 I/O 转发为主的场景**。不要添加 spring-boot-starter-web，避免把 Spring MVC/Servlet 栈混入这个响应式网关。

| Profile | 用途 | 下游地址 |
|---|---|---|
| dev（默认） | 本地开发 | localhost:8081–8084 |
| docker | Docker Compose | Docker 网络中的服务名 |
| secure | 安全配置覆盖层 | 收紧 CORS 来源并启用限流 |

本地默认激活 dev；Compose 激活 docker。路由由 YAML 静态配置，目标是固定 host/port；当前没有使用 lb:// 地址或 Nacos 动态发现 Gateway 路由。

## 2. 请求进入 Gateway：CORS 检查

URL 到达 Gateway 后，浏览器跨域请求先由 WebFlux Web 层的 WebFilter 处理；本项目使用 CorsWebFilter：默认允许来源为 *，允许所有方法和请求头，但 allowCredentials=false，也就是不允许跨域携带凭证。secure profile 默认把来源收紧为 http://127.0.0.1:5173，可用 APP_CORS_ALLOWED_ORIGINS 覆盖。

浏览器的 CORS 预检 OPTIONS 请求可由 Gateway 直接响应，不必转发到业务服务；如果前端与 API 经同源反向代理提供，浏览器通常不会触发跨域检查。

## 3. 按 URL 匹配路由

CORS 检查后，Gateway 根据 URL 的 Path 条件选择 Route。每条路由有四个要素：

- id：路由名称。
- uri：下游服务地址。
- predicates：匹配请求的条件。
- filters：路由匹配后执行的处理。

| 服务 | Path 条件 | 本地目标 | Docker 默认目标 |
|---|---|---|---|
| Auth | <code>/api/*/auth/**</code> | localhost:8081 | big-market-auth-service:8081 |
| Admin | <code>/api/*/admin/**</code> | localhost:8082 | big-market-admin-service:8082 |
| Chatbot | <code>/api/*/chatbot/**</code> | localhost:8084 | big-market-chatbot-service:8084 |
| Market | <code>/api/**</code> | localhost:8083 | big-market-market-service:8083 |

Path 中单星号匹配一个路径片段，双星号匹配后续路径
## 4. 路由匹配后执行过滤器

路由选中后，Gateway 执行全局过滤器和当前 Route 配置的过滤器：

- **GlobalFilter**：Gateway 路由链的全局过滤器。本项目的 TraceIdGlobalFilter 实现了 GlobalFilter 和 Ordered。
- **GatewayFilter**：绑定到具体 Route。本项目每条路由都配置 CircuitBreaker；Docker 的 Auth 和 Market 路由还配置了 IpPathRateLimit。

WebFilter 在 WebFlux Web 层处理请求；Predicate 决定“请求是否走这条路由”；Filter 决定“选中路由后请求如何处理”。GlobalFilter 面向 Gateway 路由链，GatewayFilter 由具体路由配置。

### 4.1 Trace ID

TraceIdGlobalFilter 读取 X-Trace-Id：请求已有就沿用，没有就生成 UUID。它把 ID 传给下游，并在**响应提交前写回响应头**，便于按同一个 ID 关联网关和下游日志。Trace ID 是日志关联标识，不是身份凭证。

### 4.2 熔断与降级

每条服务路由使用独立的 Resilience4j CircuitBreaker 实例：auth-cb、admin-cb、chatbot-cb、market-cb。

熔断器有三个状态：Closed 正常放行并统计结果；Open 快速失败，避免继续压向故障下游；Half-open 在**等待后放少量探测请求，判断下游是否恢复**。

### 4.3 限流

本项目使用内存令牌桶，按来源 IP 和路径前缀限流；没有令牌时返回 HTTP 429。仅 Auth、Market 路由接入，默认关闭，secure profile 开启。限流状态只保存在当前 Gateway 实例中，多实例不会共享；如果 Gateway 位于反向代理后，还要确认识别到的来源 IP 是否为真实客户端 IP。

## 5. 转发下游并返回响应

过滤器放行后，Gateway 把请求转发到选中 Route 的 uri。路由没有配置 StripPrefix 或 RewritePath，因此**不会显式改写请求路径**；例如 Market 会收到完整 API 路径。下游响应再经 Gateway 返回客户端。

如果请求路径不匹配任何 Route，Gateway 没有下游目标，不会自动转给业务服务。

下游调用触发熔断降级时，fallback 使用 forward:/fallback/{service}，在 Gateway 应用内转到 FallbackController，不会再发起网络请求。它返回 HTTP 503 和统一错误体：code=0007、info=网关接口调用失败、data=null。当前配置了熔断和 fallback，没有配置 Gateway Retry；熔断不是重试，也不能保证业务成功。

## 6. 运维与观测

Gateway 暴露 Actuator 的 health、info、circuitbreakers 和 prometheus 端点，并启用 Prometheus 指标导出。Compose 健康检查访问 /actuator/health。

## 7. 常见追问速记

**问：Predicate 和 Filter 有什么区别？**  
Predicate 负责匹配 Route；Filter 在路由选中后处理请求或响应。

**问：GlobalFilter 和 GatewayFilter 有什么区别？**  
GlobalFilter 加入 Gateway **路由过滤器链**；GatewayFilter 由**具体 Route 配置**。本项目 Trace ID 使用 GlobalFilter，限流使用路由级 GatewayFilter。

**问：下游服务故障时怎么办？**  
CircuitBreaker 根据**调用结果打开熔断**，路由 fallback 转到本地 Controller 返回 503；它不是重试。

**问：当前限流能覆盖多个 Gateway 实例吗？**  
不能。桶在**各实例的 JVM 内存中**；要做跨实例统一限流，需要**共享状态或分布式限流方案**。

# 登录、鉴权与注销

## 业务流程总览

Auth 管理账号凭证并签发、校验和吊销 JWT。一次完整的用户会话大致经过以下步骤：

```text
Auth 启动时准备演示账号
  → 用户登录，Auth 验证密码并签发 JWT
  → 前端保存 Token；需要时调用 Auth /verify 恢复会话
  → 业务请求到达 Market，由 Market 本地验证 Token 和用户身份
  → 用户退出，Auth 吊销当前 Token 的 jti
```

## 1. 启动准备：演示账号写入数据库

本地和验收配置可通过 `app.auth.seed-users` 提供演示账号。Auth 启动时，`AuthUserSeedRunner` 会使用 Argon2id 对配置的密码做哈希，再通过 MyBatis 写入或更新 MySQL 的 `big_market.auth_user` 表。登录时也通过 MyBatis 查询数据库，不直接使用配置中的明文密码。

相关实现见 [`AuthUserSeedRunner.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-auth-service/src/main/java/com/dyx/market/auth/user/AuthUserSeedRunner.java)、[`AuthUserRepository.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-auth-service/src/main/java/com/dyx/market/auth/user/AuthUserRepository.java)、[`MyBatisAuthUserRepository.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-auth-service/src/main/java/com/dyx/market/auth/user/MyBatisAuthUserRepository.java)、[`AuthUserMapper.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-auth-service/src/main/java/com/dyx/market/auth/user/mapper/AuthUserMapper.java) 和 [auth_user_mapper.xml](/Users/diaoyuxuan/big-market-ai-platform/big-market-auth-service/src/main/resources/mybatis/mapper/mysql/auth_user_mapper.xml)。

## 2. 登录：账号密码换成 JWT

前端登录页通过 `loginWithPassword` 发送 `POST /api/v1/auth/login`。请求经过 Gateway 转发到 Auth 服务，由 [`AuthAccessController.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-auth-service/src/main/java/com/dyx/market/auth/AuthAccessController.java) 接收。Controller 检查必填参数后，把登录用例交给 `LoginApplicationService`。

`LoginApplicationService` 从 `auth_user` 表读取账号，检查账号是否启用，再用 Argon2id 校验输入密码和数据库中的密码哈希。未知账号、密码错误或账号已禁用，都会返回相同的登录错误，业务码为 `0009`，避免通过错误提示泄露账号状态。

密码校验通过后，`LoginApplicationService` 调用 `AuthService` 签发 JWT。有效期是 24 小时（`expiresIn = 86400` 秒）。Token 包含：

- `openId`：用户标识
- `jti`：Token 唯一 ID
- `iat`、`exp`：签发时间和过期时间
- `sub`（subject）：Token 代表的用户主体，这里使用用户标识，与 `openId` 相同；它不是签发者
- `iss`（issuer）：JWT 签发者字段；当前 Auth 代码没有设置

JWT 使用 Auth 和业务服务共享的密钥做 HS256 签名，用于验证 Token 是否被篡改；JWT 本身没有加密，载荷可以被解码读取。

登录响应包含 `userId`、JWT 和有效期。前端将 Token 和 `userId` 存入 `sessionStorage`；后续 API 请求会在 `Authorization` 请求头中携带 Token。相关实现见 [`LoginApplicationService.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-auth-service/src/main/java/com/dyx/market/auth/login/LoginApplicationService.java) 和 [`api-client.js`](/Users/diaoyuxuan/big-market-ai-platform/big-market-web/api-client.js)。

## 3. 恢复会话：Auth 的 `/verify`

用户重新进入页面时，前端可以调用 `GET /api/v1/auth/verify`，在 `Authorization` 请求头中提交已有 Token。Auth 检查签名、有效期和吊销状态；通过后返回 Token 中的用户标识，失败时返回业务码 `0009`。

这个接口用于前端检查已有会话。真正调用抽奖、签到等受保护接口时，业务请求会继续由 Gateway 转发到 Market。

## 4. 业务鉴权：Market 本地验证 Token

Market 通过 [`TokenAuthInterceptor.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-market-service/src/main/java/com/dyx/market/market/config/TokenAuthInterceptor.java) 拦截受保护路径。它会：

1. 从 `Authorization` 请求头取出 Token。
2. 验证 JWT 签名和有效期。
3. 检查 `jti` 是否在吊销名单里。
4. 从 Token 的 `openId` 取得用户身份，写入请求的 `userId` 属性。
5. 检查通过后才让请求进入 Controller。

因此，`draw_by_token` 这类接口**应使用拦截器取得的身份**，不能相信客户端在请求体里传入的 `userId`。

Market 不会在每次业务请求时远程调用 Auth 验证。**它使用相同的 JWT 密钥本地验签，并通过共享吊销存储检查 Token 状态**，少一次服务间网络调用；这要求各服务的密钥和吊销存储配置一致。

错误响应也有区别：Auth 的 `/verify` 失败时返回业务码 `0009`；Market 拦截器验证失败时返回 HTTP 401，并带鉴权错误信息。

## 5. 退出登录：吊销当前 Token

退出时，前端调用 `POST /api/v1/auth/logout`，并在 `Authorization` 请求头中提交 Token。Auth 提取 Token 的 `jti` 和过期时间，把 `jwt:revoked:{jti}` 写入吊销存储，TTL 设置到 Token 到期为止。重复吊销同一个 `jti` 是幂等的。之后 Market 请求再次检查这个 `jti` 时会拒绝该 Token。

吊销针对**当前这一个 Token**，不会同时注销这个用户的其他登录会话。部署方式决定吊销状态能否跨服务共享：
- Redis 写入失败时，服务端会报错，不会假装注销成功；Redis 查询异常时按吊销处理，拒绝该 Token。

前端退出逻辑会忽略注销请求失败，然后清除本地 Token。因此，如果服务端注销失败，浏览器看起来已经退出，但旧 Token 仍可能使用到过期。

# Market Service（市场服务）

## 一句话定位

Market 是系统的核心业务 HTTP 服务，监听 **8083**。用户请求经过 Gateway 后，在 Market 完成活动查询、抽奖、签到返利、积分兑换等业务编排。抽奖策略和返利能力仍由 Market 进程内的领域服务实现；账户额度和积分通过 Account 端口访问；抽奖后的实际发奖由 Message-Job 异步处理。

“微服务全链路串讲”中的“抽奖请求入口”会说明客户端如何经 Gateway 到达 Market；本节聚焦请求进入 Market 后的身份处理和业务编排。

## 1. Market 收到请求后的处理层次

HTTP Controller 实际定义在共享模块 `big-market-trigger` 中，由 [`MarketServiceApplication.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-market-service/src/main/java/com/dyx/market/market/MarketServiceApplication.java) 扫描启用。这样其他启动器可以复用 API 契约和适配层；Market 启动器只扫描它需要的 HTTP、RPC、应用编排、领域和基础设施组件。

以抽奖请求为例，主要调用链是：

```text
RaffleActivityController
  → 身份校验并从 Token 取得 userId
  → RaffleActivityFacade
  → RaffleDrawApplicationService
  → RaffleApplicationService
  → 活动、策略、账户与奖品相关 Port / Repository
  → 返回抽奖结果
```

Controller 负责 HTTP 参数绑定、身份入口和响应包装；Facade 统一分发用例；应用服务负责流程编排；领域服务处理活动参与、抽奖策略和奖品规则；Port/Repository 把领域操作接到本地数据库、Redis、Account RPC 或消息发布实现。

## 2. 用户身份与接口权限

用户接口从 `Authorization` Token 中取得身份。受拦截器保护的路径会先由 [`TokenAuthInterceptor.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-market-service/src/main/java/com/dyx/market/market/config/TokenAuthInterceptor.java) 本地验证签名、有效期和吊销状态，**再把 `userId` 写入请求属性**。Controller 通过 [`AuthenticatedUserSupport.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-trigger/src/main/java/com/dyx/market/trigger/support/AuthenticatedUserSupport.java) 取出该身份；需要用户身份的接口不能相信请求体里客户端传入的 `userId`。

**Market 不会为每个业务请求远程调用 Auth**；JWT 本地校验和共享吊销状态的逻辑见上文“业务鉴权：Market 本地验证 Token”。运营接口由 `OperationalAuthInterceptor` 检查管理员身份；Chat 退款内部接口**还要求服务令牌，避免把内部补偿入口直接开放给普通用户**。

抽奖入口有两道保护，执行顺序是**先限流，再检查降级**。两个开关的含义不同：

- **按用户限流**：[`RaffleDrawApplicationService.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-trigger/src/main/java/com/dyx/market/trigger/application/RaffleDrawApplicationService.java) 的 `@RateLimiterAccessInterceptor` 配置 `key = "userId"`、`permitsPerSecond = 20`。全局 `system.rateLimiterSwitch` 打开时，AOP 切面 [`RateLimiterAspect.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-starter-ratelimiter/src/main/java/com/dyx/market/starter/ratelimiter/RateLimiterAspect.java) 按已认证用户的 ID 获取进程内 Guava 限流器。用户未超过许可速率就继续；超出时调用 fallback，返回限流错误，不进入抽奖方法。限流开关关闭时跳过这项检查。开关值由 [`NacosRuntimeConfigSubscriberConfig.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-market-service/src/main/java/com/dyx/market/market/config/NacosRuntimeConfigSubscriberConfig.java) 刷新到 `RuntimeConfigHolder`。限流器保存在 Market 实例本地内存中，因此多实例之间不共享同一个用户的额度；这里的 20 是每秒许可速率，不是严格的固定秒窗口计数。
- **全局降级**：抽奖方法内部读取 `system.degradeSwitch`。该开关打开时，所有抽奖请求都会返回降级错误；关闭时才调用 `RaffleApplicationService.executeDraw()` 进入领域流程。

因此，“限流开关打开”不等于所有请求都会被拒绝：只有超过该用户限流速率的请求才会被拦截；“降级开关打开”才表示抽奖整体暂停。

## 3. 活动运营、上架与预热

运营人员可通过 ERP 接口查询活动阶段、将活动上架或设为过期。上架时 Market 先装配活动 SKU 和抽奖策略缓存，确认两者都成功后才把阶段和活动状态改为生效；下架时则把阶段设为过期并关闭活动。这样新活动不会在必要数据未装配时进入可抽奖状态。

主要入口包括：

- `POST /api/v1/raffle/erp/update_stage_activity_2_active`：按阶段记录 ID 找到活动，预热 SKU 和策略，再启用活动。
- `POST /api/v1/raffle/erp/update_stage_activity_2_expire`：将活动下架并关闭。
- `GET /api/v1/raffle/erp/query_raffle_activity_stage_list`：查看渠道、来源和活动阶段。
- `GET /api/v1/raffle/activity/armory?activityId=...`、`GET /api/v1/raffle/strategy/strategy_armory?strategyId=...`：手动预热活动或策略。
- `GET /api/v1/raffle/erp/query_user_raffle_order`：查询运营侧抽奖单。

这些运维和预热接口由 `OperationalAuthInterceptor` 检查管理员身份。上架与下架编排见 [`ErpOperateApplicationService.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-trigger/src/main/java/com/dyx/market/trigger/application/ErpOperateApplicationService.java)，活动与策略预热入口见 [`RaffleActivityFacade.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-trigger/src/main/java/com/dyx/market/trigger/application/RaffleActivityFacade.java)。

## 4. 活动展示与奖品查询

用户端先用 `GET /api/v1/raffle/activity/query_stage_activity_id?channel=...&source=...` 查询当前上架的活动，再用 `POST /api/v1/raffle/activity/query_sku_product_list_by_activity_id` 读取活动商品和可兑换额度。查询奖品列表使用 `POST /api/v1/raffle/strategy/query_raffle_award_list_by_token`，用户身份从 Token 中取得；抽奖策略和奖品列表查询由 Market 内部策略适配器处理。

相关入口是 [`RaffleActivityController.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-trigger/src/main/java/com/dyx/market/trigger/http/RaffleActivityController.java) 与 [`RaffleStrategyController.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-trigger/src/main/java/com/dyx/market/trigger/http/RaffleStrategyController.java)，查询用例由 [`RaffleActivityQueryApplicationService.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-trigger/src/main/java/com/dyx/market/trigger/application/RaffleActivityQueryApplicationService.java) 和 [`RaffleStrategyQueryApplicationService.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-trigger/src/main/java/com/dyx/market/trigger/application/RaffleStrategyQueryApplicationService.java) 承接。

## 5. 抽奖与异步发奖

以 `POST /api/v1/raffle/activity/draw_by_token` 为例：

1. **取得可信用户身份。** `RaffleActivityController` 从 Token 得到 `userId` 并覆盖请求中的用户标识，然后交给 [`RaffleActivityFacade.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-trigger/src/main/java/com/dyx/market/trigger/application/RaffleActivityFacade.java)。
2. **检查流量与运行开关。** 先由限流切面按 `userId` 检查许可速率，超限时返回限流错误；通过后进入 [`RaffleDrawApplicationService.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-trigger/src/main/java/com/dyx/market/trigger/application/RaffleDrawApplicationService.java)，再检查全局降级开关。降级开关打开时返回降级错误；两项检查都通过后才进入抽奖领域流程。
3. **创建或复用参与单。** [`RaffleApplicationService.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-domain/src/main/java/com/dyx/market/domain/activity/application/RaffleApplicationService.java) 调用 `RaffleActivityPartakeService`。它检查活动状态和起止时间；如果用户已有同一活动未使用的参与单，就复用它，避免再次扣额度；否则检查总/月/日额度并创建带有 `orderId`、`strategyId` 的参与单。
4. **扣减活动额度。** `dev`、`local`、`test` 使用进程内的 [`LocalActivityAccountPort.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-infrastructure/src/main/java/com/dyx/market/infrastructure/adapter/port/LocalActivityAccountPort.java)，在本地持久化路径处理额度和参与单。Docker 使用 [`RemoteActivityAccountPort.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-trigger/src/main/java/com/dyx/market/trigger/account/RemoteActivityAccountPort.java)，以 Dubbo 调用 Account 扣减额度，再由 Market 保存参与单；远程写入结果不确定时会记录待对账/补偿任务。
5. **执行抽奖策略。** Market 根据参与单中的策略 ID 调用本地策略实现（[`LocalStrategyDecisionPort.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-infrastructure/src/main/java/com/dyx/market/infrastructure/adapter/port/LocalStrategyDecisionPort.java)），得到奖品；如果策略预占了奖品库存，后续还需要确认预占，失败时进入补偿。
6. **同步保存中奖事实。** [`AwardService.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-domain/src/main/java/com/dyx/market/domain/award/service/AwardService.java) 构造中奖记录和 `send_award` Outbox 任务；[`AwardDispatchSupport.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-infrastructure/src/main/java/com/dyx/market/infrastructure/adapter/repository/AwardDispatchSupport.java) 在同一事务中保存中奖记录和任务，并把参与单标为已使用，避免出现“有中奖记录却没有待发消息”或订单重复使用。
7. **发布异步发奖消息并返回。** 事务提交后，Market 尝试发布 `send_award` 消息。发布成功就更新任务状态；发布失败则保留失败任务供补偿重试。HTTP 响应返回奖品 ID、标题和序号，实际发奖不要求在这次 HTTP 请求里完成。消息消费入口是 Message-Job 的 [`SendAwardConsumer.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-trigger/src/main/java/com/dyx/market/trigger/listener/SendAwardConsumer.java)。

参与单创建后，如果策略执行或中奖记录保存失败，Market 会尝试释放已预占的奖品库存，并补偿参与额度；中奖记录已经落库后则保留中奖事实，不再退还参与额度。异步消费者和重试由 Message-Job 负责，Market 不扫描 `trigger.listener` 或 `trigger.job`。中奖记录状态也不等同于积分已入账；积分奖需要继续看 Message-Job 的发奖任务和 Account 积分流水。

## 6. 日历签到返利

`POST /api/v1/raffle/activity/calendar_sign_rebate_by_token` 从 Token 取得用户 ID 后执行签到；`POST /api/v1/raffle/activity/is_calendar_sign_rebate_by_token` 查询当天是否已签到。Market 用当天日期作为业务号，先检查是否已有签到，再读取签到返利配置并创建返利订单。一次签到可以按配置产生积分或活动额度等不同类型的权益。

返利订单用“用户 ID + 返利类型 + 日期”做幂等标识；重复签到或并发重复提交会返回“今日已签到”，不会重复发放。Market 会保存返利订单和 `send_rebate` 消息任务，实际增加积分或活动额度由 Message-Job 异步处理。签到用例见 [`CalendarSignApplicationService.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-trigger/src/main/java/com/dyx/market/trigger/application/CalendarSignApplicationService.java) 和 [`BehaviorRebateService.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-domain/src/main/java/com/dyx/market/domain/rebate/service/BehaviorRebateService.java)。

## 7. 用户额度、余额与记录查询

以下接口都是 `POST /api/v1/raffle/activity/{接口名}`，需要用户身份时从 Token 取 `userId`，不接受客户端自行指定其他用户：

- `query_user_activity_account_by_token`：查询用户在活动下的总、月、日额度及剩余次数。
- `query_user_credit_account_by_token`：查询积分余额。
- `query_user_award_record_by_token`：查询中奖历史，单次最多返回 50 条。
- `query_user_credit_order_by_token`：查询积分交易流水，单次最多返回 50 条。

活动额度、积分余额和积分流水经 `IAccountReadAdapter` 读取；中奖记录由 Market 的 Award 领域查询。不同 Profile 可以使用进程内适配器或 Docker 下的 Account RPC 适配器。实现入口见 [`RaffleActivityQueryApplicationService.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-trigger/src/main/java/com/dyx/market/trigger/application/RaffleActivityQueryApplicationService.java)。

## 8. 积分兑换活动 SKU

`POST /api/v1/raffle/activity/credit_pay_exchange_sku_by_token` 用用户积分兑换活动 SKU（例如活动参与次数）。请求中的用户 ID 来自 Token，`requestId` 与用户、SKU 一起组成业务幂等号。

[`CreditPayExchangeApplicationService.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-trigger/src/main/java/com/dyx/market/trigger/application/CreditPayExchangeApplicationService.java) 按顺序创建兑换/额度订单、调用 Account 扣积分，再推进发货状态。重复扣积分会复用既有交易并继续补偿发货；明确扣费失败时恢复已预占的 SKU；远程结果不确定时保留订单和库存预占等待续作。积分已扣成功但发货状态更新失败时，不会错误地退回积分，而是交给后续补偿处理。

## 9. Chat 积分扣费与退款

Chatbot 调用 `POST /api/v1/raffle/activity/chat_credit_deduct_by_token` 扣减当前用户积分，传入 `requestId` 作为幂等 ID。Market 会先记录扣费意图，再调用 Account 扣款；重复请求不会重复扣费。明确拒绝会标记失败，远程结果不确定时保留处理中状态，供对账或补偿使用。

退款入口 `POST /api/v1/internal/raffle/activity/chat_credit_refund_by_token` 和待补偿标记接口只供内部调用：除用户 Token 外，还校验 `X-Chat-Internal-Token`。退款金额从 Market 已保存的扣费会话读取，不信任调用方传来的金额；会话状态和原始 `requestId` 用于防止重复退款。退款异常会标记待补偿，由后续任务继续处理。相关用例见 [`ChatCreditApplicationService.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-trigger/src/main/java/com/dyx/market/trigger/application/ChatCreditApplicationService.java)。

## 10. Market 与其他服务的边界

- **Market 自己负责：** 活动参与与抽奖编排、策略决策、返利订单创建、用户端业务 HTTP API、中奖记录和待发消息的持久化。
- **Account 负责：** 积分账户和活动配额。Market 通过 `IActivityAccountPort`、账户读写 Adapter 等契约调用；本地 Profile 可进程内处理，Docker Profile 通过 RPC 调用 Account Service。
- **Message-Job 负责：** 消费 `send_award`、返利等消息，执行异步发奖和后台重试任务。Market 创建消息任务并发布，不负责消费这些消息。

所以抽奖 HTTP 请求的同步部分止于“中奖事实与发奖任务已可靠记录”；后续异步消息、奖品履约和积分最终入账是跨服务闭环，详见后续 Message-Job 与 Account 章节。

# 平台配置同步（Admin / Nacos）
# 运营订单检索（Canal / ES）

# 微服务全链路串讲（学完各服务后）

这一章放在各服务章节之后，用来把入口、业务编排、账户调用和异步消息处理串起来。本笔记已记录 Gateway 到 Market 的 HTTP 入口和 Market 的同步抽奖编排；待 Account、Message-Job 等章节补齐后，再把抽奖订单、配额、中奖记录、Outbox/MQ 发奖和最终积分入账接成完整闭环。

## 抽奖请求入口：客户端 → Gateway → Market

以 POST /api/v1/raffle/activity/draw_by_token 为例：

1. **客户端发到 Gateway。** 浏览器通过统一入口的 8080 端口发送请求。Docker 内部的 Chatbot 也会通过 Gateway 调用部分 Market 积分接口。
2. **WebFlux 处理跨域。** CorsConfig 为所有路径注册 CorsWebFilter。浏览器的 CORS 预检 OPTIONS 请求可以由 Gateway 直接响应，不必进入业务服务。
3. **Gateway 选路由。** 这个请求不匹配 Auth、Admin、Chatbot 的专用路径，匹配 Path=/api/**，因此选中 Market 路由。
4. **执行 Gateway 过滤器。** Trace ID 全局过滤器保留或生成 X-Trace-Id；路由配置 CircuitBreaker。Docker 配置还给 Market 路由挂了限流器，但默认开关关闭。
5. **Gateway 代理到 Market。** 请求发往当前 profile 配置的 Market 地址，原 API 路径保留。
6. **Market 验证身份并执行业务。** 抽奖接口要求 Authorization。Market 校验 Token、取得用户身份，再进入抽奖应用逻辑。认证机制见上文“登录、鉴权与注销”。
7. **响应返回客户端。** Market 的响应经 Gateway 返回，Trace ID 会在响应头中回显；如果调用触发熔断降级，则返回 Gateway 的本地 fallback 响应。

这段只讲 HTTP 请求如何进入 Market；完整抽奖链还要继续跟到配额、抽奖结果、消息任务、Message-Job 发奖以及积分奖入账。



# 简历内容
- **活动域**负责活动状态、参与单和活动名额，也负责把抽奖步骤串起来。
“创建或复用参与单”是说：用户重复提交时，先看是否已有对应参与记录；有就复用，避免重复参与。只有新建参与单时才扣活动名额。
- **策略域**负责抽奖规则和奖品选择，比如先检查资格，再按概率挑奖品。
- **奖品域**负责中奖后要执行什么发奖动作。
- **积分域**负责积分账户和积分相关操作。