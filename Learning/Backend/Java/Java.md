# Java

# 概念
<details>
<summary>Java的特点</summary>
	- 平台无关性（字节码、JVM）
	- 面向对象（封装、继承、多态、抽象）
	- 自动内存管理（JVM 垃圾回收机制）
	- 生态成熟（Spring、MyBatis、Maven、JUC 等生态）
	- 安全性与健壮性（字节码校验、异常机制、强类型检查和较好的向后兼容性）
</details>
<details>
<summary>Java 的优势和劣势</summary>
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
</details>
<details>
<summary>JVM、JDK、JRE三者关系</summary>
	JDK(Java开发工具包) = JRE + 开发工具 JRE = JVM + 核心类库
</details>
<details>
<summary>Java既是编译型也是解释性语言</summary>
	Java 更准确地说是“先编译、后解释，并带有 JIT 动态编译优化”的混合执行模型。
	- 编译性体现在：`.java` 源码先通过 `javac` 编译成平台无关的 `.class` 字节码。
	- 解释性体现在：程序运行时，JVM 可以通过解释器逐条解释执行字节码。
	- 性能优化体现在：JVM 会监测热点代码，例如频繁调用的方法或循环。当热点代码达到阈值后，JIT 即时编译器会在运行期把这部分字节码编译成本地机器码，并缓存到 JVM 的代码缓存区，后续直接执行机器码，而不是每次都解释执行。
</details>
<details>
<summary>编译型语言和解释型语言的区别</summary>
	编译型语言：在程序执行之前，整个源代码会被编译成机器码或者字节码，生成可执行文件。执行时直接运行编译后的代码，速度快，但跨平台性较差。
	解释型语言：在程序执行时，逐行解释执行源代码，不生成独立的可执行文件。通常由解释器动态解释并执行代码，跨平台性好，但执行速度相对较慢。
</details>

# 数据类型

<details>
<summary>八种基本数据类型</summary>
	<table header-row="true" header-column="false">
<tr>
<td>类型</td>
<td>占用空间</td>
<td>默认值</td>
<td>说明</td>
</tr>
<tr>
<td>byte</td>
<td>1 字节</td>
<td>0</td>
<td>整数类型</td>
</tr>
<tr>
<td>short</td>
<td>2 字节</td>
<td>0</td>
<td>整数类型</td>
</tr>
<tr>
<td>int</td>
<td>4 字节</td>
<td>0</td>
<td>最常用整数类型</td>
</tr>
<tr>
<td>long</td>
<td>8 字节</td>
<td>0L</td>
<td>声明 long 字面量建议加 `L`</td>
</tr>
<tr>
<td>float</td>
<td>4 字节</td>
<td>0.0f</td>
<td>单精度浮点数，字面量需加 `F` 或 `f`</td>
</tr>
<tr>
<td>double</td>
<td>8 字节</td>
<td>0.0d</td>
<td>双精度浮点数，默认浮点类型</td>
</tr>
<tr>
<td>char</td>
<td>2 字节</td>
<td>'\\u0000'</td>
<td>Unicode 字符</td>
</tr>
<tr>
<td>boolean</td>
<td>JVM 规范未固定</td>
<td>false</td>
<td>只有 true 和 false</td>
</tr>
	</table>
</details>
<details>
<summary>为什么用 BigDecimal 不用 double</summary>
	`double` 是二进制浮点数，无法精确表示很多十进制小数（0.1），容易出现精度误差
	`BigDecimal` 使用任意精度的十进制表示，更适合精确计算。创建 `BigDecimal` 时应优先使用字符串或 `BigDecimal.valueOf()`，避免把已经产生误差的 `double` 直接传入构造器。
	```java
BigDecimal a = new BigDecimal("0.1");
BigDecimal b = BigDecimal.valueOf(0.1);
	```
</details>
<details>
<summary>数据类型转换方式</summary>
	- 自动类型转换（隐式转换）：小范围类型转大范围类型，不会丢失数据
	- 强制类型转换（显式转换）：大范围类型转小范围类型，可能出现溢出；`double` 转 `int` 会直接截断小数部分；`int` 转 `float` 也可能损失有效数字。
	- 字符串转换：字符串转数字可以用 `Integer.parseInt()`、`Double.parseDouble()`；数字转字符串可以用 `String.valueOf()` 或 `Integer.toString()`。
</details>
<details>
<summary>对象引用转换的问题</summary>
	向上转型是自动进行的，而且是安全的 子类 → 父类 Animal animal = dog;
	向下转型需要手动进行。如果父类对象实际上并不是目标子类的实例，在转型时就会抛出异常(ClassCastException) Dog dog = (Dog) animal;
	解决方式：使用 instanceof 检查 animal instanceof Dog
</details>
<details>
<summary>基本类型和包装类的区别，以及 Integer 缓存</summary>
	基本类型直接存储值，性能高、内存开销小，不能为 `null`，也不能用于泛型。<br>包装类是对象，可以为 `null`，可以放入集合和泛型中，也提供了很多工具方法
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
</details>

# 面向对象

三大特性：封装、继承、多态

- 封装：对外隐藏对象的内部细节，仅通过对象提供的接口与外界交互。目的是增强安全性和简化编程，使得对象更加独立
- 继承：代码复用的重要手段，使得结构更加清晰
- 多态：允许不同类的对象对同一消息作出响应。分为编译时多态（重载，同一类中有多个同名方法，它们具有不同的参数列表）和运行时多态（重写，子类能够提供对父类 / 接口中同名方法的具体实现）。它使得程序具有良好的灵活性和扩展性

<details>
<summary>面向对象的设计原则</summary>
	- 单一职责原则（SRP）：一个类应该只负责一项职责
	- 开放封闭原则（OCP）：软件实体应该对扩展开放，对修改封闭
	- 里氏替换原则（LSP）：子类对象应该能够替换掉所有父类对象
	- 接口隔离原则（ISP）：客户端不应该依赖那些它不需要的接口，即接口应该小而专
	- 依赖倒置原则（DIP）：高层模块不应该依赖低层模块，都应该依赖于抽象；抽象不应该依赖于细节，细节应该依赖于抽象。例子：如果一个公司类包含部门类，应该考虑使用合成/聚合关系，而不是将公司类继承自部门类。
	- 最少知识原则 (Law of Demeter)：一个对象应当对其他对象有最少的了解，只与其直接的朋友交互。
</details>
<details>
<summary>抽象类和普通类区别</summary>
	<table header-row="true" header-column="false">
<tr>
<td>特性</td>
<td>普通类 (Normal Class)</td>
<td>抽象类 (Abstract Class)</td>
</tr>
<tr>
<td>关键字</td>
<td>无需特殊关键字</td>
<td>必须使用 abstract 声明</td>
</tr>
<tr>
<td>实例化</td>
<td>可以直接 new 对象</td>
<td>不能直接 new 对象</td>
</tr>
<tr>
<td>抽象方法</td>
<td>不能包含抽象方法</td>
<td>可以包含抽象方法（也可以没有）</td>
</tr>
<tr>
<td>继承关系</td>
<td>可以被继承，也可以不被继承</td>
<td>必须被继承才有意义</td>
</tr>
<tr>
<td>实现要求</td>
<td>无强制要求</td>
<td>子类必须实现父类所有的抽象方法</td>
</tr>
	</table>
</details>
<details>
<summary>抽象类和接口的区别</summary>
	抽象类用于描述类的共同特性和行为。接口用于定义行为规范
	<table header-row="true" header-column="false">
<tr>
<td>特性</td>
<td>抽象类 (abstract class)</td>
<td>接口 (interface)</td>
</tr>
<tr>
<td>继承/实现</td>
<td>子类使用 extends（只能继承一个）</td>
<td>实现类使用 implements（可以实现多个）</td>
</tr>
<tr>
<td>成员变量</td>
<td>可以有各种类型的变量（实例/静态变量）</td>
<td>只能是公共静态常量（默认 public static final）必须赋初值，不能被修改</td>
</tr>
<tr>
<td>构造方法</td>
<td>可以有构造方法，供子类初始化使用</td>
<td>没有构造方法</td>
</tr>
<tr>
<td>方法实现</td>
<td>可以有抽象方法，也可以有普通具体方法</td>
<td>默认全是抽象方法，不用特地加abstract（Java 8 后支持 default 和 static）</td>
</tr>
<tr>
<td>访问修饰符</td>
<td>方法可以是 public, protected, private</td>
<td>方法默认且只能是 public（Java 9 支持 private）</td>
</tr>
	</table>
</details>
<details>
<summary>抽象类能加final修饰吗</summary>
	不能，Java中的抽象类是用来被继承的，而final修饰符用于禁止类被继承或方法被重写
</details>
<details>
<summary>接口里面可以定义哪些方法</summary>
	- 抽象方法
	- 静态方法
	- 默认方法 让接口在“保持兼容”的前提下，拥有方法实现能力
	```java
default void sleep() {
        System.out.println("Sleeping...");
}
	```
	- 私有方法： 在 Java 9 中引入，用于在接口中为默认方法或其他私有方法提供辅助功能。这些方法不能被实现类访问，只能在接口内部使用。
</details>
<details>
<summary>静态变量</summary>
	共享性
	初始化：在类被加载时初始化，只会对其进行一次分配内存
	访问方式：静态变量可以直接通过类名访问（推荐），也可以通过实例访问
</details>
<details>
<summary>静态方法</summary>
	无实例依赖
	访问静态成员，但不能直接访问非静态成员
	多态性：不支持重写（不依赖对象存在，所以也就不存在“根据对象真实类型动态分派”），但可以被隐藏。程序在编译阶段就已经根据引用的类型决定好调用哪个方法了。这被称为静态绑定。如果父子类都有同名的静态方法，调用哪个只看引用的声明类型
</details>
<details>
<summary>非静态内部类和静态内部类的区别</summary>
	<table header-row="true" header-column="false">
<tr>
<td>特性</td>
<td>非静态内部类 (Inner Class)</td>
<td>静态内部类 (Static Nested Class)</td>
</tr>
<tr>
<td>对外部类的依赖</td>
<td>强依赖。必须绑定到一个具体的外部类实例。</td>
<td>弱依赖。不依赖外部类实例，逻辑上只是“嵌套”在外面。</td>
</tr>
<tr>
<td>访问外部类成员</td>
<td>可以直接访问外部类所有成员（实例+静态）。</td>
<td>只能直接访问外部类的静态成员。</td>
</tr>
<tr>
<td>定义静态成员</td>
<td>Java 16 以前禁止；Java 16+ 开始支持。</td>
<td>一直支持。可以定义静态常量、静态方法等。</td>
</tr>
<tr>
<td>实例化方式</td>
<td>Outer.Inner i = new Outer().new Inner();</td>
<td>Outer.StaticInner i = new Outer.StaticInner();</td>
</tr>
<tr>
<td>隐藏的 this 指针</td>
<td>包含一个指向外部类实例的引用 (Outer.this)。</td>
<td>不包含指向外部类实例的引用。</td>
</tr>
<tr>
<td>私有成员访问</td>
<td>直接访问</td>
<td>可以直接访问外部类的私有静态成员。</td>
</tr>
<tr>
<td>内存泄露风险</td>
<td>有风险。因为持有外部类引用，可能导致外部类无法回收。</td>
<td>无风险。因为它不持有外部类的引用。</td>
</tr>
	</table>
</details>
<details>
<summary>非静态内部类可以直接访问外部方法，编译器是怎么做到的？</summary>
	因为编译器在生成字节码时会为非静态内部类维护一个指向外部类实例的引用。同名冲突就近原则，或必须使用 外部类名.this.方法名() 的语法：Smartphone.this.consumeBattery(5);
</details>

# 关键字

<details>
<summary>final 作用</summary>
	- 修饰类：表示这个类不能被继承
	- 修饰方法：用final修饰的方法不能在子类中被重写
	- 修饰变量：当final修饰基本数据类型的变量时，该变量一旦被赋值就不能再改变。引用数据类型，这个引用变量不能再指向其他对象，但对象本身的内容是可以改变的
</details>
<details>
<summary>static 修饰代码块</summary>
	静态代码块在类加载时执行，且只执行一次（优于对象构造方法），用于初始化静态变量或执行类级别的预处理操作。多个静态代码块按定义顺序执行
</details>

# 深拷贝和浅拷贝

<details>
<summary>深拷贝和浅拷贝</summary>
	- 浅拷贝会复制对象本身和其内部的基本数据类型字段值，对于引用类型字段，只复制引用而不复制引用指向的实际对象
	- 深拷贝是指在复制对象的同时，将对象内部的所有引用类型字段的内容也复制一份，而不是共享引用
</details>
<details>
<summary>实现深拷贝的三种方法</summary>
	- 实现 Cloneable 接口并重写 clone() 方法。这种方法要求对象及其所有引用类型字段都实现 Cloneable 接口，并且重写 clone() 方法。在 clone() 方法中，通过递归克隆引用类型字段来实现深拷贝。
	- 使用序列化和反序列化。要求对象及其所有引用类型字段都实现 Serializable 接口
	- 手动递归复制
</details>

# 泛型

class Box\<T\> `T` 就是一个类型占位符

<details>
<summary>为什么需要泛型</summary>
	- 适用于多种数据类型执行相同的代码
	- 泛型中的类型在使用时指定，不需要强制类型转换（类型安全，编译器会检查类型）。引入泛型，它将提供类型的约束，提供编译前的检查
</details>
