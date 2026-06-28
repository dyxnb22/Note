# Spring

# Spring
Spring 的核心价值是用 IoC 降低对象创建和依赖管理的耦合，用 AOP 统一处理事务、日志、权限等横切逻辑，并在此基础上提供事务管理、MVC、数据访问等完整企业开发能力。
<details>
<summary>Spring 的核心思想</summary>
	<table header-row="true" header-column="false">
<tr>
<td>核心思想</td>
<td>解决的问题</td>
<td>实现手段</td>
<td>典型场景</td>
</tr>
<tr>
<td>IoC</td>
<td>对象创建、依赖组装和生命周期管理与业务代码强耦合</td>
<td>BeanFactory / ApplicationContext 管理 Bean</td>
<td>Service、DAO、配置类统一交给容器管理</td>
</tr>
<tr>
<td>DI</td>
<td>类内部硬编码 new 依赖，难测试、难替换</td>
<td>构造器、Setter、字段注入</td>
<td>注入 Repository、DataSource、第三方客户端</td>
</tr>
<tr>
<td>AOP</td>
<td>事务、日志、权限等横切逻辑散落在业务代码中</td>
<td>JDK 动态代理 / CGLIB 代理 + 切面</td>
<td>声明式事务、接口鉴权、操作日志</td>
</tr>
<tr>
<td>事务管理</td>
<td>事务 API 和业务代码耦合，跨数据访问技术不统一</td>
<td>PlatformTransactionManager + @Transactional</td>
<td>Service 层保证一组数据库操作原子性</td>
</tr>
	</table>
	一句话：IoC 管对象，DI 管依赖怎么进来，AOP 管公共逻辑怎么切进去，事务管理是 AOP 最典型的落地场景。
</details>
<details>
<summary>IoC 容器与依赖注入</summary>
	IoC 即控制反转，反转的是对象控制权：以前由业务代码主动 `new` 对象、初始化依赖、管理销毁；使用 Spring 后，由容器负责 Bean 的创建、依赖注入、初始化和销毁，业务对象只声明自己需要什么。
	DI 是 IoC 最常见的实现方式，指依赖对象由外部容器创建并注入进来，而不是类自己创建。
	常见注入方式：
	- 构造器注入：推荐用于必需依赖。
	- Setter 注入：适合可选依赖。
	- 字段注入：写法简洁，但不利于测试和不可变设计。
</details>
<details>
<summary>AOP 是什么</summary>
	AOP 即面向切面编程，用来把与核心业务无关、但多个模块都会用到的逻辑抽出来统一处理，例如事务、日志、权限、监控、限流等。
	核心概念包括 Aspect、Join Point、Pointcut、Advice、Target、Proxy、Weaving。
</details>
<details>
<summary>AOP 的实现原理：JDK 动态代理和 CGLIB</summary>
	Spring AOP 本质上是通过代理对象增强目标对象。
	- JDK 动态代理：目标类实现了接口时使用，只能代理接口方法。
	- CGLIB：目标类没有接口或强制类代理时使用，通过生成子类增强，`final` 类和 `final` 方法不能代理。
</details>
<details>
<summary>Spring 事务什么情况下会失效</summary>
	- 同类内部 `this.xxx()` 调用事务方法，绕过代理对象。
	- `@Transactional` 标在 private、final、static 方法上，或方法不是可代理的 public 方法。
	- 类没有交给 Spring 管理，例如自己 `new` 出来的对象。
	- 异常被 `try/catch` 吞掉，没有继续抛出。
	- 默认只对 RuntimeException 和 Error 回滚，受检异常需要配置 `rollbackFor`。
</details>
<details>
<summary>Bean 的生命周期</summary>
	可以按“实例化、属性赋值、初始化、使用、销毁”记忆。
	常见扩展点包括 `BeanPostProcessor`、`@PostConstruct`、`InitializingBean`、`@PreDestroy`、`DisposableBean`。
</details>
<details>
<summary>Spring 是如何解决循环依赖的</summary>
	Spring 只能解决“单例 Bean + Setter/字段注入”场景下的循环依赖。
	核心是三级缓存：
	- `singletonObjects`：完整初始化后的单例 Bean。
	- `earlySingletonObjects`：已提前暴露的早期 Bean 引用。
	- `singletonFactories`：按需生成早期引用的 `ObjectFactory`。
</details>
<details>
<summary>Spring 常用注解</summary>
	- `@Component`、`@Service`、`@Repository`、`@Controller`
	- `@RestController`、`@Configuration`、`@Bean`
	- `@Autowired`、`@Qualifier`、`@Resource`
	- `@Value`、`@Scope`、`@Lazy`、`@Primary`
	- `@Transactional`
</details>
<details>
<summary>Spring MVC 的核心流程</summary>
	请求先到 `DispatcherServlet`，再由 `HandlerMapping` 找到处理器，由 `HandlerAdapter` 调用控制器方法，最后通过视图解析器或消息转换器返回响应。
</details>
<details>
<summary>过滤器和拦截器的区别</summary>
	- Filter 属于 Servlet 规范，在 `DispatcherServlet` 之前执行。
	- Interceptor 属于 Spring MVC，在控制器前后执行。
	- Filter 更适合编码、安全、CORS、请求包装。
	- Interceptor 更适合登录校验、权限、日志、幂等。
</details>
<details>
<summary>Spring Boot 自动装配原理</summary>
	自动装配的核心是：根据 classpath 中的依赖、配置属性和条件注解，自动向 Spring 容器注册合适的 Bean。
	关键链路：
	1. `@SpringBootApplication` 包含 `@EnableAutoConfiguration`。
	2. 启动时读取自动配置类列表。
	3. 通过 `@ConditionalOnClass`、`@ConditionalOnMissingBean`、`@ConditionalOnProperty` 等条件决定是否生效。
</details>
<details>
<summary>MyBatis 里的 `#{}` 和 `${}` 的区别</summary>
	- `#{}`：预编译占位符，防 SQL 注入，适合普通参数值。
	- `${}`：字符串直接拼接，不防 SQL 注入，适合表名、列名、排序字段等无法预编译的位置。
</details>
<details>
<summary>Spring Cloud 和 Spring Boot 的区别</summary>
	Spring Boot 用来快速构建单个 Spring 应用；Spring Cloud 建立在 Spring Boot 之上，用来解决注册发现、网关、配置中心、熔断限流、链路追踪等微服务治理问题。
</details>
