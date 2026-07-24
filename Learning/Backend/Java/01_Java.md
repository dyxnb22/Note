# Java

## Java 基础与执行模型

## Java 有哪些特点、优势和局限？

Java 的主要特点：

- 平台无关：源码经 `javac` 编译为字节码，由不同平台的 JVM 执行。
- 面向对象：支持封装、继承、多态和抽象。
- 自动内存管理：由 JVM 和垃圾回收器管理对象生命周期。
- 生态成熟：拥有 Spring、MyBatis、Maven、JUC 等丰富生态。
- 类型安全和兼容性较好：有字节码校验、异常机制和强类型检查。

优势是跨平台、生态成熟、内存管理自动化、并发工具丰富；局限是 JVM 启动和运行存在开销、内存占用较高、语法相对冗长，不太适合极小型运行环境和简单脚本。

## JDK、JRE 和 JVM 有什么关系？

传统关系是：

```text
JDK = JRE + 开发工具
JRE = JVM + 核心类库
```

JDK 用于开发，JRE 用于运行，JVM 负责加载、验证、执行字节码。Java 9 之后官方不再单独发布传统意义上的 JRE，实际开发通常直接安装 JDK。

## Java 是编译型语言还是解释型语言？

Java 是混合执行模型：

1. `.java` 源码由 `javac` 编译为平台无关的 `.class` 字节码。
2. JVM 运行时可以通过解释器执行字节码。
3. JVM 会识别热点代码，并通过 JIT 编译为本地机器码，后续直接执行。

因此，Java 既有编译阶段，也有运行时解释和 JIT 动态编译阶段。

## 类型系统

## Java 有哪些基本数据类型？

| 类型 | 占用空间 | 默认值（成员变量） | 说明 |
| --- | --- | --- | --- |
| `byte` | 1 字节 | `0` | 8 位整数 |
| `short` | 2 字节 | `0` | 16 位整数 |
| `int` | 4 字节 | `0` | 常用整数类型 |
| `long` | 8 字节 | `0L` | 字面量建议加 `L` |
| `float` | 4 字节 | `0.0f` | 单精度，字面量需加 `f` |
| `double` | 8 字节 | `0.0d` | 默认浮点类型 |
| `char` | 2 字节 | `\u0000` | UTF-16 代码单元 |
| `boolean` | JVM 规范未固定 | `false` | 只有 `true` 和 `false` |

局部变量没有默认值，使用前必须显式初始化。`char` 的 2 字节表示一个 UTF-16 代码单元，不一定等于一个完整 Unicode 字符。

## 为什么金额计算使用 BigDecimal，而不是 double？

`double` 是二进制浮点数，无法精确表示很多十进制小数，例如 `0.1`，可能产生精度误差。`BigDecimal` 使用任意精度的十进制表示，适合金额等精确计算。

创建 `BigDecimal` 时优先使用字符串或 `BigDecimal.valueOf()`：

```java
BigDecimal a = new BigDecimal("0.1");
BigDecimal b = BigDecimal.valueOf(0.1);
```

## Java 如何进行类型转换？

- 自动转换：小范围类型转大范围类型，例如 `int` 转 `long`。
- 强制转换：大范围类型转小范围类型，可能溢出；浮点转整数会截断小数，`int` 转 `float` 也可能损失有效数字。
- 字符串转换：使用 `Integer.parseInt()`、`Double.parseDouble()`、`String.valueOf()` 等方法。

## Java 的对象引用如何转换？

- 向上转型：子类转父类，自动且安全。

  ```java
  Animal animal = new Dog();
  ```

- 向下转型：父类转子类，需要显式转换；如果实际对象不是目标类型，会抛出 `ClassCastException`。

  ```java
  if (animal instanceof Dog) {
      Dog dog = (Dog) animal;
  }
  ```

## 基本类型和包装类有什么区别？Integer 缓存是什么？

基本类型直接保存值，性能和内存开销较小，不能为 `null`，也不能直接用于泛型。包装类是对象，可以为 `null`，能用于集合和泛型，并提供工具方法。

自动装箱通常调用 `Integer.valueOf()`，自动拆箱通常调用 `intValue()`。包装类为 `null` 时自动拆箱会抛出 `NullPointerException`，频繁装箱也可能带来额外开销。

`Integer.valueOf()` 对 `-128` 到 `127` 的缓存是规范保证的，超出范围是否缓存不能依赖。因此比较包装类内容应使用 `equals()`，不要使用 `==`。

## 面向对象与关键字

## 面向对象的三大特性是什么？

- 封装：隐藏内部实现，通过公开接口交互。
- 继承：复用和扩展父类行为。
- 多态：同一接口或父类引用可以表现出不同子类行为；重载属于编译期多态，重写属于运行时多态。

## 面向对象有哪些设计原则？

- 单一职责原则：一个类尽量只负责一类职责。
- 开放封闭原则：对扩展开放，对修改封闭。
- 里氏替换原则：子类应能替换父类而不破坏程序正确性。
- 接口隔离原则：接口应该小而专，客户端不依赖不需要的方法。
- 依赖倒置原则：高层和低层都依赖抽象，细节依赖抽象。
- 最少知识原则：对象只与必要的直接对象交互。

## 抽象类和普通类有什么区别？

| 特性   | 普通类        | 抽象类            |
| ---- | ---------- | -------------- |
| 实例化  | 可以直接 `new` | 不能直接实例化        |
| 抽象方法 | 不能包含抽象方法   | 可以包含抽象方法，也可以没有 |
| 构造方法 | 可以有        | 可以有，用于子类初始化    |
| 子类要求 | 没有特殊要求     | 子类需要实现继承到的抽象方法 |

抽象类不一定必须包含抽象方法，常用于复用状态和通用实现。

## 抽象类和接口有什么区别？

| 特性 | 抽象类 | 接口 |
| --- | --- | --- |
| 继承关系 | 类只能继承一个父类 | 类可以实现多个接口 |
| 成员变量 | 可以有实例变量和静态变量 | 字段默认是 `public static final` 常量 |
| 构造方法 | 可以有 | 没有构造方法 |
| 方法 | 可以有抽象方法和具体方法 | 可有抽象、`default`、`static` 方法；Java 9 起可有 `private` 方法 |
| 适用场景 | 表达一组共享状态和实现 | 表达行为规范或能力 |

## 抽象类可以使用 final 修饰吗？

不能。抽象类需要被继承，`final` 类禁止继承，二者语义冲突。

## 接口中可以定义哪些方法？

- 抽象方法：由实现类提供实现。
- `default` 方法：提供默认实现，便于接口向后兼容。
- `static` 方法：属于接口本身，通过接口名调用。
- `private` 方法：Java 9 起用于复用接口内部的辅助逻辑。

```java
default void sleep() {
    System.out.println("Sleeping...");
}
```

## static 变量、static 方法和 static 代码块有什么特点？

- 静态变量属于类，在类初始化时分配并初始化一次，推荐通过类名访问。
- 静态方法不依赖对象，不能直接访问实例成员；不支持重写，只能被隐藏，调用哪个方法取决于引用的声明类型。
- 静态代码块在类初始化时执行，多个静态代码块按定义顺序执行，常用于初始化静态成员。

## 类初始化与对象初始化顺序是什么？

类第一次被主动使用时，先初始化父类，再初始化子类；同一个类中的静态变量和静态代码块按源码出现顺序执行。编译期常量可能被内联，读取它不一定触发类初始化。

创建子类对象时，实例字段会先取得默认零值，然后执行父类的实例字段初始化和初始化块、父类构造方法，再执行子类自己的实例字段初始化、初始化块和构造方法。需要区分：静态初始化每个类只执行一次，实例初始化每次创建对象都会执行。

## final 有什么作用？

- 修饰类：类不能被继承。
- 修饰方法：方法不能被子类重写。
- 修饰变量：变量只能赋值一次；如果变量保存对象引用，引用不能改变，但对象内容仍可能改变。

## 静态内部类和非静态内部类有什么区别？

| 特性 | 非静态内部类 | 静态内部类 |
| --- | --- | --- |
| 外部类实例 | 依赖外部类实例 | 不依赖外部类实例 |
| 外部成员访问 | 可直接访问外部类实例和静态成员 | 只能直接访问外部类静态成员 |
| 隐藏引用 | 持有 `Outer.this`，可能延长外部对象生命周期 | 不持有外部实例引用 |
| 实例化 | `new Outer().new Inner()` | `new Outer.StaticInner()` |

非静态内部类可以直接访问外部类方法，是因为编译器会为它维护一个外部类实例引用；发生同名冲突时可使用 `Outer.this.method()`。

## 对象模型与泛型

## Java 创建对象有哪些方式？

| 方式 | 是否调用构造器 | 特点 |
| --- | --- | --- |
| `new` | 是 | 最常用，编译期确定类型 |
| 反射 | 是，使用 `Constructor.newInstance()` | 运行时动态创建，框架常用 |
| `clone()` | 否 | 基于已有对象复制 |
| 反序列化 | 否 | 从字节流恢复对象 |
| 工厂方法 | 通常是 | 封装创建逻辑、降低耦合 |

## Java 对象什么时候会被回收？

主流 JVM 通过可达性分析判断对象是否仍然存活，而不是简单依赖引用计数。

1. 从 GC Roots 沿引用链查找对象。
2. 不可达对象具备被回收的条件，但不保证立即回收。
3. 强引用通常不会被回收；软引用内存不足时可能回收；弱引用在下一次 GC 时通常回收；虚引用用于跟踪回收。

常见 GC Roots 包括虚拟机栈局部变量、类静态字段、常量引用和 JNI 引用。`finalize()` 不推荐使用，资源应通过显式关闭或 `try-with-resources` 管理。

## 如何获取对象的私有字段？

优先使用公开访问器；确有需要时可通过反射读取：

```java
Class<?> clazz = obj.getClass();
Field field = clazz.getDeclaredField("privateField");
field.setAccessible(true);
String value = (String) field.get(obj);
```

模块系统和访问权限可能限制反射访问，框架代码应谨慎使用。

## 什么是浅拷贝和深拷贝？

- 浅拷贝复制对象本身和基本类型字段，引用类型字段仍然指向原对象。
- 深拷贝会递归复制引用类型字段，使副本不与原对象共享内部对象。

常见实现方式：手动递归复制、序列化/反序列化、实现 `Cloneable` 并递归处理引用字段。`Cloneable` 方案容易维护困难，实际项目通常优先使用明确的复制构造器或工厂方法。

## 为什么需要泛型？

泛型用类型参数表达一组可复用的代码：

```java
class Box<T> {
    private T value;
}
```

使用泛型可以复用同一套逻辑，并由编译器进行类型检查，减少强制类型转换和运行时类型错误。

## 反射与注解

## 什么是 Java 反射？

反射允许程序在运行时获取类的名称、父类、接口、构造器、方法和字段等信息，并动态创建对象、调用方法、读取或修改字段。

建议使用 `Constructor.newInstance()` 创建对象，不再使用已过时的 `Class.newInstance()`：

```java
Constructor<MyClass> constructor =
        MyClass.class.getDeclaredConstructor();
constructor.setAccessible(true);
MyClass obj = constructor.newInstance();
```

## 反射有哪些应用？动态代理和反射有什么关系？

反射常用于：

- 动态加载类和数据库驱动。
- 根据配置文件创建对象、注入属性。
- Spring 扫描注解并注册 Bean。
- JDK 动态代理和框架方法调用。

JDK 动态代理基于接口，核心 API 是 `Proxy.newProxyInstance()` 和 `InvocationHandler`；调用代理方法时会转发到 `invoke()`，其中可以通过 `Method.invoke()` 调用目标方法。Spring AOP 通常在有接口时使用 JDK 代理，没有接口时使用 CGLIB 子类代理。

## Java 注解的原理是什么？

注解本质上是继承 `java.lang.annotation.Annotation` 的特殊接口，用于给类、方法、字段等程序元素添加元数据。

`@Retention` 决定保留阶段：

- `SOURCE`：只保留在源码中，例如 `@Override`。
- `CLASS`：保留在 `.class` 文件中，运行时默认不可见。
- `RUNTIME`：保留到运行时，可通过反射读取。

`@Target` 用于限制注解可以作用于类、方法、字段、构造器或局部变量等位置。

运行时注解会作为字节码元数据被 JVM 加载，`Class`、`Method`、`Field`、`Constructor` 等实现了 `AnnotatedElement`，可通过以下方法读取：

```java
MyLog log = method.getAnnotation(MyLog.class);
boolean present = method.isAnnotationPresent(MyLog.class);
```

JDK 返回的注解对象是注解接口的代理对象，调用属性方法时会读取注解中保存的属性值。框架可以据此注册 Bean、生成代理或开启事务。

## API 和 SPI 有什么区别？

API 是功能提供方暴露给调用方使用的接口，调用方依赖并调用它；SPI 则是框架或调用方定义扩展契约，由实现方提供实现，框架在运行时发现并加载实现。

```text
API：调用方 -> 使用 -> 提供方
SPI：框架定义契约 <- 实现方接入，框架负责发现和调用
```

JDBC 驱动、日志实现和 Java `ServiceLoader` 都体现了 SPI 思想。SPI 能降低框架与具体实现的耦合，但需要处理实现发现、版本兼容、加载失败和生命周期管理。

## 异常与常用类

## Java 的异常体系是怎样的？

```text
Throwable
├── Error
│   ├── OutOfMemoryError
│   └── StackOverflowError
└── Exception
    ├── RuntimeException
    │   ├── NullPointerException
    │   ├── ClassCastException
    │   └── IndexOutOfBoundsException
    └── Checked Exception
        ├── IOException
        └── SQLException
```

- `Error`：JVM 或运行环境层面的严重错误，通常不应由业务捕获。
- Checked Exception：编译器要求捕获或声明抛出，常表示文件、网络、数据库等外部环境问题。
- `RuntimeException`：编译器不强制处理，通常表示程序逻辑错误。

## `assert` 什么时候适合使用？

`assert condition` 用于检查开发者假设的不变量；通常需要用 `-ea` 显式开启，失败时抛出 `AssertionError`，生产环境可能默认关闭。因此它适合开发、测试和内部状态检查，不应承担用户输入校验、权限校验或必须执行的业务规则。

## ==、equals 和 hashCode 有什么区别？

- `==` 比较基本类型的值；比较引用类型时比较是否指向同一个对象。
- `equals()` 默认也比较对象身份，但许多类会重写它来比较逻辑内容，例如 `String`。
- 如果重写 `equals()`，通常必须同时重写 `hashCode()`。

`HashMap`、`HashSet` 等哈希集合先用 `hashCode()` 定位桶，再用 `equals()` 判断是否真正相等。只重写 `equals()` 而不重写 `hashCode()`，可能导致逻辑相等的对象位于不同桶中。

## String、StringBuilder 和 StringBuffer 有什么区别？

| 特性 | String | StringBuilder | StringBuffer |
| --- | --- | --- | --- |
| 可变性 | 不可变 | 可变 | 可变 |
| 线程安全 | 不可变，因此可安全共享 | 不保证线程安全 | 主要方法使用同步 |
| 适用场景 | 常量、只读字符串 | 单线程频繁拼接 | 需要同步的动态字符串 |

`String` 拼接可能创建新对象，`StringBuilder` 和 `StringBuffer` 维护可变字符序列。JDK 9 之后 `String` 内部使用 `byte[] + coder`，对 Latin-1 字符更节省内存，但核心结论仍是“String 不可变，Builder/Buffer 可变，Buffer 线程安全”。

## Java 8+ 新特性

## Java 8 有哪些重要新特性？

| 特性 | 作用 |
| --- | --- |
| Lambda | 简化函数式接口的实现 |
| 函数式接口 | 只有一个抽象方法的接口 |
| Stream | 链式处理集合数据 |
| Optional | 封装可能为空的值 |
| 方法引用 | 简化 Lambda |
| 接口默认/静态方法 | 增强接口的扩展能力 |
| CompletableFuture | 支持异步任务组合 |
| 重复注解和类型注解 | 扩大注解使用能力 |

## Lambda 和函数式接口如何使用？

Lambda 是函数式接口的简洁实现形式，常见语法：

```java
(parameters) -> expression
(parameters) -> { statements; }
```

```java
interface Calculator {
    int calculate(int a, int b);
}

int result = ((Calculator) (a, b) -> a + b).calculate(3, 5);
```

Lambda 可以减少匿名内部类的样板代码，但嵌套过深时会降低可读性和调试体验。

## 常见函数式接口有哪些？

`@FunctionalInterface` 用于让编译器检查接口是否只有一个抽象方法（`default`、`static` 方法不计入）。常见接口可以这样记：

| 接口 | 输入/输出 | 典型用途 |
| --- | --- | --- |
| `Predicate<T>` | `T -> boolean` | 条件判断、过滤 |
| `Function<T, R>` | `T -> R` | 转换、映射 |
| `Consumer<T>` | `T -> void` | 消费、遍历处理 |
| `Supplier<T>` | `() -> T` | 延迟提供对象或数据 |

它们常与 Stream、集合处理和异步任务组合使用。

## `java.time` 相比 `Date`/`Calendar` 有什么优势？

`java.time` 类型不可变且线程安全，职责更清晰，适合替代旧日期 API：

- `LocalDate`、`LocalTime`、`LocalDateTime`：不含时区的日期和时间。
- `Instant`：时间线上的瞬时点，适合记录时间戳。
- `ZonedDateTime`、`ZoneId`：需要时区时使用。
- `Duration`、`Period`：分别表示时间量和日期量。
- `DateTimeFormatter`：线程安全的格式化工具。

涉及跨时区或系统边界时，不要把 `LocalDateTime` 当作时间戳；应明确使用 `Instant` 或带时区的类型。

## Stream API 如何使用？

Stream 用于对数据进行过滤、映射、排序、聚合等链式处理：

```java
List<String> result = originalList.stream()
        .filter(s -> s.length() > 3)
        .collect(Collectors.toList());

int sum = numbers.stream()
        .mapToInt(Integer::intValue)
        .sum();
```

Stream 不直接存储数据，通常由数据源、多个中间操作和一个终止操作组成。

## Parallel Stream 有什么特点和问题？

Parallel Stream 会把数据拆成多个子任务，使用通用 `ForkJoinPool` 并行处理，再合并结果。

- 更适合计算量较大的 CPU 密集型任务。
- 对 I/O 密集型任务、任务量很小的场景通常不合适。
- 会使用公共线程池，阻塞或任务过重可能影响进程中的其他并行任务。
- 需要注意线程安全、顺序、拆分和合并成本，不能默认比串行 Stream 快。

## Java 9 到 Java 25 有哪些常见新特性？

| 版本 | 代表特性 |
| --- | --- |
| Java 9 | JPMS 模块系统、接口私有方法、try-with-resources 改进 |
| Java 10 | `var` 局部变量类型推断 |
| Java 14/16 | Record |
| Java 17 LTS | Sealed Class、模式匹配持续演进 |
| Java 21 LTS | 虚拟线程、Record Pattern、Pattern Matching for switch、Sequenced Collections |
| Java 25（多数发行商 LTS） | Scoped Values、Module Import Declarations、Compact Source Files、Flexible Constructor Bodies |

Java 21 的虚拟线程主要降低大量阻塞 I/O 任务的线程创建和调度成本，不用于提升 CPU 密集型计算性能。JDK 25 于 2025-09-16 GA；具体发行商的支持期限不同，选型时同时核对框架兼容矩阵和发行商支持策略。

## 专题延伸

- 序列化、BIO/NIO/AIO、文件和网络服务线程模型见 [Java I/O 与网络编程](02_JavaIO与网络编程.md)。
- 可见性、锁、双重检查和并发工具见 [JUC](05_JUC.md)。
- 代理、适配器等职责设计见 [Java 设计模式](06_设计模式.md)。

## Java 面试题

## 学生如何按照分数排序，再按照学号排序？

可以让类实现 `Comparable`，在 `compareTo()` 中定义默认排序规则：

```java
public class Student implements Comparable<Student> {
    private int id;
    private int score;

    @Override
    public int compareTo(Student other) {
        if (score != other.score) {
            return Integer.compare(other.score, score); // 分数降序
        }
        return Integer.compare(id, other.id); // 学号升序
    }
}
```

如果同一个类需要多种排序规则，也可以使用 `Comparator`，而不是把所有规则都写进 `Comparable`。
