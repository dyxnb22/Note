# Java

## 概念
### Java的特点

- 平台无关性（字节码、JVM）
- 面向对象（封装、继承、多态、抽象）
- 自动内存管理（JVM 垃圾回收机制）
- 生态成熟（Spring、MyBatis、Maven、JUC 等生态）
- 安全性与健壮性（字节码校验、异常机制、强类型检查和较好的向后兼容性）

### Java 的优势和劣势

优势：
- 跨平台性
- 极致的生态与社区
- 内存管理自动化
- 原生并发支持：从语言底层支持多线程模型，拥有极其丰富的并发工具包（java.util.concurrent），适合处理高并发业务。
- 面向对象与规范性
- 高安全性与兼容性

劣势：

- 性能开销与启动延迟：相较于 C++/Rust 等原生编译语言，JVM **存在运行时开销**。且在微服务场景下**启动慢**
- 语法冗长：虽然引入了 Lambda 和 Record，但相比 Python 或 Go，Java 依然显得笨重，需要编写大量**样板代码**。
- 高内存占用：JVM 运行本身需要预分配较多内存，且对象头信息等开销，使得 Java 在内存受限（如嵌入式或极小容器）的环境下表现不佳。
- 开发节奏较慢：由于**强类型的约束和强制的编译过程**，在进行快速原型开发或脚本编写时，效率不及动态语言。
- 函数式支持不够纯正：Java 的函数式编程（Stream API 等）是在 OOP 基础上“缝补”而来的，在处理复杂的函数式逻辑时，不如 Scala 或 Kotlin 自然。

### JVM、JDK、JRE三者关系

JDK(Java开发工具包) = JRE + 开发工具 JRE = JVM + 核心类库

### Java既是编译型也是解释性语言

Java 更准确地说是“先编译、后解释，并带有 JIT 动态编译优化”的混合执行模型。
- 编译性体现在：`.java` 源码先通过 `javac` 编译成平台无关的 `.class` 字节码。
- 解释性体现在：程序运行时，JVM 可以通过解释器逐条解释执行字节码。
- 性能优化体现在：JVM 会监测热点代码，例如频繁调用的方法或循环。当热点代码达到阈值后，JIT 即时编译器会在运行期把这部分字节码编译成本地机器码，并缓存到 JVM 的代码缓存区，后续直接执行机器码，而不是每次都解释执行。

### 编译型语言和解释型语言的区别

编译型语言：在程序执行之前，整个源代码会被编译成机器码或者字节码，生成可执行文件。执行时直接运行编译后的代码，速度快，但跨平台性较差。
解释型语言：在程序执行时，逐行解释执行源代码，不生成独立的可执行文件。通常由解释器动态解释并执行代码，跨平台性好，但执行速度相对较慢。

## 数据类型

### 八种基本数据类型

| 类型 | 占用空间 | 默认值 | 说明 |
| --- | --- | --- | --- |
| byte | 1 字节 | 0 | 整数类型 |
| short | 2 字节 | 0 | 整数类型 |
| int | 4 字节 | 0 | 最常用整数类型 |
| long | 8 字节 | 0L | 声明 long 字面量建议加 `L` |
| float | 4 字节 | 0.0f | 单精度浮点数，字面量需加 `F` 或 `f` |
| double | 8 字节 | 0.0d | 双精度浮点数，默认浮点类型 |
| char | 2 字节 | '\\u0000' | Unicode 字符 |
| boolean | JVM 规范未固定 | false | 只有 true 和 false |

### 为什么用 BigDecimal 不用 double

`double` 是二进制浮点数，无法精确表示很多十进制小数（0.1），容易出现精度误差
`BigDecimal` 使用任意精度的十进制表示，更适合精确计算。创建 `BigDecimal` 时应优先使用字符串或 `BigDecimal.valueOf()`，避免把已经产生误差的 `double` 直接传入构造器。

```java
BigDecimal a = new BigDecimal("0.1");
BigDecimal b = BigDecimal.valueOf(0.1);
```

### 数据类型转换方式

- 自动类型转换（隐式转换）：小范围类型转大范围类型，不会丢失数据
- 强制类型转换（显式转换）：大范围类型转小范围类型，可能出现溢出；`double` 转 `int` 会直接截断小数部分；`int` 转 `float` 也可能损失有效数字。
- 字符串转换：字符串转数字可以用 `Integer.parseInt()`、`Double.parseDouble()`；数字转字符串可以用 `String.valueOf()` 或 `Integer.toString()`。

### 对象引用转换的问题

向上转型是自动进行的，而且是安全的 子类 → 父类 Animal animal = dog;
向下转型需要手动进行。如果父类对象实际上并不是目标子类的实例，在转型时就会抛出异常(ClassCastException) Dog dog = (Dog) animal;
解决方式：使用 instanceof 检查 animal instanceof Dog

### 基本类型和包装类的区别，以及 Integer 缓存

基本类型直接存储值，性能高、内存开销小，不能为 `null`，也不能用于泛型。
包装类是对象，可以为 `null`，可以放入集合和泛型中，也提供了很多工具方法
为什么需要 `Integer`：
- 集合和泛型不能直接使用基本类型
- 包装类可以表示缺失值
- 包装类封装了常用方法
自动装箱和拆箱：
- 自动装箱：`int` 自动转为 `Integer`，本质通常是调用 `Integer.valueOf()`。
- 自动拆箱：`Integer` 自动转为 `int`，本质通常是调用 `intValue()`。
- 弊端：频繁装箱会创建对象或触发缓存查找，循环中可能带来性能开销；`Integer` 为 `null` 时自动拆箱会抛出 `NullPointerException`。
Integer 缓存：
- `Integer.valueOf()` 默认会缓存 `-128` 到 `127` 范围内的对象。
- 因此 `Integer a = 127; Integer b = 127; a == b` 通常为 `true`，而 `Integer a = 128; Integer b = 128; a == b` 通常为 `false`。

## 面向对象

三大特性：封装、继承、多态

- 封装：对外隐藏对象的内部细节，仅通过对象提供的接口与外界交互。目的是增强安全性和简化编程，使得对象更加独立
- 继承：代码复用的重要手段，使得结构更加清晰
- 多态：允许不同类的对象对同一消息作出响应。分为编译时多态（重载，同一类中有多个同名方法，它们具有不同的参数列表）和运行时多态（重写，子类能够提供对父类 / 接口中同名方法的具体实现）。它使得程序具有良好的灵活性和扩展性

### 面向对象的设计原则

- 单一职责原则（SRP）：一个类应该只负责一项职责
- 开放封闭原则（OCP）：软件实体应该对扩展开放，对修改封闭
- 里氏替换原则（LSP）：子类对象应该能够替换掉所有父类对象
- 接口隔离原则（ISP）：客户端不应该依赖那些它不需要的接口，即接口应该小而专
- 依赖倒置原则（DIP）：高层模块不应该依赖低层模块，都应该依赖于抽象；抽象不应该依赖于细节，细节应该依赖于抽象。例子：如果一个公司类包含部门类，应该考虑使用合成/聚合关系，而不是将公司类继承自部门类。
- 最少知识原则 (Law of Demeter)：一个对象应当对其他对象有最少的了解，只与其直接的朋友交互。

### 抽象类和普通类区别

| 特性 | 普通类 (Normal Class) | 抽象类 (Abstract Class) |
| --- | --- | --- |
| 关键字 | 无需特殊关键字 | 必须使用 abstract 声明 |
| 实例化 | 可以直接 new 对象 | 不能直接 new 对象 |
| 抽象方法 | 不能包含抽象方法 | 可以包含抽象方法（也可以没有） |
| 继承关系 | 可以被继承，也可以不被继承 | 必须被继承才有意义 |
| 实现要求 | 无强制要求 | 子类必须实现父类所有的抽象方法 |

### 抽象类和接口的区别

抽象类用于描述类的共同特性和行为。接口用于定义行为规范
| 特性 | 抽象类 (abstract class) | 接口 (interface) |
| --- | --- | --- |
| 继承/实现 | 子类使用 extends（只能继承一个） | 实现类使用 implements（可以实现多个） |
| 成员变量 | 可以有各种类型的变量（实例/静态变量） | 只能是公共静态常量（默认 public static final）必须赋初值，不能被修改 |
| 构造方法 | 可以有构造方法，供子类初始化使用 | 没有构造方法 |
| 方法实现 | 可以有抽象方法，也可以有普通具体方法 | 默认全是抽象方法，不用特地加abstract（Java 8 后支持 default 和 static） |
| 访问修饰符 | 方法可以是 public, protected, private | 方法默认且只能是 public（Java 9 支持 private） |

### 抽象类能加final修饰吗

不能，Java中的抽象类是用来被继承的，而final修饰符用于禁止类被继承或方法被重写

### 接口里面可以定义哪些方法

- 抽象方法
- 静态方法
- 默认方法 让接口在“保持兼容”的前提下，拥有方法实现能力
```java
default void sleep() {
    System.out.println("Sleeping...");
}
```
- 私有方法： 在 Java 9 中引入，用于在接口中为默认方法或其他私有方法提供辅助功能。这些方法不能被实现类访问，只能在接口内部使用。

### 静态变量

共享性
初始化：在类被加载时初始化，只会对其进行一次分配内存
访问方式：静态变量可以直接通过类名访问（推荐），也可以通过实例访问

### 静态方法

无实例依赖
访问静态成员，但不能直接访问非静态成员
多态性：不支持重写（不依赖对象存在，所以也就不存在“根据对象真实类型动态分派”），但可以被隐藏。程序在编译阶段就已经根据引用的类型决定好调用哪个方法了。这被称为静态绑定。如果父子类都有同名的静态方法，调用哪个只看引用的声明类型

### 非静态内部类和静态内部类的区别

| 特性 | 非静态内部类 (Inner Class) | 静态内部类 (Static Nested Class) |
| --- | --- | --- |
| 对外部类的依赖 | 强依赖。必须绑定到一个具体的外部类实例。 | 弱依赖。不依赖外部类实例，逻辑上只是“嵌套”在外面。 |
| 访问外部类成员 | 可以直接访问外部类所有成员（实例+静态）。 | 只能直接访问外部类的静态成员。 |
| 定义静态成员 | Java 16 以前禁止；Java 16+ 开始支持。 | 一直支持。可以定义静态常量、静态方法等。 |
| 实例化方式 | Outer.Inner i = new Outer().new Inner(); | Outer.StaticInner i = new Outer.StaticInner(); |
| 隐藏的 this 指针 | 包含一个指向外部类实例的引用 (Outer.this)。 | 不包含指向外部类实例的引用。 |
| 私有成员访问 | 直接访问 | 可以直接访问外部类的私有静态成员。 |
| 内存泄露风险 | 有风险。因为持有外部类引用，可能导致外部类无法回收。 | 无风险。因为它不持有外部类的引用。 |

### 非静态内部类可以直接访问外部方法，编译器是怎么做到的？

因为编译器在生成字节码时会为非静态内部类维护一个指向外部类实例的引用。同名冲突就近原则，或必须使用 外部类名.this.方法名() 的语法：Smartphone.this.consumeBattery(5);

## 关键字

### final 作用

- 修饰类：表示这个类不能被继承
- 修饰方法：用final修饰的方法不能在子类中被重写
- 修饰变量：当final修饰基本数据类型的变量时，该变量一旦被赋值就不能再改变。引用数据类型，这个引用变量不能再指向其他对象，但对象本身的内容是可以改变的

### static 修饰代码块

静态代码块在类加载时执行，且只执行一次（优于对象构造方法），用于初始化静态变量或执行类级别的预处理操作。多个静态代码块按定义顺序执行

## 深拷贝和浅拷贝

### 深拷贝和浅拷贝

- 浅拷贝会复制对象本身和其内部的基本数据类型字段值，对于引用类型字段，只复制引用而不复制引用指向的实际对象
- 深拷贝是指在复制对象的同时，将对象内部的所有引用类型字段的内容也复制一份，而不是共享引用

### 实现深拷贝的三种方法

- 实现 Cloneable 接口并重写 clone() 方法。这种方法要求对象及其所有引用类型字段都实现 Cloneable 接口，并且重写 clone() 方法。在 clone() 方法中，通过递归克隆引用类型字段来实现深拷贝。
- 使用序列化和反序列化。要求对象及其所有引用类型字段都实现 Serializable 接口
- 手动递归复制

## 泛型

class Box\<T\> `T` 就是一个类型占位符

### 为什么需要泛型

- 适用于多种数据类型执行相同的代码
- 泛型中的类型在使用时指定，不需要强制类型转换（类型安全，编译器会检查类型）。引入泛型，它将提供类型的约束，提供编译前的检查



# 对象

###  Java 创建对象有哪些方式

| 方式       | 核心原理       | 是否调用构造器？ | 特点与应用场景               |
| ---------- | -------------- | ---------------- | ---------------------------- |
| new 关键字 | JVM 指令       | 是               | 最标准、最常用，紧密耦合     |
| 反射       | 运行时类信息   | 是               | 灵活、解耦，常用于框架       |
| clone()    | 复制现有对象   | 否               | 基于原型创建副本             |
| 反序列化   | 从字节流恢复   | 否               | 用于持久化和网络通信         |
| 工厂模式   | 方法封装 (new) | 是               | 解耦，隐藏创建逻辑，控制实例 |

### new 出的对象什么时候回收

Java 对象是否能被回收，主流 JVM 主要看它**是否仍然“可达”，而不是简单看引用计数**。

1.  可达性分析：从 **GC Roots 出发沿引用链查找对象**，如果某个对象不可达，就具备被回收的条件。常见 GC Roots 包括**虚拟机栈中的局部变量、方法区中的静态变量、常量引用、JNI 引用等**。
2.  引用类型影响回收时机：**强引用存在**时对象不会被回收；**软引用**在内存不足时可能回收；**弱引用**下次 GC 通常会回收；**虚引用**主要用于跟踪对象回收。
3.  `finalize()` 不推荐使用：**它执行时机不确定**，可能导致性能和资源释放问题。现代 Java 更推荐使用 `try-with-resources`、显式关闭资源或 `Cleaner`。

### 如何获取私有对象

-   使用公共访问器方法（getter 方法）
-   反射机制。反射机制允许在运行时检查和修改类、方法、字段等信息，通过反射可以绕过 private 访问修饰符的限制来获取私有对象。

```java
        MyClass obj = new MyClass();
        // 获取 Class 对象
        Class<?> clazz = obj.getClass();
        // 获取私有字段
        Field privateField = clazz.getDeclaredField("privateField");
        // 设置可访问性
        privateField.setAccessible(true);
        // 获取私有字段的值
        String value = (String) privateField.get(obj);
        System.out.println(value);
```



# 反射

Java 反射机制是在**运行状态中**，对于任意一个类，都能够知道这个类中的**所有属性和方法**，对于任意一个对象，都能够调用它的任意一个方法和属性

反射具有以下特性：

1.  运行时类信息访问：反射机制允许程序在运行时获取**类的完整结构信息**，包括类名、包名、父类、实现的接口、构造函数、方法和字段等。
2.  动态对象创建：可以使用反射 **API 动态创建对象实例**，即使编译时不知道具体类名。实际开发中推荐使用 `Constructor.newInstance()`。
3.  动态方法调用：可以在运行时**动态地调用对象的方法，包括私有方法**。这通过Method类的invoke()方法实现，允许你传入对象实例和参数值来执行方法。
4.  访问和修改字段值：反射还允许程序在运行时**访问和修改对象的字段值，即使是私有的**。这是通过Field类的get()和set()方法完成的。

反射创建对象建议使用 `Constructor.newInstance()`，不要再使用 `Class.newInstance()`，因为后者在 JDK 9 后已过时，只能调用**无参 public 构造器，异常处理也不够清晰**。

```java
Constructor<MyClass> constructor = MyClass.class.getDeclaredConstructor();
constructor.setAccessible(true);
MyClass obj = constructor.newInstance();
```

### 反射在你平时写代码或者框架中的应用场景有哪些

-   加载数据库驱动

-   配置文件加载

    Spring 框架的 IOC（动态加载管理 Bean），Spring通过配置文件配置各种各样的bean，你需要用到哪些bean就配哪些，spring容器就会根据你的需求去动态加载，你的程序就能健壮地运行。

    Spring通过XML配置模式装载Bean的过程：

    -   将程序中所有**XML或properties配置文件加载入内存**
    -   Java类里面解析xml或者properties里面的内容，得到**对应实体类的字节码字符串以及相关的属性信息**
    -   使用反射机制，根据这个字符串**获得某个类的Class实例**
    -   **动态配置实例的属性**

# 注解

### Java注解的原理

注解本质是一个继承了 `java.lang.annotation.Annotation` 的特殊接口。例如：

```java
import java.lang.annotation.*;

@Retention(RetentionPolicy.RUNTIME) // 运行时还能读取到这个注解
@Target(ElementType.METHOD)          // 这个注解只能用在方法上
public @interface MyLog {
    String value() default "";
    int level() default 1;
}

    @MyLog("新增用户")
    public void addUser() {
        System.out.println("执行 addUser 方法");
    }
    等价于
    @MyLog(value = "新增用户")
    因为属性名叫 value 时，可以省略 value =。
```

编译后，注解信息会按照保留策略写入**源码、`.class` 文件或运行时元数据**中。只有 `@Retention(RetentionPolicy.RUNTIME)` 的注解才能在运行时通过反射读取。

运行时通过**反射获取注解**时，**JVM 会返回一个注解代理对象**。调用注解属性方法时，底层会从保存注解属性值的 Map 中取值，这也是为什么注解方法看起来像接口方法，但调用时能返回配置值。

```java
定义注解 注解本质上是 Java 给程序元素添加的元数据。
   ↓
使用注解
   ↓
编译器把注解信息写进 .class 文件
   ↓
运行时通过反射读取注解
   ↓
JDK 返回一个注解代理对象 它代理的是“注解接口”，和 Spring 代理对象不同
   ↓
调用注解属性方法，从内部 Map 中取值
   ↓
框架根据注解做额外逻辑，例如生成代理、注册 Bean、开启事务

Method method = UserService.class.getMethod("addUser");

MyLog myLog = method.getAnnotation(MyLog.class);

System.out.println(myLog.value());
System.out.println(myLog.level());

Spring 扫描 @Service
扫描 class
   ↓
读取类上的注解
   ↓
发现 @Service
   ↓
创建 UserService 对象
   ↓
放入 Spring 容器
```

-   注解解析的底层实现

    注解解析依赖“字节码中的注解元数据 + 反射 API”。

    -   源码级别注解：**只存在于源码中，编译后不会保留**，例如 `@Override`，对应 `RetentionPolicy.SOURCE`。
    -   类文件级别注解：保留在 `.class` 文件中，但运行时默认不可见，对应 `RetentionPolicy.CLASS`。
    -   运行时注解：保留在 `.class` 文件中，并且**可以通过反射访问**，对应 `RetentionPolicy.RUNTIME`。

    当注解保留到运行时，编译器会把注解信息写入字节码的属性表，例如 `RuntimeVisibleAnnotations`、`RuntimeInvisibleAnnotations`、`RuntimeVisibleParameterAnnotations` 等。JVM 加载类后，反射 API 可以读取这些元数据。

    常见解析流程：

    ```java
    Class<?> clazz = MyClass.class;
    MyAnnotation annotation = clazz.getAnnotation(MyAnnotation.class);
    if (annotation != null) {
        System.out.println(annotation.value());
    }
    ```

    反射中与注解相关的核心接口是 `java.lang.reflect.AnnotatedElement`，`Class`、`Method`、`Field`、`Constructor` 等都实现了它。常用方法包括：

    -   `getAnnotation(Class<T> annotationClass)`：获取指定类型的注解。
    -   `getAnnotations()`：获取所有注解。
    -   `isAnnotationPresent(Class<? extends Annotation> annotationClass)`：判断是否存在指定注解。

    总结：`@Retention` 决定注解能保留到哪个阶段；运行时注解会被写入字节码并由 JVM 加载；反射 API 负责读取这些元数据并返回注解代理对象。

-   Java注解的作用域

    注解的作用域（Scope）指的是注解可以应用在哪些程序元素上，例如类、方法、字段等。Java注解的作用域可以分为三种：

    1.  **类**级别作用域：用于描述类的注解，通常放置在类定义的上面，可以用来指定类的一些属性，如类的访问级别、继承关系、注释等。
    2.  **方法**级别作用域：用于描述方法的注解，通常放置在方法定义的上面，可以用来指定方法的一些属性，如方法的访问级别、返回值类型、异常类型、注释等。
    3.  **字段**级别作用域：用于描述字段的注解，通常放置在字段定义的上面，**可以用来指定字段的一些属性，如字段的访问级别、默认值、注释等。**

    Java还提供了其他一些注解作用域，例如**构造函数作用域和局部变量作用域**



# 异常

Java 的异常体系以 `Throwable` 为根，主要分为 `Error` 和 `Exception`。

```
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

1.  `Error`：表示 **JVM 或运行环境层面**的严重错误，程序通常无法恢复，也不建议捕获处理，例如 `OutOfMemoryError`、`StackOverflowError`。
2.  `Checked Exception`：受检异常，**编译期强制要求捕获或声明抛出**，通常表示外部环境问题，例如文件不存在、网络异常、数据库异常。
3.  `RuntimeException`：**运行时异常，编译期不强制处理**，通常由程序逻辑错误导致，例如空指针、类型转换错误、数组越界等。



# Object

## == 与 equals 区别

对于字符串变量来说，使用"=="和"equals"比较字符串时，其比较方法不同。"=="比较两个变量本身的值，即两个对象在内存中的首地址，"equals"比较字符串包含内容是否相同。

对于非字符串变量来说，如果没有对equals()进行重写的话，"==" 和 "equals"方法的作用是相同的，比较两个引用变量是否指向同一个对象。

## hashcode和equals

如果重写了 `equals()`，通常必须同时重写 `hashCode()`。

是 `HashMap`、`HashSet` 等哈希集合会先根据 `hashCode()` 定位桶，再用 `equals()` 判断对象是否真正相等。如果只重写 `equals()` 不重写 `hashCode()`，可能导致**逻辑相等的对象被放到不同桶里，出现查找失败或重复元素**。

## String、StringBuffer、StringBuilder的区别和联系

| 特性     | String           | StringBuilder    | StringBuffer     |
| -------- | ---------------- | ---------------- | ---------------- |
| 不可变性 | 不可变           | 可变             | 可变             |
| 线程安全 | 是（因不可变）   | 否               | 是（同步方法）   |
| 性能     | 低（频繁修改时） | 高（单线程）     | 中（多线程安全） |
| 适用场景 | 静态字符串       | 单线程动态字符串 | 多线程动态字符串 |

补充说明：

-   `String` 不可变，每次拼接如果生成新字符串，都可能创建新对象。字符串常量会进入字符串常量池。
-   `StringBuilder` 和 `StringBuffer` 内部维护**可变字符序列**，频繁拼接时比 `String` 更合适。
-   `StringBuffer` 的**关键方法带有 `synchronized`，线程安全但性能略低**。
-   JDK 9 之后 `String` 底层从 `char[]` 优化为 `byte[] + coder`，对 Latin-1 字符更省内存；但面试回答核心仍然是“String 不可变，Builder/Buffer 可变，Buffer 线程安全”。



# Java新特性

### Java8新特性

| 特性名称                 | 描述                                                       | 示例或说明                                                   |
| ------------------------ | ---------------------------------------------------------- | ------------------------------------------------------------ |
| Lambda 表达式            | 简化匿名内部类，支持函数式编程                             | (a, b) -> a + b 代替匿名类实现接口                           |
| 函数式接口               | 仅含一个抽象方法的接口，可用 @FunctionalInterface 注解标记 | Runnable, Comparator, 或自定义接口 @FunctionalInterface interface MyFunc { void run(); } |
| Stream API               | 提供链式操作处理集合数据，支持并行处理                     | list.stream().filter(x -> x > 0).collect(Collectors.toList()) |
| Optional 类              | 封装可能为 null 的对象，减少空指针异常                     | Optional.ofNullable(value).orElse("default")                 |
| 方法引用                 | 简化 Lambda 表达式，直接引用现有方法                       | System.out::println 等价于 x -> System.out.println(x)        |
| 接口的默认方法与静态方法 | 接口可定义默认实现和静态方法，增强扩展性                   | interface A { default void print() { System.out.println("默认方法"); } } |
| 并行数组排序             | 使用多线程加速数组排序                                     | Arrays.parallelSort(array)                                   |
| 重复注解                 | 允许同一位置多次使用相同注解                               | @Repeatable 注解配合容器注解使用                             |
| 类型注解                 | 注解可应用于更多位置（如泛型、异常等）                     | List<@NonNull String> list                                   |
| CompletableFuture        | 增强异步编程能力，支持链式调用和组合操作                   | CompletableFuture.supplyAsync(() -> "result").thenAccept(System.out::println) |

### Lambda 表达式

Lambda 表达式它是一种简洁的语法，用于创建匿名函数，主要用于简化函数式接口（只有一个抽象方法的接口）的使用。其基本语法有以下两种形式：

(parameters) -> expression：当 Lambda 体只有一个表达式时使用，表达式的结果会作为返回值。

(parameters) -> { statements; }：当 Lambda 体包含多条语句时，需要使用大括号将语句括起来，若有返回值则需要使用 return 语句。

传统的匿名内部类实现方式代码较为冗长，而 Lambda 表达式可以用更简洁的语法实现相同的功能。比如，使用匿名内部类实现 Runnable 接口

```java
public class AnonymousClassExample {
    public static void main(String[] args) {
        Thread t1 = new Thread(new Runnable() {
            @Override
            public void run() {
                System.out.println("Running using anonymous class");
            }
        });
        t1.start();
    }
}
```

使用 Lambda 表达式实现相同功能：

```java
public class LambdaExample {
    public static void main(String[] args) {
        Thread t1 = new Thread(() -> System.out.println("Running using lambda expression"));
        t1.start();
    }
}

List<Integer> evenNumbers = numbers.stream()
                                           .filter(n -> n % 2 == 0)
                                           .collect(Collectors.toList());
                                           
interface Calculator {
    int calculate(int a, int b);
}

public class FunctionalProgrammingExample {
    public static int operate(int a, int b, Calculator calculator) {
        return calculator.calculate(a, b);
    }

    public static void main(String[] args) {
        // 使用 Lambda 表达式传递加法函数
        int sum = operate(3, 5, (x, y) -> x + y);
        System.out.println("Sum: " + sum);

        // 使用 Lambda 表达式传递乘法函数
        int product = operate(3, 5, (x, y) -> x * y);
        System.out.println("Product: " + product);
    }
}
```

虽然 Lambda 表达式优点蛮多的，不过也有一些缺点，比如会增加调试困难，因为 Lambda 表达式是匿名的，在调试时很难定位具体是哪个 Lambda 表达式出现了问题。尤其是当 Lambda 表达式嵌套使用或者比较复杂时，调试难度会进一步增加。

### stream的API

```java
List<String> originalList = Arrays.asList("apple", "fig", "banana", "kiwi");
List<String> filteredList = originalList.stream()
                                        .filter(s -> s.length() > 3)
                                        .collect(Collectors.toList());
                                        
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
int sum = numbers.stream()
                 .mapToInt(Integer::intValue)
                 .sum();
```

### Stream流的并行API是什么

并行流（ParallelStream）就是将源数据分为**多个子流对象进行多线程操作**，然后将处理的结果再汇总为一个流对象，底层是使用通用的 **fork/join 池来实现**，即将一个任务拆分成多个“小任务”并行计算，再把多个“小任务”的结果合并成总的计算结果

对**CPU密集型的任务来说**，并行流使用**ForkJoinPool**线程池，为每个CPU分配一个任务，这是非常有效率的，但是如果任务不是CPU密集的，而是I/O密集的，并且任务数相对线程数比较大，那么直接用ParallelStream并不是很好的选择。

### Java 9 到 Java 21 常见新特性

| 版本        | 代表特性                                                     | 面试关注点                                                   |
| ----------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Java 9      | 模块系统 JPMS、接口私有方法、try-with-resources 改进         | 模块化可以更明确地管理依赖和封装边界                         |
| Java 10     | `var` 局部变量类型推断                                       | 只适用于局部变量，不能用于成员变量和方法参数                 |
| Java 14/16  | Record                                                       | 用于不可变数据载体，减少 getter、构造器、equals/hashCode 样板代码 |
| Java 17 LTS | Sealed Class、增强 switch、模式匹配持续演进                  | 限制类继承范围，适合建模有限类型体系                         |
| Java 21 LTS | 虚拟线程、Record Pattern、Pattern Matching for switch、Sequenced Collections | 虚拟线程是高并发 I/O 场景重点，能用更低成本承载大量阻塞任务  |

Java 21 里最值得重点准备的是虚拟线程。它属于 Project Loom 的成果，目标是降低线程创建和阻塞成本，让同步阻塞风格代码也能支撑大量并发连接。但它不是用来提升 CPU 密集型计算性能的，适合 I/O 密集型场景。

# 序列化

### 怎么把一个对象从一个jvm转移到另一个jvm

-   使用序列化和反序列化：将对象序列化为字节流，并将其发送到另一个 JVM，然后在另一个 **JVM 中反序列化字节流恢复对象**。这可以通过 Java 的 ObjectOutputStream 和 ObjectInputStream 来实现。
-   使用消息传递机制：**利用消息传递机制**，比如使用消息队列（如 RabbitMQ、Kafka）或者通过网络套接字进行通信，将对象从一个 JVM 发送到另一个。这需要**自定义协议**来序列化对象并在另一个 JVM 中反序列化。
-   使用远程方法调用（RPC）：可以使用远程方法调用框架，如 gRPC，来实现对象在不同 JVM 之间的传输。远程方法调用可以让你在分布式系统中调用远程 JVM 上的对象的方法
-   使用共享数据库或缓存：将**对象存储在共享数据库**（如 MySQL、PostgreSQL）或共享缓存（如 Redis）中，让不同的 JVM 可以访问这些共享数据。这种方法适用于需要共享数据但不需要直接传输对象的场景。

### 序列化和反序列化让你自己实现你会怎么做?

Java 默认的序列化虽然实现方便，但却存在安全漏洞、不跨语言以及性能差等缺陷。

-   **无法跨语言**： Java 序列化目前只适用基于 Java 语言实现的框架，其它语言大部分都没有使用 Java 的序列化框架，也没有实现 Java 序列化这套协议
-   容易被攻击：Java 序列化是不安全的，我们知道对象是通过在 ObjectInputStream 上调用 readObject() 方法进行反序列化的，这个方法其实是一个神奇的构造器，它可以将类路径上几乎所有实现了 Serializable 接口的对象都实例化。这也就意味着，在反序列化字节流的过程中，**该方法可以执行任意类型的代码，这是非常危险的**。
-   序列化后的流太大：序列化后的二进制流大小能体现序列化的性能。序列化后的二进制数组越大，占用的存储空间就越多，**存储硬件的成本就越高**。如果我们是进行网络传输，则占用的带宽就更多，这时就会**影响到系统的吞吐量**。

我会考虑用主流序列化框架，比如FastJson、Protobuf来替代Java 序列化。

如果追求性能的话，Protobuf 序列化框架会比较合适，Protobuf 的这种数据存储格式，不仅压缩存储数据的效果好， 在编码和解码的性能方面也很高效。Protobuf 的编码和解码过程结合.proto 文件格式，加上 Protocol Buffer 独特的编码格式，只需要简单的数据运算以及位移等操作就可以完成编码与解码。可以说 Protobuf 的整体性能非常优秀。



# 设计模式

### volatile和synchronized如何实现单例模式

```java
public class SingleTon {

    // volatile 关键字修饰变量 防止指令重排序
    // 它禁止这种危险顺序：分配内存 instance 指向内存 初始化对象
    // 必须保证效果上是：分配内存 初始化对象 instance 指向内存
    private static volatile SingleTon instance = null;
    private SingleTon(){}
     
    public static  SingleTon getInstance(){
        if(instance == null){
            //同步代码块 只有在第一次获取对象的时候会执行到
            //第二次及以后访问时 instance变量均非null故不会往下执行了 直接返回啦
            synchronized(SingleTon.class){
                if(instance == null){
                    instance = new SingleTon();
                }
            }
        }
        return instance;
    }
}
```

正确的双重检查锁定模式需要使用 `volatile`。原因是 `instance = new SingleTon()` 不是一个简单的原子动作，通常包含分配内存、初始化对象、把引用赋给变量几个步骤。如果发生指令重排，其他**线程可能拿到一个尚未初始化完成的对象**。

-   保证可见性：一个线程初始化完成后，其他线程能及时看到 `instance` 的最新值。
-   禁止指令重排序：避免引用赋值先于对象初始化完成。

另外，单例还可能被反射和反序列化破坏。实际开发中如果没有延迟加载要求，也可以使用枚举单例，它天然防反射和反序列化破坏。

### 动态代理和反射有什么关系

动态代理是代理模式在 Java 中的典型实现，常用于 AOP、事务、日志、权限校验等场景。

-   JDK 动态代理基于接口，核心 API 是 `Proxy.newProxyInstance()` 和 `InvocationHandler`。方法调用会被转发到 `invoke()` 方法中。
-   JDK 动态代理底层会使用反射调用目标方法，例如 `method.invoke(target, args)`。
-   Spring AOP 中，如果目标类实现了接口，默认可以使用 JDK 动态代理；如果没有接口，通常使用 CGLIB 基于子类生成代理。

简答：反射提供了运行时获取类信息和调用方法的能力，动态代理利用这些能力在**不修改原对象代码的情况下增强方法行为**。

### 代理模式和适配器模式有什么区别

-   目的不同：代理模式主要关注控制对对象的访问，而适配器模式则用于接口转换，使不兼容的类能够一起工作。

-   结构不同：代理模式一般包含抽象主题、真实主题和代理三个角色，适配器模式包含目标接口、适配器和被适配者三个角色。

    ```java
    public class UserServiceProxy implements UserService {
    
        private final UserService target;
    
        public UserServiceProxy(UserService target) {
            this.target = target;
        }
    
        @Override
        public void addUser() {
            System.out.println("代理增强：权限校验");
    
            target.addUser();
    
            System.out.println("代理增强：记录日志");
        }
    }
    
    public class Main {
        public static void main(String[] args) {
        // 抽象主题：接口
            UserService real = new UserServiceImpl();// 真实主题
    
            UserService proxy = new UserServiceProxy(real); // 代理
    
            proxy.addUser();
        }
    }
    ```

    ```java
    public class AliPayAdapter implements PayService {
    // 接口： 目标接口
        private final AliPaySDK aliPaySDK;// 被适配者
    
        public AliPayAdapter(AliPaySDK aliPaySDK) {
            this.aliPaySDK = aliPaySDK;
        }
    
        @Override
        public void pay(double amount) {
            String money = String.valueOf(amount);
    
            aliPaySDK.aliPay(money);
        }
    }
    
    public class Main {
        public static void main(String[] args) {
            AliPaySDK aliPaySDK = new AliPaySDK();
    
            PayService payService = new AliPayAdapter(aliPaySDK);
    
            payService.pay(100.0);
        }
    }
    ```

-   应用场景不同：代理模式常用于添加额外功能或控制对对象的访问，适配器模式常用于让不兼容的接口协同工作。



# I/O

### BIO、NIO、AIO区别

-   BIO（blocking IO）：就是传统的 java.io 包，它是基于流模型实现的，交互的方式是**同步、阻塞方式**，也就是说在读入输入流或者输出流时，在读写动作完成之前，线程会一直阻塞在那里，它们之间的调用是可靠的线性顺序。优点是代码比较简单、直观；缺点是 IO 的效率和扩展性很低，容易成为应用性能瓶颈。

-   NIO（non-blocking IO）：Java 1.4 引入的 `java.nio` 包，核心是 `Channel`、`Buffer`、`Selector`。它可以构建**同步非阻塞的 I/O 多路复用模型**，也是 Netty 常用模型的基础。

    NIO 的重点：

    -   `Channel`：双向通道，数据可以从**通道读到缓冲区**，也可以从缓冲区写入通道。
    -   `Buffer`：缓冲区，**NIO 面向缓冲区操作**，而传统 BIO 面向流操作。
    -   `Selector`：选择器，一个线程可以监听多个 Channel 的连接、读、写等就绪事件。

    为什么说 NIO 是同步非阻塞：

    -   **非阻塞**指 Channel 可以设置为非阻塞模式，线程发起读写时，如果没有数据就绪，不必一直卡在读写调用上。
    -   同步指应用线程仍然需要**主动调用 `Selector.select()` 等方法等待和获取就绪事件**，并自己处理读写。`select()` 可以阻塞等待事件，但这不是 AIO 那种操作完成后由系统回调通知的异步模型。

-   AIO（Asynchronous IO）：Java 1.7 引入，提供异步非阻塞 I/O。应用发起 I/O 操作后可以直接返回，等后台处理完成后，操作系统再通过**回调或通知机制**让应用继续处理结果。



# 其他

### 有一个学生类，想按照分数排序，再按学号排序，应该怎么做

```java
public class Student implements Comparable<Student> {
    private int id;
    private int score;

    // 构造方法和其他属性、方法省略

    @Override
    public int compareTo(Student other) {
        if (this.score != other.score) {
            return Integer.compare(other.score, this.score); // 按照分数降序排序
        } else {
            return Integer.compare(this.id, other.id); // 如果分数相同，则按照学号升序排序
        }
    }
}
```
