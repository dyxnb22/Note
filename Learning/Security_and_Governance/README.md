# 安全、隐私与治理

这里把分散在 CS、Backend、Agent、MLOps、Web3 和 Finance 中的安全内容连接成一条跨系统路线。它不复制已有的应用安全和 Agent 安全正文，而是提供共同的判断框架、生命周期和演练入口。

## 风险处理链路

~~~text
资产与责任
  → 威胁与安全需求
  → 身份、权限与数据边界
  → 安全交付与供应链
  → 运行监控与事故响应
  → 复盘、修复与治理
~~~

## 文档地图

| 文档 | 重点 |
|---|---|
| 安全需求与威胁建模 | 资产、攻击面、信任边界和可验证控制 |
| [身份权限与秘密生命周期](./02_身份权限与秘密生命周期.md) | 人、服务、Agent、租户、权限和密钥 |
| [数据分类隐私与生命周期](./03_数据分类隐私与生命周期.md) | 最小化、用途、保留、删除、导出和审计 |
| [软件供应链与安全交付](./04_软件供应链与安全交付.md) | 依赖、构建、制品、发布和回滚 |
| [AI 系统治理与模型风险](./05_AI系统治理与模型风险.md) | 模型、数据、工具、副作用、评估和责任 |
| [事故响应与复盘](./06_事故响应与复盘.md) | 发现、遏制、恢复、证据和长期修复 |

## 现有正文的连接

- [CS 信息安全与密码学](../CS/08_信息安全与密码学.md)
- [Backend 应用安全](../Backend/Architecture/应用安全.md)
- [Agent 安全与威胁建模题](../Agent面试题库/07_可靠性与安全/可靠性与安全.md)
- [Agent 身份与数据治理题](../Agent面试题库/12_课程深化/05_身份治理与跨Agent/身份治理与跨Agent.md)
- [ML 系统与 MLOps](../AI/ML系统与MLOps.md)
- [Web3 安全](../Web3/05_Security_and_Risks/Web3安全速查.md)

## 最低证据

安全设计不能只写“已加强安全”。至少要有资产清单、威胁模型、控制措施、测试结果、日志/审计证据和残余风险。

## 怎么使用

本目录不是进入开发前必须完成的安全课程。先针对真实系统阅读 [安全需求与威胁建模](./01_安全需求与威胁建模.md)，再根据它实际拥有的身份、数据、供应链、AI 或运维风险进入对应正文。需要正式评审时，按 `资产 → 信任边界 → 威胁 → 控制 → 测试 → 残余风险` 留下一页记录；没有相关风险时不展开全部治理框架。

## 参考资料

- [OWASP Application Security Verification Standard](https://owasp.org/www-project-application-security-verification-standard/)
- [OWASP Threat Modeling](https://owasp.org/www-community/Threat_Modeling)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [CISA Secure by Design](https://www.cisa.gov/securebydesign)
