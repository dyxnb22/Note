# Spring 核心

Spring Core 解决对象的创建、依赖装配、生命周期和横切能力。Spring MVC、Boot、MyBatis 和 Cloud 都建立在这些基础之上。

## IoC 与 DI

IoC 是把对象创建和依赖管理从业务代码交给容器；DI 是容器把依赖传给对象的实现方式。优先使用构造器注入，因为依赖显式、对象可保持完整状态，也便于单元测试。

容器的核心流程可以概括为：

```text
读取配置与扫描
→ 注册 BeanDefinition
→ 实例化
→ 属性填充
→ Aware 回调
→ BeanPostProcessor 前置处理
→ 初始化
→ BeanPostProcessor 后置处理/生成代理
→ 对外提供 Bean
→ 容器关闭时执行销毁回调
```

BeanDefinition 是“如何创建对象”的元数据，Bean 是创建完成的实例。不要把容器理解成一个普通 `Map<Class, Object>`：它还要处理作用域、生命周期、代理、扩展点和依赖关系。

## Bean 作用域与生命周期

常见作用域包括 singleton、prototype、request 和 session。Spring singleton 是“每个容器一个实例”，不是 JVM 全局单例；单例 Bean 仍需自行保证可变状态的线程安全。

prototype Bean 的创建由容器负责，但完整销毁通常由调用方负责。Web 作用域依赖请求上下文，不能在普通线程中随意使用。

## 循环依赖

循环依赖暴露了对象职责互相纠缠。Spring 对部分单例、Setter/字段注入的循环依赖可以通过提前暴露引用解决，但构造器循环依赖无法靠三级缓存绕过。

三级缓存的意义不只是“提前放一个对象”，还要保证其他 Bean 取得的早期引用与最终 AOP 代理保持一致。工程上优先通过拆分职责、引入领域事件或中间服务消除循环，而不是依赖容器兜底。

## AOP 与代理

AOP 把日志、事务、鉴权、指标等横切逻辑织入业务方法。Spring AOP 主要基于运行时代理：

| 方式 | 特点 | 典型限制 |
| --- | --- | --- |
| JDK 动态代理 | 基于接口 | 调用方通常面向接口 |
| CGLIB | 生成目标类子类 | `final` 类或方法不能被覆盖增强 |

代理只拦截“经过代理对象”的调用。对象内部 `this.method()` 通常不会再次经过代理，因此 `@Transactional`、`@Async`、`@Cacheable` 等都可能失效。

## 声明式事务

声明式事务由代理在方法前后打开、提交或回滚事务。重点不是记注解参数，而是确认：

- 方法是否通过 Spring 代理调用。
- 异常是否传播到事务拦截器，回滚规则是否匹配。
- 多个数据源使用的是哪个事务管理器。
- 异步线程是否已经离开原事务上下文。
- 事务是否覆盖远程调用，导致持锁时间过长。
- 自调用、非公开方法和对象手动 `new` 是否绕开代理。

数据库事务只能保证本地资源，不能直接保证消息和远程服务的一致性；跨边界方案见 [可靠性与一致性](../Architecture/04_可靠性与一致性.md)。

## 常用扩展点

| 扩展点 | 适用场景 |
| --- | --- |
| `BeanFactoryPostProcessor` | Bean 实例化前修改定义元数据 |
| `BeanPostProcessor` | Bean 初始化前后包装或增强实例 |
| `ApplicationContextInitializer` | 容器刷新前调整上下文 |
| `ApplicationListener` | 监听应用事件 |
| `FactoryBean` | 用复杂逻辑创建特定对象 |
| `ImportSelector` | 按条件导入配置，常用于自动装配 |

扩展点要有清晰的执行顺序和失败策略，避免把关键业务逻辑藏在隐式生命周期回调里。

## 复习检查

- IoC、DI、BeanDefinition 和 Bean 分别是什么？
- BeanPostProcessor 为什么能生成 AOP 代理？
- 构造器循环依赖为什么不能用三级缓存解决？
- `this` 调用为什么绕过声明式事务？
- 单例 Bean 为什么仍可能有线程安全问题？
