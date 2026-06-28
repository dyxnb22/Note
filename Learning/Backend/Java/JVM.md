# JVM

# JVM 内存区域
<details>
<summary>JVM 运行时数据区有哪些？</summary>
	JVM 运行时数据区可以按线程是否共享来记：
	- 程序计数器：线程私有，记录当前线程正在执行的字节码指令地址。
	- Java 虚拟机栈：线程私有，保存栈帧、局部变量表、操作数栈、返回地址。
	- 本地方法栈：线程私有，为 Native 方法服务。
	- Java 堆：线程共享，存放对象实例和数组，是 GC 管理的主要区域。
	- 方法区 / 元空间：线程共享，存放类元数据、运行时常量池、方法字节码等。
	- 直接内存：堆外内存，NIO、Netty 常用。
</details>
<details>
<summary>堆和栈有什么区别？</summary>
	- 栈管方法调用，线程私有，生命周期明确。
	- 堆管对象实例，线程共享，主要由 GC 管理。
	- 栈分配释放快；堆分配更复杂，可能涉及 GC。
</details>
<details>
<summary>Java 堆分为哪几部分？</summary>
	传统分代理解中，Java 堆主要分为新生代和老年代：
	- Eden：大多数新对象优先分配在这里。
	- Survivor 0 / Survivor 1：Minor GC 后仍存活的对象在两块 Survivor 之间复制。
	- Old：长期存活对象、大对象或晋升对象。
</details>
<details>
<summary>对象创建过程是什么？</summary>
	1. 类加载检查。
	2. 在堆中分配内存。
	3. 处理并发分配。
	4. 初始化零值。
	5. 设置对象头。
	6. 执行 `<init>` 构造方法。
</details>
<details>
<summary>如何判断对象是否可以被回收？</summary>
	JVM 主流使用可达性分析：从 GC Roots 出发沿引用链搜索，不可达对象可被回收。
	常见 GC Roots 包括栈中引用、JNI 引用、静态变量引用、常量引用、同步锁持有对象等。
</details>
<details>
<summary>Java 有哪些引用类型？</summary>
	- 强引用：只要存在就不会被回收。
	- 软引用：内存不足前会尝试回收。
	- 弱引用：下一次 GC 发生时就可能被回收。
	- 虚引用：配合 ReferenceQueue 跟踪对象回收。
</details>
<details>
<summary>垃圾回收算法有哪些？</summary>
	- 标记-清除：实现简单，但会产生碎片。
	- 复制算法：适合新生代，存活对象少时效率高。
	- 标记-整理：解决碎片问题，常用于老年代。
	- 分代收集：新生代和老年代使用不同策略。
</details>
<details>
<summary>Minor GC、Major GC、Full GC 有什么区别？</summary>
	- Minor GC / Young GC：回收新生代。
	- Major GC / Old GC：回收老年代，术语常和 Full GC 混用。
	- Full GC：回收整个堆，通常还会包含方法区 / 元空间相关清理。
</details>
<details>
<summary>常见垃圾收集器有哪些？</summary>
	- Serial / Serial Old
	- ParNew
	- Parallel Scavenge / Parallel Old
	- CMS
	- G1
	- ZGC / Shenandoah
	JDK 9 以后 G1 是默认收集器。
</details>
<details>
<summary>CMS 和 G1 有什么区别？</summary>
	- CMS 主要回收老年代，目标是低停顿，但会产生碎片。
	- G1 面向整个堆，按 Region 管理，支持可预测停顿，碎片问题更小。
</details>
<details>
<summary>类加载过程有哪些阶段？</summary>
	加载 -> 验证 -> 准备 -> 解析 -> 初始化 -> 使用 -> 卸载。
	其中验证、准备、解析合称连接。
</details>
<details>
<summary>双亲委派模型是什么？</summary>
	类加载请求先委托父加载器加载；父加载器无法加载时，子加载器才自己加载。
	作用是保证核心类安全与类唯一性。
</details>
<details>
<summary>JVM 常见 OOM 有哪些？</summary>
	- `Java heap space`
	- `StackOverflowError`
	- `Metaspace`
	- `Direct buffer memory`
	- `GC overhead limit exceeded`
</details>
<details>
<summary>内存泄漏和内存溢出有什么区别？</summary>
	- 内存泄漏：不用的对象仍被引用，无法回收，是原因。
	- 内存溢出：申请不到足够内存，抛出 OOM，是结果。
</details>
