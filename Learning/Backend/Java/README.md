# Java 后端索引

本目录把语言基础、运行时、并发、框架和常用容器分开维护。

## 建议顺序

1. [Java](Java.md)：语言核心、类型、异常与基础机制。
2. [Java 集合](Java集合.md)：容器选择、复杂度与实现边界。
3. [JVM](JVM.md)：内存、类加载、GC 与诊断。
4. [JUC](JUC.md)：线程安全、锁、并发容器与线程池。
5. [设计模式](设计模式.md)：围绕变化点安排职责，不背固定模板。
6. [Spring](Spring.md)：依赖注入、AOP、事务和 Web 应用。

## 工程专题

- [Tomcat](Tomcat.md)：Servlet 容器与请求处理。
- [正则表达式](正则表达式.md)：匹配、分组、边界和性能风险。
- [调试与问题定位](调试与问题定位.md)：从现象、日志和指标收敛根因。

语言语法放本目录；跨服务可靠性和系统取舍放 [Architecture](../Architecture/README.md)，数据组件放 [Data](../Data/README.md)。
