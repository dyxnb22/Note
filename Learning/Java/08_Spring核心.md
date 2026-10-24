# 08 Spring 核心：对象图、代理与事务

Spring 容器按定义创建和装配对象，代理再在调用边界加入事务、异步或审计等行为。对象是由谁取得的、方法经过哪个引用调用，比单独记住一个注解更能解释实际运行结果。本章以 Spring Framework 6.2、JDK 17 的命令式应用为例，Boot 装配与 Web 请求另见下一章。

## IoC、DI 与构造器注入

IoC 把对象创建与依赖管理交给容器，DI 则通过构造器、方法或字段将依赖交给对象。构造器注入让必要依赖明确，也便于直接构造对象测试；复杂职责仍需由业务设计划分，容器不会自动修正相互纠缠的对象图。

BeanDefinition 是创建方式、作用域等元数据，Bean 是取得的实例。典型流程是注册定义、实例化、属性填充、初始化前后处理、对外提供对象；Aware 与初始化回调分别在对应阶段执行，代理和早期引用会使实际流程出现分支，不能把容器当成单纯的类型到对象 Map。

## Bean 作用域与生命周期

singleton 是每个容器中每份 Bean 定义对应一个实例，不是某个 Java 类在 JVM 中只能有一个对象。同类可以有多个不同 Bean 定义，单例里的共享可变状态也仍需同步保护。

prototype 在每次向容器请求该 Bean 时创建新实例，不是每调用一次业务方法就创建。把它直接注入 singleton 时，依赖通常只在装配时解析一次；需要运行中反复获取，应使用 ObjectProvider 等明确获取机制。request/session 则依赖相应 Web 上下文。[Bean 作用域](https://docs.spring.io/spring-framework/reference/6.2/core/beans/factory-scopes.html)

下面是使用 spring-context 6.2 的完整示例，需要该库及其依赖；它只演示对象身份，没有外部服务。

```java
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Scope;

public class SpringScopeDemo {
    static class Token {}
    record Holder(Token token) {}

    @Configuration(proxyBeanMethods = false)
    static class Config {
        @Bean @Scope("prototype")
        Token token() { return new Token(); }
        @Bean
        Holder holder(Token token) { return new Holder(token); }
    }

    public static void main(String[] args) {
        try (var context = new AnnotationConfigApplicationContext(Config.class)) {
            Token first = context.getBean(Token.class);
            Token second = context.getBean(Token.class);
            assert first != second;
            Holder holder = context.getBean(Holder.class);
            assert context.getBean(Holder.class) == holder;
            Token injected = holder.token();
            assert holder.token() == injected;
            ObjectProvider<Token> provider = context.getBeanProvider(Token.class);
            Token third = provider.getObject();
            Token fourth = provider.getObject();
            assert third != fourth;
        }
    }
}
```

无状态服务避免把某次请求的累计值写进共享字段，但输入与依赖对象本身也需满足访问约定；局部变量引用一个共享可变 List，不会让这个 List 自动安全。计数可用相应原子 API，多字段不变量用同一同步协议，ThreadLocal 还需要生命周期与跨线程策略。

容器管理 singleton 的相应销毁回调，prototype 通常由取用方负责后续清理，不能因它来自容器就假设所有昂贵资源都会在容器关闭时自动释放。

## 循环依赖与早期引用

### 三级缓存的作用范围

普通构造器循环 A→B→A 在实例化之前就缺少必要对象，不能靠提前缓存一个尚不存在的实例解决。允许相应循环策略时，部分 singleton 的字段或 Setter 循环可在实例化后通过早期引用完成；prototype 循环等情况不适用。

| 内部缓存 | 保存的角色 |
|---|---|
| singletonObjects | 完成创建的单例对象 |
| earlySingletonObjects | 已取出的早期引用 |
| singletonFactories | 按需取得早期引用的工厂 |

这些是理解相应实现的工具，不是任意对象图都能启动的保证。Spring Boot 的循环引用默认策略与 Framework 容器本身也要区分；工程中优先拆清职责，避免在半初始化对象上调用业务方法。

### 从对象职责消除循环

若 UserService 与 RoleService 因同一权限规则互相依赖，可以将规则提取为 PermissionChecker，由两者共同依赖。若通过应用事件解除类型依赖，也要明确默认事件分发通常仍在发布线程同步执行，并不会自动变成提交后、跨进程或可靠持久的消息。

## AOP 代理与调用边界

JDK 动态代理面向接口，类代理通过子类增强，final、private 或不可覆盖的方法会限制增强范围。具体选哪一种取决于框架与配置，不能只看到类实现了接口就判断最终代理类型。

代理只处理经过代理引用的调用。对象内部 this.method 不会再次穿过同一代理；直接 new 出来的普通对象也不因方法上有注解就自动受容器增强。[Spring 代理机制](https://docs.spring.io/spring-framework/reference/6.2/core/aop/proxying.html)

### BeanPostProcessor 与代理生成

典型自动代理器通过初始化后处理包装对象；需要早期引用的循环场景，还可能经 getEarlyBeanReference 提前建立代理。最终暴露引用需要与早期使用的引用协调，因此不能一边解释三级缓存，一边又断言代理永远只能在初始化完成后出现。

初始化回调通常发生在目标对象准备阶段，不应依赖经最终代理触发的事务或异步。注解还要满足相应处理器和代理的调用条件：Spring 6 起类代理的事务方法默认还可支持 protected 与包可见方法，接口代理则要求接口中的 public 方法；不是因为扫描器“看不到非 public 方法”。[事务方法可见性](https://docs.spring.io/spring-framework/reference/6.2/data-access/transaction/declarative/annotations.html)

## 声明式事务的调用条件

本节讨论 JDBC 等命令式事务：资源通常绑定到执行线程。响应式事务另以 Reactor 上下文组织，不能把所有 Spring 事务都简化为同一个 ThreadLocal 模型。

### 自调用绕开代理

| 调用路径 | 实际事务语义 |
|---|---|
| 无事务入口直接 this 调用带注解方法 | 不会凭该内部注解新建事务 |
| 已有事务的外层方法 this 调用内部方法 | 内部数据库操作仍可参加外层事务，但内部传播、隔离等配置不会重新应用 |
| 通过另一 Bean 的事务代理调用 | 由该边界的事务属性与管理器决定加入或新建 |

常见修复是把事务边界放在被外部调用的用例方法，或拆为独立 Bean；不能把方法移到同一个类的另一个位置，就宣称已经新开事务。AspectJ 等其他织入模式有不同机制，本章不将其与代理模式混用。

### 异常被吞掉，事务拦截器收不到回滚信号

异常没有越过事务拦截边界，且事务未被其他路径标记 rollback-only 时，正常返回可能导致部分修改提交。但数据库错误、内层事务或 ORM 也可能已将资源标记回滚，不能断言“catch 后一定提交”。

先定义失败是否需要原子回滚，再选择传播异常、配置回滚规则或显式标记 rollback-only。外层 catch 住内层异常也不一定清除已有回滚标记，最终仍可能得到 UnexpectedRollbackException。

### Checked Exception 不触发默认回滚

常见默认规则对 RuntimeException、Error 回滚，受检异常需按业务配置 rollbackFor 等规则；项目还可能统一改写默认行为。受检异常不是必然提交的指令，实际还要看事务状态与资源能否提交。

### 多数据源配错事务管理器

事务管理器的默认解析受配置、类型、主候选与限定符等影响，不能统一说成只按 transactionManager 这个名称查找。多数据源时明确指定管理器，并确认它管理的是实际访问的同一资源。

```java
// 配置片段：导入 Spring JDBC、事务与依赖注入相关类型。
@Bean("orderTx")
PlatformTransactionManager orderTx(@Qualifier("orderDs") DataSource source) {
    return new DataSourceTransactionManager(source);
}

// 对应的服务方法使用：
// @Transactional(transactionManager = "orderTx")
```

### 异步线程丢失事务上下文

提交到其他线程的任务不会自动参加调用线程的命令式事务，甚至可能在原事务提交前读取旧数据。仅复制 ThreadLocal 或 MDC 也不能安全地把数据库事务搬到另一线程。

afterCommit 回调可以在本地提交后触发动作，但回调失败不会撤销已经提交的数据库事实，也存在提交后崩溃而未投递的窗口。要求可靠交付时，将业务事实与 Outbox 等待办记录写在同一本地事务，再由独立执行者投递、去重和恢复。

### 事务覆盖远程调用，持锁时间过长

事务已经取得连接或锁后，再等远端响应，会延长资源占用并放大排队。缩短事务时要保留“本地已记录、远端结果未知、结果已确认”等事实，而非只把注解删掉。

```text
CheckoutService.submit
  → OrderWriter.savePending：经过另一 Bean 的短事务代理
  → PaymentGateway.charge：事务外调用，使用业务幂等键
  → OrderWriter.recordResult：再次经过事务代理保存确认结果
未知结果 → 查询、对账或补偿，保留恢复依据
```

跨这三个阶段不再具有一个本地数据库事务的原子性，所以需要状态机和幂等来维持业务正确性。调用图清楚说明了边界，也避免“修复示例”又在同类内部自调用事务方法。

## 事务传播与数据库隔离

传播决定调用之间如何组合事务，隔离决定并发数据库事务能观察哪些现象。REQUIRES_NEW 不等于更高隔离，SERIALIZABLE 也不会自动让内部方法另开事务。

| 传播 | 资源关系 | 必须保留的后果 |
|---|---|---|
| REQUIRED | 加入已有事务或新建 | 内层回滚标记可能影响外层最终提交 |
| REQUIRES_NEW | 挂起外层，使用独立物理事务 | 可能需额外连接，内层提交不随外层回滚撤销 |
| NESTED | 在支持的同一物理事务中建立保存点 | 局部回滚依赖支持，外层最终回滚仍撤销整体 |
| SUPPORTS / NOT_SUPPORTED | 可参加已有事务 / 挂起后无事务执行 | 语义依实际上下文，不因名字自动保证一致读 |

DEFAULT 隔离沿用资源默认配置；加入已有事务时，内部声明也不一定重新改变其隔离属性。唯一约束、条件更新和版本仍负责具体业务不变量，传播设置不能替代它们。

## 容器启动中的扩展点

| 扩展点 | 修改或处理的对象 |
|---|---|
| BeanFactoryPostProcessor | Bean 定义等元数据 |
| BeanPostProcessor | 创建与初始化相应阶段的实例 |
| ApplicationContextInitializer | refresh 前的上下文 |
| ApplicationListener | 相应应用事件 |
| FactoryBean | 通过工厂提供的目标对象 |
| ImportSelector | 需导入的配置类型 |

扩展点应保留清晰的阶段、依赖与失败结果。把关键业务动作藏进隐式启动回调，会使重试、事务和运行归属难以解释；对象生命周期与一次业务用例应各有边界。
