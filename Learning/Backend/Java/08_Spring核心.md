
## IoC 和 DI 分别是什么，为什么优先使用构造器注入？

IoC 是把对象创建和依赖管理**从业务代码交给容器**；DI 是容器把依赖传给对象的**实现方式**。优先使用**构造器注入**，因为依赖显式、对象可保持完整状态，也便于单元测试。

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

BeanDefinition 是“如何创建对象”的元数据，Bean 是创建完成的实例。不要把容器理解成一个普通 `Map<Class, Object>`：它还要处理**作用域、生命周期、代理、扩展点和依赖关系**。

## Spring Bean 的作用域和生命周期如何理解？

常见作用域包括 singleton、prototype、request 和 session。Spring singleton 是"每个容器一个实例"，不是 JVM 全局单例；单例 Bean 仍需自行保证可变状态的线程安全。

### 单例 Bean 为什么仍可能有线程安全问题？

Spring 容器对每个 Bean 只创建一个实例，但**线程安全不由容器保证**。多线程并发访问同一个对象，如果对象内部有可变状态（成员变量被修改），就会出现数据竞争。

```java
@Service  // 默认 singleton
public class CounterService {
    private int count = 0;        // 可变状态，所有线程共享

    public int increment() {
        return ++count;           // 非原子操作，线程不安全
    }
}

// 三个线程各调用 1000 次，结果可能 < 3000
```

常见修复策略：

| 策略 | 适用场景 | 示例 |
|------|---------|------|
| **无状态设计** | 最佳方案，去掉成员变量 | 方法内用局部变量，依赖注入的都是无状态 Bean |
| `@Scope("prototype")` | 每次调用创建新实例 | 有状态的计算器、上下文对象 |
| `ThreadLocal` | 线程隔离，如用户上下文 | `UserContext.get()` |
| `synchronized` / 锁 | 低并发简单场景 | 计数器、缓存同步 |
| 并发容器 | 集合类共享状态 | `ConcurrentHashMap`、`AtomicLong` |

```java
// 无状态设计：每次调用都返回新结果，不修改成员变量
@Service
public class OrderCalculator {
    public BigDecimal calculateTotal(List<Item> items) {
        return items.stream()       // 局部变量，无线程问题
            .map(Item::getPrice)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
    }
}
```

prototype Bean 的创建由容器负责，但完整销毁通常由调用方负责。Web 作用域依赖请求上下文，不能在普通线程中随意使用。

## Spring 循环依赖为什么会发生，三级缓存能解决什么？

**循环依赖**暴露了对象职责互相纠缠。Spring 对部分单例、Setter/字段注入的循环依赖可以通过**提前暴露引用解决**，但**构造器循环依赖无法靠三级缓存绕过**。

### 三级缓存解决的是什么问题？

Spring 创建单例 Bean 时有三级缓存：

| 缓存 | 作用 |
|------|------|
| `singletonObjects` (一级) | 完全初始化好的 Bean |
| `earlySingletonObjects` (二级) | 提前暴露的早期引用（可能是代理） |
| `singletonFactories` (三级) | Bean 工厂，用于生成早期引用 |

Setter 注入的循环依赖能解决，关键在于**对象可以先半成品创建**：

```java
@Service
public class A {
    @Autowired private B b;      // A 先创建，b 字段先空着
    // 容器把 A 的引用提前暴露到三级缓存
}

@Service
public class B {
    @Autowired private A a;      // B 创建时从缓存拿到 A 的早期引用
    // B 创建完成后，A 再注入 b
}
```

流程：`创建 A → 实例化后放入三级缓存 → 填充属性时发现需要 B → 创建 B → B 从缓存拿到 A → B 完成 → A 注入 B → A 完成`

### 为什么构造器循环依赖无法解决？

构造器注入要求**实例化时就必须提供所有依赖**——对象还没创建出来，没有引用可以暴露给缓存。

```java
@Service
public class A {
    public A(B b) {  // 创建 A 需要 B，但 A 还没实例化完成
        this.b = b;  // 没有半成品可以暴露
    }
}

@Service
public class B {
    public B(A a) {  // 创建 B 需要 A，同样卡住
        this.a = a;
    }
}

// 容器启动时直接报错：
// BeanCurrentlyInCreationException:
// Requested bean is currently in creation: Is there an
// unresolvable circular reference?
```

本质矛盾：**构造器语义要求对象创建即完整，而缓存机制依赖"先给引用再补属性"**。二者不可兼得。

### 工程上怎么解决？

优先**消除循环**，而不是依赖容器兜底：

```java
// 方案一：抽取公共逻辑到第三个 Bean
@Service
public class PermissionChecker {
    public boolean check(User user, Resource resource) { /* ... */ }
}

@Service
public class UserService {
    @Autowired private PermissionChecker checker;  // 不再依赖 RoleService
}

@Service
public class RoleService {
    @Autowired private PermissionChecker checker;  // 不再依赖 UserService
}
```

```java
// 方案二：用事件解耦
@Service
public class OrderService {
    @Autowired private ApplicationEventPublisher publisher;

    public void createOrder(OrderDTO dto) {
        // ... 创建订单
        publisher.publishEvent(new OrderCreatedEvent(dto.getId()));
    }
}

@Component
public class InventoryListener {
    @EventListener
    public void onOrderCreated(OrderCreatedEvent event) {
        // 扣库存，不再直接依赖 OrderService
    }
}
```

三级缓存的意义不只是“提前放一个对象”，**还要保证其他 Bean 取得的早期引用与最终 AOP 代理保持一致**。工程上优先通过拆分职责、引入领域事件或中间服务消除循环，而不是依赖容器兜底。

## Spring AOP 如何通过代理实现，哪些调用会失效？

AOP 把**日志、事务、鉴权、指标**等横切逻辑织入业务方法。Spring AOP 主要基于运行时代理：

| 方式       | 特点      | 典型限制                |
| -------- | ------- | ------------------- |
| JDK 动态代理 | 基于接口    | 调用方通常面向接口           |
| CGLIB    | 生成目标类子类 | `final` 类或方法不能被覆盖增强 |

代理只拦截“经过代理对象”的调用。对象内部 `this.method()` 通常不会再次经过代理，因此 `@Transactional`、`@Async`、`@Cacheable` 等都可能失效。

### BeanPostProcessor 为什么能生成 AOP 代理？

AOP 代理不是在 Bean 实例化时就生成的，而是在**初始化阶段**由 `BeanPostProcessor` 拦截并包装的。

Spring 容器启动时会注册一系列 `BeanPostProcessor`，其中 `AbstractAutoProxyCreator` 负责 AOP 代理。它的工作时机是在 Bean 初始化完成之后（`init-method` 执行完、`@PostConstruct` 调用完）：

```java
// 简化后的流程
Object bean = instantiateBean(bd);           // 1. 反射创建原始对象
bean = initializeBean(bean, beanName, bd);   // 2. 属性填充、Aware、初始化
// ↓ 在 initializeBean 内部 ↓
for (BeanPostProcessor processor : processors) {
    Object result = processor.postProcessAfterInitialization(bean, beanName);
    if (result != bean) {
        bean = result;  // 3. AbstractAutoProxyCreator 在这里返回代理对象
    }
}
```

`AbstractAutoProxyCreator` 的判断逻辑：

```java
public Object postProcessAfterInitialization(Object bean, String beanName) {
    if (bean != null) {
        // 检查是否需要代理（有没有匹配的 Advisor/切面）
        Object[] specificInterceptors = getAdvicesAndAdvisorsForBean(bean.getClass(), beanName, null);
        if (specificInterceptors != DO_NOT_PROXY) {
            // 创建代理并返回，容器后续使用的都是这个代理
            Object proxy = createProxy(bean.getClass(), beanName, specificInterceptors, new SingletonTargetSource(bean));
            return proxy;
        }
    }
    return bean;  // 不需要代理，返回原始对象
}
```

所以 BeanPostProcessor 能生成代理的关键在于：**它在初始化完成后介入，用代理对象替换原始对象**。容器后续拿到的 Bean 引用已经是代理了，调用方完全无感知。

这也解释了为什么 `@Async`、`@Transactional` 等注解要放在**公开方法**上——它们需要被 `BeanPostProcessor` 扫描到才能生成对应的代理逻辑。

## Spring 声明式事务为什么会失效，边界如何设计？

声明式事务由代理在方法前后打开、提交或回滚事务。重点不是记注解参数，而是确认以下六种常见失效场景。

### 1. 自调用绕开代理

同类内部方法调用走的是 `this.method()`，**不经过代理对象**，`@Transactional` 完全失效。

```java
@Service
public class OrderService {
    public void createOrder(OrderDTO dto) {
        this.saveOrder(dto);       // this 调用，事务不生效
        this.sendNotification(dto);
    }

    @Transactional
    public void saveOrder(OrderDTO dto) { /* ... */ }
}

// 修复方式一：抽取到另一个 Bean
@Service
public class OrderPersistence {
    @Transactional
    public void save(OrderDTO dto) { /* ... */ }
}

// 修复方式二：**注入自身代理**
@Autowired @Lazy
private self;  // 注入的是代理对象
public void createOrder(OrderDTO dto) {
    self.saveOrder(dto);           // 走代理，事务生效
}
```

### 2. 异常被吞掉，事务拦截器收不到回滚信号

`try-catch` 吞掉**异常后**，拦截器认为方法正常完成，直接提交——**即使数据库已经部分写入。**

```java
@Transactional
public void transfer(Long from, Long to, BigDecimal amount) {
    try {
        accountDao.deduct(from, amount);
        accountDao.add(to, amount);
    } catch (Exception e) {
        log.error("转账失败", e);    // 吞掉了，事务不会回滚
    }
}

// 修复：让异常传播，或手动标记回滚
@Transactional
public void transfer(Long from, Long to, BigDecimal amount) {
    try {
        accountDao.deduct(from, amount);
        accountDao.add(to, amount);
    } catch (Exception e) {
        log.error("转账失败", e);
        TransactionAspectSupport.currentTransactionStatus().setRollbackOnly();
        // 或者直接 throw，不要 catch
    }
}
```

### 3. Checked Exception 不触发默认回滚

Spring 默认只对 `RuntimeException` 和 `Error` 回滚，**checked Exception（如 `IOException`）会直接提交**。

```java
@Transactional
public void importData(File file) throws IOException {
    validate(file);       // 抛 IOException → 事务提交，不回滚
    bulkInsert(file);
}

// 修复：指定回滚规则
@Transactional(rollbackFor = Exception.class)
public void importData(File file) throws IOException { /* ... */ }
```

### 4. 多数据源配错事务管理器

`@Transactional` 默认按名称查找 `transactionManager`，多数据源时容易**指向错误的管理器**。

```java
@Bean("orderTx")
public PlatformTransactionManager orderTx(DataSource orderDs) {
    return new DataSourceTransactionManager(orderDs);
}

@Service
public class OrderService {
    @Transactional("orderTx")        // 必须显式指定，否则用默认的
    public void create() { /* ... */ }
}
```

### 5. 异步线程丢失事务上下文

`TransactionSynchronizationManager` 基于 `ThreadLocal` 绑定，**新线程拿不到原事务**。

```java
@Transactional
public void process() {
    orderDao.save(order);
    executor.submit(() -> {
        // 这里没有事务，order 可能还没提交
        notificationService.send(order.getId());
    });
}

// 修复：把事务内的结果带出去，异步操作放在事务提交后
@Transactional
public void process() {
    orderDao.save(order);
    // 在事务同步回调中执行，保证提交后才跑
    TransactionSynchronizationManager.registerSynchronization(
        new TransactionSynchronization() {
            @Override
            public void afterCommit() {
                notificationService.send(order.getId());
            }
        });
}
```

### 6. 事务覆盖远程调用，持锁时间过长

事务内做 HTTP/RPC 调用，**数据库连接一直被占着**，锁等待时间随网络延迟线性增长。

```java
@Transactional
public void submit(OrderDTO dto) {
    orderDao.save(dto);             // 拿到连接，开始持锁
    paymentGateway.charge(dto);     // 网络调用 2s，连接空等
    orderDao.markPaid(dto.getId()); // 还在事务内
}

// 修复：远程调用放在事务外
public void submit(OrderDTO dto) {
    orderDao.save(dto);             // 短事务，快速释放连接
    paymentGateway.charge(dto);     // 事务外调用
    markPaidInTransaction(dto.getId()); // 新开事务处理结果
}

@Transactional
public void markPaidInTransaction(Long id) {
    orderDao.markPaid(id);
}
```

### 设计原则

- 事务尽量**短小**：只包含数据库操作，不掺杂远程调用和文件 I/O。
- 异常**不要吞**：catch 之后要么 rethrow，要么手动 `setRollbackOnly`。
- 多数据源**显式指定**事务管理器名称。
- 数据库事务只能保证本地资源，不能直接保证消息和远程服务的一致性——跨服务一致性用**本地事务表、事务消息或 Saga** 解决。

## Spring 事务传播和数据库隔离级别分别解决什么问题？

核心回答：**传播行为解决“一个带事务的方法调用另一个事务方法时如何组合”**，**隔离级别解决“多个数据库事务并发时能看到什么”**。二者不在同一层，`REQUIRES_NEW` 不能替代更高隔离级别，`SERIALIZABLE` 也不能自动决定内部方法是否新开事务。

高频传播行为：

| 行为                           | 语义                 | 主要边界                                                                 |
| ---------------------------- | ------------------ | -------------------------------------------------------------------- |
| `REQUIRED`                   | 有事务就加入，**没有就新建**   | 内层标记 rollback-only 后，外层即使捕获异常也可能在提交时得到 `UnexpectedRollbackException` |
| `REQUIRES_NEW`               | 挂起外层，**开启独立物理事务**  | 需要额外连接；内层提交后外层回滚也撤不回内层效果                                             |
| `NESTED`                     | **同一物理事务内建立保存点**   | 依赖事务管理器和数据库保存点支持；外层最终回滚仍会撤销全部                                        |
| `SUPPORTS` / `NOT_SUPPORTED` | 可加入事务 / 挂起事务后无事务执行 | 适合明确的只读或非事务边界，不能凭名称假设一致性                                             |

隔离级别应从**脏读、不可重复读、幻读和写冲突**的业务风险出发，`DEFAULT` 表示沿用数据库默认值。即使使用较高隔离，也要通过唯一约束、条件更新、版本号或显式锁保护业务不变量；长事务和外部 RPC 会放大锁等待与连接池占用。

自调用失效的首选修复是拆分 Bean，让调用真正经过代理，或把事务边界上移到公开用例方法；不建议为了绕过设计问题普遍使用 `AopContext.currentProxy()`。测试至少覆盖代理类型、回滚规则、内外层组合、连接池容量和并发冲突。

## Spring 常用扩展点分别在什么时候执行？

| 扩展点                             | 适用场景              |
| ------------------------------- | ----------------- |
| `BeanFactoryPostProcessor`      | Bean 实例化前修改定义元数据  |
| `BeanPostProcessor`             | Bean 初始化前后包装或增强实例 |
| `ApplicationContextInitializer` | 容器刷新前调整上下文        |
| `ApplicationListener`           | 监听应用事件            |
| `FactoryBean`                   | 用复杂逻辑创建特定对象       |
| `ImportSelector`                | 按条件导入配置，常用于自动装配   |

扩展点要有清晰的执行顺序和失败策略，避免把关键业务逻辑藏在隐式生命周期回调里。

## 如何验收 Spring Core 基础？

- IoC、DI、BeanDefinition 和 Bean 分别是什么？
- BeanPostProcessor 为什么能生成 AOP 代理？
- 构造器循环依赖为什么不能用三级缓存解决？
- `this` 调用为什么绕过声明式事务？
- 单例 Bean 为什么仍可能有线程安全问题？
