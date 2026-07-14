# Spring

Spring 的核心价值是用 IoC 降低对象创建和依赖管理的耦合，用 AOP 统一处理事务、日志、权限等横切逻辑，并在此基础上提供事务管理、MVC、数据访问等企业开发能力。

## Spring 的核心思想

| 核心思想 | 解决的问题                                       | 实现手段                                    | 典型场景                                  |
| -------- | ------------------------------------------------ | ------------------------------------------- | ----------------------------------------- |
| IoC      | 对象创建、依赖组装和生命周期管理与业务代码强耦合 | BeanFactory / ApplicationContext 管理 Bean  | Service、DAO、配置类统一交给容器管理      |
| DI       | 类内部硬编码 `new` 依赖，难测试、难替换            | 构造器、Setter、字段注入                    | 注入 Repository、DataSource、第三方客户端 |
| AOP      | 事务、日志、权限等横切逻辑散落在业务代码中       | JDK 动态代理 / CGLIB 代理 + 切面            | 声明式事务、接口鉴权、操作日志            |
| 事务管理 | 事务 API 和业务代码耦合，跨数据访问技术不统一    | `PlatformTransactionManager` + `@Transactional` | Service 层保证一组数据库操作原子性     |

一句话：IoC 管对象，DI 管依赖怎么进来，AOP 管公共逻辑怎么切进去，事务管理是 AOP 最典型的落地场景。

## IoC 和 DI 是什么？

IoC 即控制反转，反转的是对象控制权：以前由业务代码主动 `new` 对象、初始化依赖、管理销毁；使用 Spring 后，由容器负责 Bean 的创建、依赖注入、初始化和销毁，业务对象只声明自己需要什么。

DI 是 IoC 最常见的实现方式，指依赖对象由外部容器创建并注入，而不是类自己创建。

常见注入方式：

| 方式       | 特点                                           | 面试建议               |
| ---------- | ---------------------------------------------- | ---------------------- |
| 构造器注入 | 依赖不可变，创建对象时依赖完整，便于测试       | 推荐用于必需依赖       |
| Setter 注入 | 可选依赖更灵活，但对象可能存在未完全初始化状态 | 适合可选配置           |
| 字段注入   | 写法简洁，但隐藏依赖，不利于测试和不可变设计   | 不推荐作为生产代码首选 |

IoC 的底层能力主要包括：

- 反射：运行时创建对象、调用构造器和方法、访问字段。
- 工厂模式：BeanFactory / ApplicationContext 作为 Bean 创建和管理工厂。
- BeanDefinition：保存 Bean 的类名、作用域、依赖、初始化方法等元信息。
- 依赖注入：根据类型、名称、构造器参数等规则完成依赖装配。
- 生命周期管理：统一处理实例化、属性填充、初始化、销毁和扩展点。

依赖倒置原则和 IoC 的关系：高层模块不直接依赖低层实现，而是依赖抽象；IoC 容器负责把具体实现注入到抽象依赖中。

## 如何设计一个 IoC 容器？

- Bean 定义模型：用 BeanDefinition 描述类、作用域、构造参数、属性依赖、初始化和销毁方法。
- 配置来源：支持 XML、注解、Java Config 等方式加载 BeanDefinition。
- Bean 创建：通过反射、工厂方法或 FactoryBean 创建实例。
- 依赖注入：支持构造器、Setter、字段注入，并处理依赖查找。
- 作用域管理：至少支持 singleton 和 prototype，Web 场景可扩展 request、session 等。
- 生命周期：支持实例化、属性填充、Aware 回调、BeanPostProcessor、初始化和销毁。
- 循环依赖：单例 Setter/字段注入场景可通过提前暴露对象引用解决。
- 扩展机制：提供 BeanFactoryPostProcessor、BeanPostProcessor、事件监听等扩展点。
- AOP 集成：在 Bean 初始化过程中或完成后通过代理对象增强 Bean。
- 异常处理：明确 Bean 创建失败、依赖不存在、循环依赖不可解决等异常。

## AOP 是什么？常用注解有哪些？

AOP 即面向切面编程，用来把与核心业务无关、但多个模块都会用到的逻辑抽出来统一处理，例如事务、日志、权限、监控、限流等。

核心业务和横切逻辑分离后，业务代码只关注业务本身，公共能力通过切面织入到目标方法前后，减少重复代码并降低耦合。

核心概念：

| 概念              | 含义                                                         |
| ----------------- | ------------------------------------------------------------ |
| Aspect 切面       | 切点和通知的组合，表示一类横切逻辑。AspectJ 是一个 AOP 框架，不等于切面概念本身。 |
| Join Point 连接点 | 程序执行过程中的某个点。Spring AOP 只支持方法级别连接点。    |
| Pointcut 切点     | 用表达式筛选哪些连接点需要被增强。                           |
| Advice 通知       | 真正增强的逻辑，如方法前、方法后、异常时、环绕执行。         |
| Target 目标对象   | 被代理、被增强的原始对象。                                   |
| Proxy 代理对象    | Spring 创建的增强对象，外部调用实际进入代理对象。            |
| Weaving 织入      | 把通知应用到目标方法的过程。Spring AOP 通常在运行期通过代理织入。 |

常用注解：

| 注解            | 作用                                 |
| --------------- | ------------------------------------ |
| `@Aspect`       | 声明切面类                           |
| `@Pointcut`     | 定义切点表达式                       |
| `@Before`       | 目标方法执行前执行                   |
| `@After`        | 目标方法结束后执行，不关心成功或异常 |
| `@AfterReturning` | 目标方法正常返回后执行             |
| `@AfterThrowing` | 目标方法抛出异常后执行              |
| `@Around`       | 环绕通知，可决定是否执行目标方法     |

Spring AOP 没有通用的 `@Advice` 注解，通知类型需要使用上表中的具体注解。

示例：

```java
@Aspect
@Component
public class LogAspect {
    @Pointcut("execution(* com.example.service.*.*(..))")
    public void serviceMethods() {}

    @Before("serviceMethods()")
    public void before() {
        System.out.println("before method");
    }

    @Around("serviceMethods()")
    public Object around(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.currentTimeMillis();
        try {
            return pjp.proceed();
        } finally {
            System.out.println("cost=" + (System.currentTimeMillis() - start));
        }
    }
}
```

## Spring AOP 如何实现？JDK 动态代理和 CGLIB 有什么区别？

Spring AOP 本质上通过代理对象增强目标对象。容器对外暴露的不是原始对象，而是代理对象；调用代理方法时，代理先执行通知逻辑，再调用目标方法。

| 代理方式     | 适用条件                       | 原理                                                         | 限制                            |
| ------------ | ------------------------------ | ------------------------------------------------------------ | ------------------------------- |
| JDK 动态代理 | 目标类实现了接口               | 运行时生成实现同一接口的代理类，调用转发到 InvocationHandler | 只能代理接口方法                |
| CGLIB 代理   | 目标类没有接口或强制使用类代理 | 运行时生成目标类子类，重写方法实现增强                       | `final` 类 / `final` 方法不能被代理 |

Spring 的代理策略受版本和配置影响。常见规则是：有接口时使用 JDK 动态代理，没有接口时使用 CGLIB；也可以通过配置统一强制使用 CGLIB。

静态代理理论上也能实现 AOP，但每个目标类都要手写代理类，接口变更维护成本高，也无法根据注解和切点表达式在运行时灵活匹配。

| 维度           | 静态代理                     | 动态代理                                      |
| -------------- | ---------------------------- | --------------------------------------------- |
| 代理类生成时机 | 编译期已经写好代理类         | 运行期动态生成代理类                          |
| 灵活性         | 每个目标类型通常要一个代理类 | 一个 InvocationHandler 或拦截器可处理多个方法 |
| 维护成本       | 接口新增方法时代理类也要修改 | 通过反射或方法拦截统一处理                    |
| 典型应用       | 简单固定增强                 | Spring AOP、MyBatis Mapper、RPC 客户端代理    |

代理模式的核心是：调用方不直接调用目标对象，而是调用代理对象，代理对象在调用目标方法前后添加额外逻辑。

## Spring 事务为什么会失效？`this` 调用是否生效？

事务失效通常指 `@Transactional` 没有被 Spring 代理正确拦截，或回滚规则没有按预期生效。

常见场景：

- 同类内部使用 `this.xxx()` 调用事务方法，绕过代理对象。
- `@Transactional` 标在 private、final、static 方法上，或方法不是可代理的 public 方法。具体限制取决于代理方式和 Spring 版本，但这类方法通常不能通过代理增强。
- 类没有交给 Spring 管理，例如自己 `new` 出来的对象。
- 异常被 `try/catch` 吞掉，没有继续抛出，事务管理器感知不到异常。
- 默认只对 `RuntimeException` 和 `Error` 回滚，受检异常需要配置 `rollbackFor`。
- 数据库或表引擎不支持事务，例如 MySQL MyISAM。
- 多线程中执行数据库操作，新线程不继承当前线程事务上下文。
- 事务传播行为不符合预期，例如内部方法使用 `REQUIRES_NEW` 或 `NOT_SUPPORTED`。
- 多数据源场景下事务管理器配置错误，事务方法使用了错误的 `TransactionManager`。

同类内部 `this.method()` 通常不生效，因为调用没有进入代理对象。常见解决方式：

- 把事务方法拆到另一个 Spring Bean 中，通过注入的 Bean 调用。
- 从 `AopContext` 获取当前代理调用，但需要开启 `exposeProxy`，不推荐作为常规方案。
- 把事务边界放到外层入口方法上，避免内部自调用依赖事务增强。

需要区分：抛出运行时异常导致回滚是事务正常生效；异常被捕获导致不回滚，才是典型的“回滚失效”。

## Bean 生命周期和初始化、销毁回调

Spring Bean 生命周期可以按“实例化、属性赋值、初始化、使用、销毁”记忆。

| 阶段       | 关键动作                           | 常见扩展点                                               |
| ---------- | ---------------------------------- | -------------------------------------------------------- |
| 实例化     | 通过构造器或工厂方法创建对象       | InstantiationAwareBeanPostProcessor                      |
| 属性填充   | 注入依赖和配置属性                 | `@Autowired`、`@Value`                                   |
| Aware 回调 | 注入容器相关资源                   | BeanNameAware、BeanFactoryAware、ApplicationContextAware |
| 初始化前   | 初始化方法前置处理                 | `BeanPostProcessor#postProcessBeforeInitialization`      |
| 初始化     | 执行初始化逻辑                     | `@PostConstruct`、InitializingBean、init-method           |
| 初始化后   | 初始化后置处理，AOP 常在此生成代理 | `BeanPostProcessor#postProcessAfterInitialization`       |
| 使用       | Bean 放入单例池，对外提供服务      | singletonObjects                                         |
| 销毁       | 容器关闭时释放资源                 | `@PreDestroy`、DisposableBean、destroy-method              |

面试回答可以简化为：先实例化，再属性注入，然后执行 Aware 和 BeanPostProcessor，接着初始化，初始化后可能生成 AOP 代理，最后进入容器使用，容器关闭时销毁。

初始化和销毁回调的常见方式：

| 方式               | 初始化                              | 销毁                   | 特点                   |
| ------------------ | ----------------------------------- | ---------------------- | ---------------------- |
| JSR-250 注解       | `@PostConstruct`                    | `@PreDestroy`           | 简洁，侵入较低         |
| Spring 接口        | `InitializingBean#afterPropertiesSet` | `DisposableBean#destroy` | 与 Spring 接口耦合   |
| `@Bean` 属性       | `initMethod`                        | `destroyMethod`         | 适合第三方类           |
| XML 配置           | `init-method`                       | `destroy-method`        | 传统配置方式           |
| BeanPostProcessor  | 初始化前后统一处理                 | 不直接负责销毁          | 适合对一批 Bean 做增强 |

执行顺序通常是：`@PostConstruct` 先于 `InitializingBean`，再执行自定义 `initMethod`；销毁时也会按对应机制执行。

## Bean 作用域有哪些？单例和非单例的生命周期一样吗？

Spring Bean 默认是单例 `singleton`，即一个 Spring 容器中同名 Bean 只有一个实例。单例 Bean 适合无状态的 Service、DAO、工具类等；如果保存可变状态，需要考虑线程安全。

如果配置为 `prototype`，每次从容器获取都会创建新实例，适合有状态、临时使用的对象。

注意：单例是容器级别的单例，不是全 JVM 唯一的单例。如果一个应用有多个容器，同一个 Bean 可能在不同容器中各有一个实例。

| 作用域      | 含义                                     | 典型场景             |
| ----------- | ---------------------------------------- | -------------------- |
| singleton   | 容器中同名 Bean 只有一个实例，默认作用域 | Service、DAO         |
| prototype   | 每次获取都创建新实例                     | 有状态临时对象       |
| request     | 每个 HTTP 请求一个实例                   | 请求级上下文         |
| session     | 每个 HTTP Session 一个实例               | 用户会话信息、购物车 |
| application | 每个 ServletContext 一个实例             | Web 应用全局共享对象 |
| websocket   | 每个 WebSocket 会话一个实例              | WebSocket 会话状态   |

| 对比项   | Singleton                      | Prototype                          |
| -------- | ------------------------------ | ---------------------------------- |
| 创建时机 | 默认容器启动时创建，也可懒加载 | 每次 `getBean` 或依赖注入时创建      |
| 初始化   | 容器负责完整初始化             | 容器负责完整初始化                 |
| 使用管理 | 容器持有并复用同一个实例       | 容器创建后交给调用方               |
| 销毁     | 容器关闭时调用销毁回调         | 容器不负责销毁，需要调用方自行清理 |
| 适用场景 | 无状态服务、DAO、配置组件      | 有状态对象、临时任务对象           |

核心区别：prototype Bean 容器只管创建和初始化，不跟踪后续生命周期，也不会自动执行销毁方法。

配置示例：

```java
@Bean
@Scope("prototype")
public MyBean myBean() {
    return new MyBean();
}
```

## Spring 如何解决循环依赖？三级缓存为什么需要？

Spring 主要能解决“单例 Bean + Setter/字段注入”场景下的循环依赖。构造器循环依赖无法解决，因为对象必须先构造完成才能暴露引用；prototype 循环依赖也无法通过单例缓存解决。现代 Spring Boot 版本还可能默认禁止循环引用，需要以具体版本和配置为准。

三级缓存位于 `DefaultSingletonBeanRegistry`，本质上都是 Map：

| 缓存     | 名称                  | 存放内容                   | 作用                            |
| -------- | --------------------- | -------------------------- | ------------------------------- |
| 一级缓存 | `singletonObjects`     | 完整初始化后的单例 Bean    | 最终对外提供的 Bean             |
| 二级缓存 | `earlySingletonObjects` | 已提前暴露的早期 Bean 引用 | 避免重复创建早期引用            |
| 三级缓存 | `singletonFactories`   | `ObjectFactory`            | 按需生成早期引用，兼容 AOP 代理 |

以 A 依赖 B、B 依赖 A 为例：

1. 创建 A，完成实例化后，把能生成 A 早期引用的 `ObjectFactory` 放入三级缓存。
2. A 属性注入时发现需要 B，于是创建 B。
3. B 完成实例化后，也把 `ObjectFactory` 放入三级缓存。
4. B 注入 A 时发现 A 正在创建，从三级缓存拿到 A 的 `ObjectFactory`，生成 A 的早期引用，放入二级缓存。
5. B 注入完成并初始化，进入一级缓存。
6. A 拿到 B 后继续完成初始化，最终进入一级缓存。

核心思想：先实例化，再提前暴露引用，最后完成属性注入和初始化。

如果没有 AOP，两级缓存理论上可以保存“已实例化但未初始化”的早期对象引用。但如果 A 需要被事务等 AOP 增强，而 B 在循环依赖中提前注入了 A，二级缓存直接保存原始对象可能导致：

- B 持有 `A_raw`；
- A 初始化后容器生成 `A_proxy`；
- B 持有原始对象，容器持有代理对象，事务等增强可能失效。

三级缓存保存的是 `ObjectFactory`，只有真正发生循环依赖时才生成早期引用。若需要代理，就提前返回代理对象；否则返回原始对象。生成后的引用进入二级缓存，避免重复生成。

```java
// 一级缓存：完整单例对象
Map<String, Object> singletonObjects;

// 二级缓存：早期单例对象
Map<String, Object> earlySingletonObjects;

// 三级缓存：早期对象工厂
Map<String, ObjectFactory<?>> singletonFactories;
```

## Spring 框架中用到了哪些设计模式？

| 设计模式     | Spring 中的体现                                       |
| ------------ | ----------------------------------------------------- |
| 工厂模式     | BeanFactory、ApplicationContext 创建和管理 Bean       |
| 单例模式     | Bean 默认 singleton 作用域                            |
| 代理模式     | Spring AOP、声明式事务                                |
| 模板方法模式 | JdbcTemplate、TransactionTemplate                    |
| 观察者模式   | ApplicationEvent、ApplicationListener 事件机制       |
| 适配器模式   | HandlerAdapter、AdvisorAdapter                       |
| 装饰器模式   | BeanWrapper、部分缓存和包装类                         |
| 策略模式     | ResourceLoader、InstantiationStrategy、不同事务管理器 |

## Spring 常用注解有哪些？

| 注解             | 作用                                            |
| ---------------- | ----------------------------------------------- |
| `@Component`     | 通用组件，注册为 Spring Bean                    |
| `@Service`       | Service 层语义化组件                            |
| `@Repository`    | DAO 层组件，并支持异常转换                      |
| `@Controller`    | MVC 控制器                                      |
| `@RestController` | `@Controller` + `@ResponseBody`，返回 JSON 等响应体 |
| `@Configuration`  | 配置类                                          |
| `@Bean`          | 把方法返回值注册为 Bean                         |
| `@Autowired`     | 按类型自动注入                                  |
| `@Qualifier`     | 配合 `@Autowired` 指定 Bean                     |
| `@Resource`      | JSR-250 注入，通常先按名称查找，再按类型匹配    |
| `@Value`         | 注入配置值                                      |
| `@Scope`         | 指定 Bean 作用域                                |
| `@Lazy`          | 延迟初始化                                      |
| `@Primary`       | 多个候选 Bean 时优先选择                        |
| `@Transactional` | 声明式事务                                      |

## Spring 提供了哪些常见扩展点？

| 扩展点                                  | 作用                                  |
| --------------------------------------- | ------------------------------------- |
| BeanFactoryPostProcessor                | Bean 实例化前修改 BeanDefinition      |
| BeanDefinitionRegistryPostProcessor     | 动态注册 BeanDefinition               |
| BeanPostProcessor                       | Bean 初始化前后增强，AOP 常基于此扩展 |
| FactoryBean                              | 自定义复杂 Bean 的创建逻辑            |
| ImportSelector                           | 根据条件动态导入配置类                |
| ImportBeanDefinitionRegistrar            | 编程式注册 BeanDefinition             |
| ApplicationContextInitializer            | 容器刷新前初始化 ApplicationContext   |
| ApplicationListener / ApplicationEvent   | 事件发布和监听                        |
| SmartInitializingSingleton               | 所有单例 Bean 初始化完成后回调        |
| HandlerInterceptor                       | Spring MVC 请求拦截                   |
| ControllerAdvice                         | 全局异常处理、数据绑定、响应增强      |

# Spring MVC

Spring MVC 是基于 Servlet API 的 Web MVC 框架，把请求处理拆成 Controller、Model、View 等角色，并通过 `DispatcherServlet` 统一调度。

## Spring MVC 请求处理流程

1. 用户请求进入前端控制器 `DispatcherServlet`。
2. `DispatcherServlet` 调用 `HandlerMapping`，根据 URL、HTTP Method 等找到 Handler，通常是 Controller 方法，并返回 `HandlerExecutionChain`。
3. `DispatcherServlet` 选择合适的 `HandlerAdapter`。
4. `HandlerAdapter` 完成参数解析、数据绑定、类型转换，然后调用 Controller 方法。
5. Controller 执行业务逻辑，返回 ModelAndView、视图名、对象数据或 ResponseEntity。
6. 如果返回视图，`ViewResolver` 解析视图并渲染页面。
7. 如果返回 JSON，`HttpMessageConverter` 把对象转换为响应体。
8. `DispatcherServlet` 把最终响应返回客户端。

一句话：请求先到 DispatcherServlet，再由 HandlerMapping 定位方法、HandlerAdapter 负责调用，最后通过视图解析器或消息转换器生成响应。

## HandlerMapping 和 HandlerAdapter 的区别

| 维度     | HandlerMapping                   | HandlerAdapter                 |
| -------- | -------------------------------- | ------------------------------ |
| 核心问题 | 找谁处理请求                     | 怎么调用处理器                 |
| 作用     | 根据请求找到 Handler             | 适配并执行 Handler              |
| 常见实现 | RequestMappingHandlerMapping     | RequestMappingHandlerAdapter   |
| 返回结果 | HandlerExecutionChain            | ModelAndView 或响应结果        |
| 额外能力 | 匹配 URL、Method、注解、拦截器链 | 参数绑定、类型转换、返回值处理 |

两者配合的原因是 Spring MVC 支持多种 Handler 形式。HandlerMapping 负责定位，HandlerAdapter 负责适配执行，从而保证扩展性。

## Filter 和 Interceptor 有什么区别？

| 维度             | Filter                                                 | Interceptor                             |
| ---------------- | ------------------------------------------------------ | --------------------------------------- |
| 所属体系         | Servlet 规范                                           | Spring MVC                              |
| 执行位置         | DispatcherServlet 之前                                 | DispatcherServlet 之后、Controller 前后 |
| 拦截范围         | 几乎所有进入 Servlet 容器的请求，包括静态资源          | 主要拦截 Spring MVC Handler             |
| 实现方式         | 实现 `javax.servlet.Filter` / `jakarta.servlet.Filter` | 实现 `HandlerInterceptor`               |
| 回调方法         | init、doFilter、destroy                                | preHandle、postHandle、afterCompletion  |
| Spring Bean 注入 | 可以通过注册为 Bean 支持注入                           | 天然支持 Spring Bean 注入               |
| 典型场景         | 编码、安全、CORS、请求包装                             | 登录校验、权限、业务日志、接口幂等      |

执行顺序一般是：请求先经过 Filter，再进入 DispatcherServlet，然后经过 Interceptor，最后到 Controller。

# Spring Boot

Spring Boot 的目标是简化 Spring 应用开发，通过 Starter、自动配置、内嵌容器、约定大于配置，让开发者少写配置、快速启动应用。

## 为什么使用 Spring Boot？它和 Spring 有什么区别？

Spring 更偏底层框架，需要开发者配置较多 Bean、依赖版本、Web 容器和集成组件。Spring Boot 在 Spring 之上做了工程化增强：

| 对比项 | Spring                    | Spring Boot                 |
| ------ | ------------------------- | --------------------------- |
| 配置   | 手动配置较多              | 自动配置为主                |
| 依赖   | 自己管理依赖版本          | Starter 统一依赖            |
| 部署   | 常部署到外部 Servlet 容器 | 内嵌容器，可执行 Jar        |
| 启动   | 需要较多环境准备          | main 方法直接启动           |
| 监控   | 需要自行集成              | Actuator 提供健康检查和指标 |

主要收益：

- 简化配置，减少 XML 和手动 Bean 配置。
- 内嵌 Tomcat、Jetty、Undertow，可直接打成可执行 Jar。
- 通过 Starter 快速集成 Web、Redis、MyBatis、JPA、安全等能力。
- 与 Spring MVC、Spring Data、Spring Security、Actuator、Spring Cloud 等生态集成。

Spring Boot 不是替代 Spring，而是在 Spring 基础上提供更高层的工程化封装。

## Spring Boot 如何体现约定大于配置？自动装配原理是什么？

约定大于配置指框架预设一套合理默认规则：遵循约定时不需要显式配置，默认行为不满足需求时再通过配置覆盖。

典型约定：

- 主启动类放在根包，默认扫描其所在包及子包下的组件。
- 引入 `spring-boot-starter-web` 后自动配置 Spring MVC 和内嵌 Tomcat。
- 默认读取 `application.properties` 或 `application.yml`。
- 默认提供日志、JSON 转换、错误处理和静态资源目录。

自动装配的核心是：根据 classpath 中的依赖、配置属性和条件注解，自动向 Spring 容器注册合适的 Bean。

关键链路：

1. `@SpringBootApplication` 包含 `@EnableAutoConfiguration`。
2. Spring Boot 启动时读取自动配置类列表。
3. Spring Boot 2.7+ 主要读取 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`。
4. Spring Boot 2.7 之前主要读取 `META-INF/spring.factories` 中的 `EnableAutoConfiguration`。
5. 自动配置类通过 `@ConditionalOnClass`、`@ConditionalOnMissingBean`、`@ConditionalOnProperty` 等条件判断是否生效。
6. 条件满足后，自动配置类通过 `@Bean` 注册默认组件。

Starter 的作用是把依赖和自动配置打包好。开发者“导入就能用”，本质是起步依赖引入了相关类和自动配置，自动配置再根据条件创建 Bean。

## 常见 Starter 有哪些？

| Starter                        | 作用                                            |
| ------------------------------ | ----------------------------------------------- |
| spring-boot-starter-web        | Spring MVC、JSON、内嵌 Tomcat                   |
| spring-boot-starter-test       | JUnit、Spring Test、AssertJ、Mockito 等测试依赖 |
| spring-boot-starter-jdbc       | JDBC、数据源、事务基础能力                      |
| spring-boot-starter-data-jpa   | Spring Data JPA、Hibernate                      |
| spring-boot-starter-data-redis | Redis 客户端和 Spring Data Redis                |
| spring-boot-starter-security   | Spring Security 安全能力                        |
| spring-boot-starter-aop        | Spring AOP 和 AspectJ 支持                      |
| mybatis-spring-boot-starter    | MyBatis 与 Spring Boot 集成                     |
| spring-boot-starter-actuator   | 健康检查、指标、监控端点                        |

## 如何自定义 Spring Boot Starter？

自定义 Starter 一般包含两部分：starter 依赖包和 autoconfigure 自动配置包；小项目也可以放在一个模块里。

基本步骤：

1. 引入 `spring-boot-autoconfigure`。
2. 编写业务服务类，例如 `HelloService`。
3. 编写配置属性类，使用 `@ConfigurationProperties(prefix = "hello")` 接收用户配置。
4. 编写自动配置类，使用条件注解决定是否创建默认 Bean。
5. 注册自动配置类。

示例：

```java
@ConfigurationProperties(prefix = "hello")
public class HelloProperties {
    private String prefix = "Hi";
    private String suffix = "Welcome";
}

@AutoConfiguration
@EnableConfigurationProperties(HelloProperties.class)
@ConditionalOnClass(HelloService.class)
public class HelloAutoConfiguration {
    @Bean
    @ConditionalOnMissingBean
    public HelloService helloService(HelloProperties properties) {
        return new HelloService(properties.getPrefix(), properties.getSuffix());
    }
}
```

Spring Boot 2.7+ 在下面文件中写入自动配置类全限定名：

```text
META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
```

Spring Boot 2.7 之前使用：

```text
META-INF/spring.factories
```

## Spring Boot 里面有哪些重要注解？

| 注解                           | 作用                                                         |
| ------------------------------ | ------------------------------------------------------------ |
| `@SpringBootApplication`       | 启动类注解，组合了 `@SpringBootConfiguration`、`@EnableAutoConfiguration`、`@ComponentScan` |
| `@EnableAutoConfiguration`     | 开启自动配置                                                 |
| `@SpringBootConfiguration`     | Spring Boot 配置类，本质上是 `@Configuration`                |
| `@ComponentScan`               | 组件扫描                                                     |
| `@ConfigurationProperties`     | 绑定配置文件属性                                             |
| `@EnableConfigurationProperties` | 开启配置属性类绑定                                         |
| `@ConditionalOnClass`           | classpath 存在某个类时生效                                   |
| `@ConditionalOnMissingBean`     | 容器中不存在某个 Bean 时生效                                 |
| `@ConditionalOnProperty`        | 配置属性满足条件时生效                                       |
| `@RestController`               | REST 接口控制器                                              |
| `@GetMapping` / `@PostMapping`  | HTTP 请求映射                                                |

# MyBatis

MyBatis 是半自动 ORM 框架：开发者自己编写 SQL，框架负责参数映射、结果集映射、执行流程封装和与 Spring 集成。

## MyBatis 和 JDBC 相比有什么优点？

- 减少模板代码：封装连接获取、参数设置、结果集映射和资源关闭。
- SQL 和 Java 代码解耦：SQL 写在 XML 或注解中，便于维护和调优。
- 支持动态 SQL：通过 `if`、`choose`、`foreach` 等标签动态拼接条件。
- 结果映射方便：支持字段到对象属性的映射，也支持复杂 `resultMap`。
- 与 Spring 集成好：Mapper 接口可被扫描成 Bean，并复用 Spring 事务。
- 灵活可控：相比全自动 ORM，更适合复杂 SQL 和性能优化场景。

## JDBC 连接数据库的步骤是什么？

1. 加载数据库驱动。
2. 通过 `DriverManager.getConnection(url, username, password)` 获取连接。
3. 创建 Statement 或 PreparedStatement。
4. 执行 SQL。
5. 如果是查询，遍历 ResultSet 并封装结果。
6. 关闭 ResultSet、Statement、Connection。

MyBatis 对这些重复流程做了封装，开发者重点关注 SQL 和映射关系。

## 原生 MyBatis 查询怎么写？

1. 配置数据源和 MyBatis 全局配置。
2. 编写实体类。
3. 编写 Mapper 接口，声明查询方法。
4. 编写 XML 映射文件，namespace 对应 Mapper 接口全限定名。
5. 在 XML 中编写 SQL，并配置 `parameterType`、`resultType` 或 `resultMap`。
6. 通过 SqlSession 获取 Mapper 代理对象并调用方法。
7. 提交事务并关闭 SqlSession。

在 Spring Boot 中通常使用 `@MapperScan` 扫描 Mapper，由 Spring 管理 SqlSession 和事务。

## MyBatis 中 `#{}` 和 `${}` 有什么区别？

| 写法  | 原理                                                | 是否防 SQL 注入 | 适用场景                                 |
| ----- | --------------------------------------------------- | --------------- | ---------------------------------------- |
| `#{}` | 使用 `?` 占位符，PreparedStatement 预编译并设置参数 | 是              | 普通参数值，如 id、name                  |
| `${}` | 字符串直接拼接进 SQL                                | 否              | 表名、列名、排序字段等无法用占位符的位置 |

优先使用 `#{}`。必须使用 `${}` 时，一定要做白名单校验，例如排序字段只能从固定枚举中选择。

## MyBatis 一级缓存和二级缓存有什么区别？

一级缓存：

- SqlSession 级别缓存，默认开启。
- 同一个 SqlSession 中执行相同查询，可能直接从缓存返回。
- 执行 insert、update、delete、commit、rollback 会清空一级缓存。

二级缓存：

- Mapper namespace 级别缓存，需要手动开启。
- 多个 SqlSession 可共享同一个 Mapper 的二级缓存。
- 要求缓存对象可序列化，且要注意数据一致性。

面试重点：一级缓存默认开启、作用域是 SqlSession；二级缓存作用域更大，但实际项目里常用 Redis 等外部缓存替代。

## MyBatis 和 MyBatis-Plus 有什么区别？

MyBatis-Plus 是 MyBatis 的增强工具，不改变 MyBatis 原有能力，只是在其基础上提供通用 CRUD、条件构造器、分页插件、代码生成器等能力。

| 对比项   | MyBatis                  | MyBatis-Plus                               |
| -------- | ------------------------ | ----------------------------------------- |
| CRUD     | 多数需要自己写 SQL       | BaseMapper 提供通用方法                   |
| 条件查询 | XML 或注解手写           | QueryWrapper、LambdaQueryWrapper          |
| 分页     | 自己写 limit 或插件      | 内置分页插件                              |
| 代码生成 | 需自行处理或借助外部工具 | 提供代码生成器                            |
| 灵活性   | SQL 完全可控             | 简单场景效率高，复杂 SQL 仍可回到 MyBatis |

## MyBatis 运用了哪些常见设计模式？

| 设计模式     | MyBatis 中的体现                                     |
| ------------ | ---------------------------------------------------- |
| 建造者模式   | SqlSessionFactoryBuilder、XMLConfigBuilder           |
| 工厂模式     | SqlSessionFactory、ObjectFactory、MapperProxyFactory |
| 代理模式     | MapperProxy 为 Mapper 接口生成代理对象               |
| 模板方法模式 | BaseExecutor、BaseTypeHandler                        |
| 装饰器模式   | Cache decorators                                     |
| 适配器模式   | Log 接口适配不同日志框架                             |
| 组合模式     | SqlNode 及动态 SQL 节点                              |
| 单例模式     | ErrorContext、LogFactory 部分实现                    |

# Spring Cloud

Spring Cloud 是用于构建微服务架构的一组工具集，解决服务注册发现、配置管理、网关、负载均衡、熔断限流、链路追踪等分布式系统问题。

## Spring Cloud 和 Spring Boot 有什么区别？

Spring Boot 用来快速构建单个 Spring 应用，重点是自动配置、快速启动和工程化。

Spring Cloud 建立在 Spring Boot 之上，用来构建分布式微服务系统，重点是注册中心、配置中心、网关、负载均衡、熔断降级、链路追踪等服务治理能力。

两者关系：先用 Spring Boot 开发每个微服务，再用 Spring Cloud 解决多个微服务之间的治理问题。具体版本需要遵循 Spring Cloud 与 Spring Boot 的兼容关系。

## 微服务核心组件有哪些？

| 组件     | 解决的问题                       | 常见实现                                  |
| -------- | -------------------------------- | ----------------------------------------- |
| 注册中心 | 服务实例如何注册、发现和健康检查 | Eureka、Nacos、Consul                     |
| 负载均衡 | 多个实例如何选择一个调用         | Spring Cloud LoadBalancer、旧版 Ribbon    |
| 服务通信 | 服务之间如何调用                 | OpenFeign、RestTemplate、WebClient、Dubbo |
| 网关     | 统一入口、路由、鉴权、限流       | Spring Cloud Gateway                      |
| 配置中心 | 多环境配置如何集中管理和动态刷新 | Nacos Config、Spring Cloud Config         |
| 熔断限流 | 依赖服务异常时如何保护系统       | Resilience4j、Sentinel                    |
| 链路追踪 | 一次请求跨多个服务如何排查       | Micrometer Tracing、Zipkin、SkyWalking    |
| 日志监控 | 日志、指标如何集中查看           | ELK、EFK、Prometheus、Grafana             |

Spring Cloud Alibaba 常见对应关系：

| 能力                | Alibaba 生态                                                 |
| ------------------- | ------------------------------------------------------------ |
| 注册中心 / 配置中心 | Nacos                                                        |
| 负载均衡            | Nacos 提供实例列表，结合 Spring Cloud LoadBalancer 客户端负载均衡 |
| 服务通信            | OpenFeign、Dubbo                                             |
| 网关                | Spring Cloud Gateway                                         |
| 熔断限流            | Sentinel                                                     |
| 链路追踪            | SkyWalking、Zipkin 等                                        |

## 负载均衡有哪些算法？如何实现用户黏性？

常见算法：

- 轮询：请求按顺序分配给不同实例。
- 加权轮询：权重高的实例分配更多请求。
- 随机：随机选择实例。
- 加权随机：按权重随机选择实例。
- 最小连接数 / 最小活跃数：优先选择当前压力较小的实例。
- 一致性哈希：根据用户 ID、IP 或业务 key 哈希到固定实例，适合需要会话黏性的场景。

要让同一个用户尽量打到同一个实例，可以根据用户 ID、token、客户端 IP 等稳定 key 计算哈希值，再映射到服务实例。

不过微服务设计最好尽量无状态，把会话状态放到 Redis、数据库等外部存储中。这样即使请求打到不同实例，也不会影响业务正确性。

## 什么是服务熔断和服务降级？

服务熔断是为了防止下游服务异常拖垮整个调用链。当错误率、超时率或慢调用比例达到阈值时，熔断器会暂时打开，后续请求不再真实调用下游，而是快速失败或返回 fallback。

熔断器常见状态：

- Closed：正常调用，统计失败率。
- Open：熔断打开，直接拒绝或降级返回。
- Half-Open：放少量请求探测下游是否恢复，成功则关闭熔断，失败则继续打开。

现代 Spring Cloud 中常用 Resilience4j 或 Spring Cloud Circuit Breaker；Spring Cloud Alibaba 生态常用 Sentinel。Hystrix 已停止维护，不应作为新项目首选。

服务降级是在系统压力过高或依赖服务不可用时，牺牲非核心功能，保证核心链路可用。常见方式：

- 返回默认值、缓存值或兜底文案。
- 关闭推荐、排行榜、埋点等非核心功能。
- 限制部分用户或部分接口访问。
- 异步化或延迟处理非关键任务。

熔断更偏“保护调用链，阻止继续调用异常依赖”；降级更偏“提供有损但可接受的兜底服务”，两者通常配合使用。

# 注册中心与配置中心

## Nacos 和 Eureka 有什么区别？

| 对比项     | Eureka                                      | Nacos                                      |
| ---------- | ------------------------------------------- | ------------------------------------------ |
| 定位       | 服务注册与发现                              | 服务注册发现 + 配置中心                    |
| 一致性     | 以 AP 思路为主，网络分区时允许返回旧数据    | 支持 AP / CP，具体取决于服务类型和配置      |
| 数据获取   | 客户端定时拉取服务列表                      | 服务发现支持推拉结合，配置支持长轮询        |
| 生态        | Netflix 旧版 Spring Cloud 组件              | 与 Spring Cloud Alibaba 集成较好           |
| 维护状态   | Eureka 2.x 已停止开发，项目选型需谨慎       | 具体能力和版本需要结合官方文档确认          |

Nacos 可以减少注册中心和配置中心的组件数量，但不应脱离 Spring Cloud、Spring Boot 和 Nacos 版本兼容关系做绝对选型结论。

## Nacos 配置中心如何实现动态配置更新？

客户端与 Nacos Server 建立长轮询连接，配置未变更时 Server 挂起请求，直到超时或配置变更；配置变更时 Server 立即响应，客户端再拉取最新内容。长轮询超时时间和具体行为以客户端版本及配置为准。

配置隔离的三个维度通常是：

`Namespace`（命名空间）→ `Group`（分组）→ `Data ID`

常见用法是 Namespace 区分环境（dev/test/prod），Group 区分业务模块。

代码层面：

- `@Value` + `@RefreshScope`：配置变更后刷新 Bean 中的配置字段。
- `@NacosConfigListener`：监听指定配置变更事件。
- 灰度发布：只将配置推送给指定实例或指定标签的实例。

# API 网关

## Spring Cloud Gateway 的作用和核心原理是什么？

Gateway 是所有外部请求的统一入口，负责路由转发、鉴权、限流、日志、跨域和灰度发布。

三大核心概念：

- Route（路由）：定义请求转发规则，包含 ID、目标 URI、断言和过滤器。
- Predicate（断言）：匹配请求条件，如 Path、Header、Host、Method。
- Filter（过滤器）：对请求或响应做处理，分为 GatewayFilter（单路由）和 GlobalFilter（全局）。

与 Zuul 的对比需要结合版本：Zuul 1.x 基于 Servlet 阻塞式 I/O，Gateway 基于 Spring WebFlux 和 Reactor，采用响应式非阻塞模型。两者的性能和适用性不能只由模型直接推断，还要结合业务、配置和压测结果。

生产常见用法：

- `GlobalFilter` 实现 JWT 鉴权，解析 Token，失败返回 401。
- Redis + 令牌桶实现接口限流。
- 根据 Header 路由实现灰度发布（金丝雀部署）。

# 服务间通信

## OpenFeign 和 RestTemplate 有什么区别？

| 对比项       | RestTemplate                         | OpenFeign                                      |
| ------------ | ------------------------------------ | ---------------------------------------------- |
| 调用方式     | 命令式 HTTP 客户端                   | 声明式 HTTP 客户端                             |
| 编码方式     | 手写 URL、参数拼接和响应解析         | 定义接口并使用注解，框架生成代理实现           |
| 服务治理     | 需要额外集成                         | 可集成 Spring Cloud LoadBalancer               |
| 公共能力     | 需要自行封装拦截器和异常处理         | 支持请求/响应拦截器、超时和降级配置             |
| 适用场景     | 灵活、简单的 HTTP 调用               | 微服务间标准化接口调用                         |

示例：

```java
@FeignClient(name = "order-service", fallback = OrderFallback.class)
public interface OrderClient {
    @GetMapping("/order/{id}")
    Order getById(@PathVariable Long id);
}
```

OpenFeign 还可以统一注入 Token、TraceId 等请求头。Fallback 通常需要结合 Sentinel 或 Spring Cloud Circuit Breaker 等组件，超时配置通过对应版本的 Feign 配置项统一管理。

一般来说，微服务内部调用优先考虑 OpenFeign；简单、灵活的独立 HTTP 调用也可以使用 RestTemplate 或 WebClient。
