# 网关（Gateway Service）

## 一句话定位

Gateway 是系统对外的统一 HTTP 入口，监听 **8080**，按请求路径把流量转给 Auth、Admin、Chatbot 或 Market。客户端只需使用 Gateway 地址，不必直接依赖各微服务的地址和端口；Gateway 不处理抽奖、积分等业务。

    浏览器 / 内部服务 → Gateway :8080 → Auth / Admin / Chatbot / Market

## 1. 技术栈与运行配置

入口类 GatewayApplication 启动 Spring Boot。模块使用 Spring Cloud Gateway 和 WebFlux，并集成 Reactor Resilience4j、Actuator 和 Prometheus。

Gateway 基于 **WebFlux 响应式栈**，用 Mono 和过滤器链异步处理请求，适合以网络 I/O 转发为主的场景。不要添加 spring-boot-starter-web，避免把 Spring MVC/Servlet 栈混入这个响应式网关。

| Profile | 用途 | 下游地址 |
|---|---|---|
| dev（默认） | 本地开发 | localhost:8081–8084 |
| docker | Docker Compose | Docker 网络中的服务名 |
| secure | 安全配置覆盖层 | 收紧 CORS 来源并启用限流 |

本地默认激活 dev；Compose 激活 docker。路由由 YAML 静态配置，目标是固定 host/port；当前没有使用 lb:// 地址或 Nacos 动态发现 Gateway 路由。

## 2. 路由规则

每条路由有四个要素：

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

Path 中单星号匹配一个路径片段，双星号匹配后续路径。Auth、Admin、Chatbot 是专用规则；其余以 /api/ 开头的请求由 Market 兜底。例如，POST /api/v1/auth/login 到 Auth，POST /api/v1/raffle/activity/draw_by_token 到 Market。

路由没有配置 StripPrefix 或 RewritePath，因此不会显式改写请求路径；Market 会收到完整 API 路径。路径不匹配任何 Route 时，Gateway 没有下游目标，不会自动转给业务服务。

## 3. 过滤器类型

- **WebFilter**：WebFlux Web 层过滤器。本项目用 CorsWebFilter 处理 CORS。
- **GlobalFilter**：Gateway 路由链的全局过滤器。本项目的 TraceIdGlobalFilter 实现了 GlobalFilter 和 Ordered。
- **GatewayFilter**：绑定到具体 Route。本项目每条路由都配置 CircuitBreaker；Docker 的 Auth 和 Market 路由还配置了 IpPathRateLimit。

面试区分点：Predicate 决定“请求是否走这条路由”；Filter 决定“选中路由后请求如何处理”。GlobalFilter 面向 Gateway 路由链，GatewayFilter 由具体路由配置。

## 4. Trace ID

TraceIdGlobalFilter 读取 X-Trace-Id：请求已有就沿用，没有就生成 UUID。它把 ID 传给下游，并在响应提交前写回响应头，便于按同一个 ID 关联网关和下游日志。Trace ID 是日志关联标识，不是身份凭证。

## 5. CORS

默认允许来源为 *，允许所有方法和请求头，但 allowCredentials=false，也就是不允许跨域携带凭证。secure profile 默认把来源收紧为 http://127.0.0.1:5173，可用 APP_CORS_ALLOWED_ORIGINS 覆盖。

浏览器的 CORS 预检 OPTIONS 请求可由 Gateway 直接响应；如果前端与 API 经同源反向代理提供，浏览器通常不会触发跨域检查。

## 6. 熔断与降级

每条服务路由使用独立的 Resilience4j CircuitBreaker 实例：auth-cb、admin-cb、chatbot-cb、market-cb。当前配置为：

| 配置项 | 值 |
|---|---:|
| 滑动窗口大小 | 10 |
| 失败率阈值 | 50% |
| 打开状态等待时间 | 10 秒 |
| 半开状态试探请求数 | 3 |
| TimeLimiter 默认超时 | 30 秒 |

熔断器有三个状态：Closed 正常放行并统计结果；Open 快速失败，避免继续压向故障下游；Half-open 在等待后放少量探测请求，判断下游是否恢复。

熔断 fallback 使用 forward:/fallback/{service}，是在 Gateway 应用内转到 FallbackController，不会再发起网络请求。它返回 HTTP 503 和统一错误体：code=0007、info=网关接口调用失败、data=null。当前配置了熔断和 fallback，没有配置 Gateway Retry；熔断不是重试，也不能保证业务成功。

## 7. 限流

自定义 IpPathRateLimit 使用内存令牌桶：桶初始容量由 burstCapacity 决定，每个请求消耗一个令牌，再按 replenishRate 个/秒补充；没有令牌时返回 HTTP 429，不再转发下游。

当前配置有几个面试要点：

- 限流开关默认关闭；secure profile 会打开。Compose 默认只激活 docker，所以默认 Compose 下过滤器虽然挂在路由上，仍会直接放行。
- Docker 的 Auth 和 Market 路由挂了该过滤器，默认补充速率为每秒 20 个、桶容量为 40，可由 GATEWAY_RATE_LIMITER_REPLENISH 和 GATEWAY_RATE_LIMITER_BURST 覆盖；Admin 和 Chatbot 没挂。
- application.yml 还声明了 100/200 的通用默认值，但 Docker 路由直接给过滤器传 20/40 默认值；不要把 100/200 当成当前 Docker 路由的有效默认值。
- 限流 key 是 socket 对端 IP 加路径前缀。代码只取路径前两个非空片段，所以 /api/v1/raffle/... 和 /api/v1/auth/... 的路径 key 都是 /api/v1；同一 IP 的 Auth、Market 请求会共用这个版本级桶。
- 桶保存在当前 Gateway JVM 内存中，实例之间不共享，重启后状态重置。它不是分布式限流；经过反向代理时还要确认 getRemoteAddress() 取到的是代理 IP 还是客户端 IP。

## 8. 认证边界：Gateway 不验证 JWT

请求经过 Gateway 不代表 JWT 已在 Gateway 验证。当前 Gateway 没有读取 Authorization 的过滤器或 JWT 校验逻辑，它负责路由并透传请求头。

/api/v1/auth/login、verify、logout 路由到 Auth，由 Auth 处理账号验证和 Token 生命周期。Market 的受保护接口由 Market 认证拦截器验证 Token 并取得用户身份。

application-secure.yml 虽然配置了 app.jwt.secret，但配置密钥不等于实现了 JWT 校验。面试时可以概括为：**Gateway 负责路由，Auth 管理 Token，业务服务校验访问身份。**

## 9. 运维与观测

Gateway 暴露 Actuator 的 health、info、circuitbreakers 和 prometheus 端点，并启用 Prometheus 指标导出。Compose 健康检查访问 /actuator/health。

## 10. 面试时的一分钟介绍

> 这个项目的 Gateway 基于 Spring Cloud Gateway 和 WebFlux，监听 8080，按路径把请求转给 Auth、Admin、Chatbot 或 Market。路由是 YAML 静态配置，本地指向 localhost，Docker 指向容器名。网关提供 Trace ID 透传、CORS、Resilience4j 熔断和 fallback；Docker 中 Auth、Market 还配置了内存令牌桶限流，但默认开关关闭。Gateway 不校验 JWT，Auth 管理 Token，Market 等业务服务验证访问身份。当前限流不在多实例间共享。

## 11. 常见追问速记

**问：Predicate 和 Filter 有什么区别？**  
Predicate 负责匹配 Route；Filter 在路由选中后处理请求或响应。

**问：GlobalFilter 和 GatewayFilter 有什么区别？**  
GlobalFilter 加入 Gateway 路由过滤器链；GatewayFilter 由具体 Route 配置。本项目 Trace ID 使用 GlobalFilter，限流使用路由级 GatewayFilter。

**问：下游服务故障时怎么办？**  
CircuitBreaker 根据调用结果打开熔断，路由 fallback 转到本地 Controller 返回 503；它不是重试。

**问：Gateway 是否验证 JWT？**  
不验证。Gateway 路由并透传 Authorization；Auth 管理 Token，Market 对受保护业务请求验证身份。

**问：当前限流能覆盖多个 Gateway 实例吗？**  
不能。桶在各实例的 JVM 内存中；要做跨实例统一限流，需要共享状态或分布式限流方案。

# 登录、鉴权与注销

## 1. 登录：账号密码换成 JWT

前端登录页通过 `loginWithPassword` 发送 `POST /api/v1/auth/login`，请求经过 Gateway 转发到 Auth 服务，入口是 [`AuthAccessController.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-auth-service/src/main/java/com/dyx/market/auth/AuthAccessController.java)。

Auth 将登录交给 `LoginApplicationService`：它从 MySQL 的 `big_market.auth_user` 表读取账号，检查账号是否启用，再用 Argon2id 校验输入密码和表中保存的密码哈希。未知账号、密码错误或账号已禁用，都会返回相同的登录错误，业务码为 `0009`。

本地和验收环境通过 `app.auth.seed-users` 配置演示账号。Auth 启动时，`AuthUserSeedRunner` 会把配置中的账号密码用 Argon2id 哈希后写入或更新 `auth_user` 表；登录时始终查数据库。开发环境默认示例账号是 `xiaofuge/demo` 和 `admin/admin`。这个项目没有注册、找回密码或外部身份提供商流程。

密码校验通过后，`LoginApplicationService` 调用 `AuthService` 签发 JWT。有效期是 24 小时（`expiresIn = 86400` 秒）。Token 包含：

- `openId`：用户标识
- `jti`：Token 唯一 ID
- `iat`、`exp`：签发时间和过期时间
- `sub`（subject）：签发对象，这里也使用用户标识

JWT 使用共享密钥做 HS256 签名，用于验证 Token 是否被篡改；JWT 本身没有加密，载荷可以被解码读取。

登录响应包含 `userId`、JWT 和有效期。前端将 Token 和 `userId` 存入 `sessionStorage`；后续 API 请求会在 `Authorization` 请求头中携带 Token。相关实现见 [`LoginApplicationService.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-auth-service/src/main/java/com/dyx/market/auth/login/LoginApplicationService.java)、[`AuthUserSeedRunner.java`](/Users/diaoyuxuan/big-market-ai-platform/big-market-auth-service/src/main/java/com/dyx/market/auth/user/AuthUserSeedRunner.java) 和 [`api-client.js`](/Users/diaoyuxuan/big-market-ai-platform/big-market-web/api-client.js)。

## 2. 鉴权：Market 自己验证 Token

用户进入页面时，前端会调用 `/api/v1/auth/verify` 检查已有 Token。真正调用抽奖、签到等受保护接口时，Gateway 把请求转给 Market。

Market 通过 [TokenAuthInterceptor.java](/Users/diaoyuxuan/big-market-ai-platform/big-market-market-service/src/main/java/com/dyx/market/market/config/TokenAuthInterceptor.java) 拦截受保护路径。它会：

1. 验证 JWT 签名和有效期。
2. 检查 `jti` 是否在吊销名单里。
3. 从 token 的 `openId` 取用户身份，写入请求的 `userId` 属性。
4. 只有通过检查，才让请求进入 Controller。

因此，`draw_by_token` 这类接口应使用拦截器取得的身份，不能相信客户端自己在请求体里传的 `userId`。

**Market 不会每次都远程调用 Auth 服务验证。** 它用相同的 JWT 密钥本地验签，并通过共享 Redis 检查吊销状态。这样少了一次服务间网络调用，但要求各服务的密钥和吊销存储配置一致。

错误响应也有两种表现：Auth 的 `/verify` 返回业务码 `0009`；Market 拦截器验证失败会返回 HTTP 401，并带鉴权错误信息。

## 3. 注销：吊销一个具体的 Token

退出时，前端调用 `/api/v1/auth/logout`。Auth 解析这个 Token 的 `jti` 和过期时间，把 `jwt:revoked:{jti}` 写进吊销存储，TTL 设置到 Token 到期为止。重复吊销同一个 Token 是幂等的。

后续 Market 请求再次检查这个 `jti` 时会拒绝它。这里吊销的是**当前这一个 Token**，不是把这个用户所有登录会话都注销。

部署方式会影响注销效果：

- 启用 Redis 时，Auth 和 Market 共用吊销名单，跨服务生效。
- 未启用 Redis 的本地单进程模式使用进程内 Map；Auth 和 Market 各自运行时，名单不会自动共享。

还有一个前端细节：退出逻辑会忽略注销请求失败，然后清除本地 Token。所以如果服务端注销失败，浏览器看起来已经退出，但旧 Token 可能仍能使用到过期。服务端 Redis 写入失败时会报错，不会假装注销成功。
# 抽奖和异步发奖（核心主流程）
# 签到返利
# 积分兑换抽奖次数
# Chat 积分扣费与退款
# 活动配置、上架与策略预热
# 平台配置同步（Admin / Nacos）
# 运营订单检索（Canal / ES）

# 微服务全链路串讲（学完各服务后）

这一章放在各服务章节之后，用来把入口、业务编排、账户调用和异步消息处理串起来。目前先记录抽奖请求的 HTTP 入口段；等 Market、Account、Message-Job 等章节补齐后，再把抽奖订单、配额、中奖记录、Outbox/MQ 发奖和最终积分入账接成完整闭环。

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
