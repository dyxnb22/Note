# 路由（`big-market-gateway`）

## 0. 这个服务里有什么？

```plain text
big-market-gateway/
├── GatewayApplication.java          启动入口
├── config/
│   ├── CorsConfig.java              跨域 WebFilter
│   └── RateLimiterConfig.java       自定义限流 Route Filter
├── filter/
│   └── TraceIdGlobalFilter.java     全局追踪 ID
└── fallback/
    └── FallbackController.java      熔断降级响应

配置：
├── application.yml                  公共配置（熔断参数、监控、限流开关）
├── application-dev.yml                本地路由表（localhost:808x）
└── application-docker.yml             Docker 路由表 + 限流
```

**网关只做对外 HTTP 入口**，不处理业务、不校验 JWT。
