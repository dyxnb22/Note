# JUC

## 线程基础
### Java 线程和操作系统线程是什么关系

在现代主流 HotSpot JVM 中，Java 线程通常与操作系统内核线程是一对一映射关系，底层会通过 `pthread_create` 等系统调用创建系统线程，所以线程调度、阻塞、唤醒最终**依赖操作系统**。**主流 HotSpot 是 1:1 线程模型**。

### 使用多线程要注意哪些核心问题

多线程的核心问题是**线程安全**，主要看三个维度：
- 原子性：常见手段有 `synchronized`、`Lock`、`Atomic` 原子类。
- 可见性：一个线程修改共享变量后，其他线程能及时看到。常见手段有 `volatile`、`synchronized`、`Lock`。
- 有序性：程序执行顺序在多线程下仍符合预期。编译器和 CPU 可能为了优化进行**指令重排序**，Java 通过 `volatile`、`synchronized` 和 happens-before 规则限制重排序。

### 线程的创建方式有哪些

| 方式 | 写法 | 优点 | 缺点 | 适用场景 |
| --- | --- | --- | --- | --- |
| 继承 `Thread` | 重写 `run()`，调用 `start()` | 简单，能直接使用 `this` 获取当前线程对象 | Java 单继承，扩展性差 | 简单 demo，不推荐生产大量使用 |
| 实现 `Runnable` | 实现 `run()`，交给 `Thread` | 任务和线程解耦，可继承其他类，可多个线程共享同一个任务对象 | 没有返回值，不能直接抛受检异常 | 普通无返回值任务 |
| 实现 `Callable` | 实现 `call()`，配合 `FutureTask` 或线程池 | 有返回值，可抛受检异常 | 写法比 `Runnable` 复杂 | 需要获取异步执行结果 |
| 使用线程池 | `ExecutorService.submit/execute` | 复用线程、控制并发量、统一管理生命周期 | 参数配置不当会导致 OOM、拒绝任务或排查困难 | 生产环境首选 |

示例：
```java
Callable<Integer> task = () -> 1;
FutureTask<Integer> futureTask = new FutureTask<>(task);
new Thread(futureTask).start();
Integer result = futureTask.get();
```
生产中一般不手动频繁 `new Thread()`，而是使用自定义 `ThreadPoolExecutor`。

### Java 线程有哪些状态

可以通过 `Thread#getState()` 获取线程状态：
| 状态 | 含义 |
| --- | --- |
| NEW | 已创建但未调用 `start()` |
| RUNNABLE | 可运行状态，包含就绪和正在 CPU 上运行 |
| BLOCKED | 等待进入 `synchronized` 临界区，即等待 monitor 锁 |
| WAITING | 无限期等待其他线程唤醒，例如 `wait()`、`join()`、`LockSupport.park()` |
| TIMED_WAITING | 限时等待，例如 `sleep(time)`、`wait(time)`、`join(time)` |
| TERMINATED | 线程执行结束 |

注意：Java 的 `RUNNABLE` 不等于一定正在运行，也可能正在等待操作系统调度。

### BLOCKED 和 WAITING 有什么区别

| 对比点 | BLOCKED | WAITING |
| --- | --- | --- |
| 触发原因 | 获取 `synchronized` 的 monitor 锁失败 | 主动等待其他线程动作 |
| 典型方法 | 进入同步方法或同步代码块 | `Object.wait()`、`Thread.join()`、`LockSupport.park()` |
| 是否持有锁 | 正在等待锁，尚未获得目标 monitor | `wait()` 会释放 monitor，`park()` 不涉及 monitor |
| 唤醒方式 | 持锁线程释放锁后重新竞争 | `notify/notifyAll`、目标线程结束、`unpark`、中断等 |

简单记忆：`BLOCKED` 是抢锁抢不到；`WAITING` 是自己进入等待，需要其他条件触发。

### 如何优雅停止一个线程

不要使用 `Thread.stop()`、`suspend()`、`resume()`。`stop()` 会强制终止线程并释放锁，可能破坏共享数据一致性；`suspend()` 容易导致死锁。
常用方式：

- `volatile` 标志位
- `interrupt()`
- `Future.cancel(true)`
- 关闭资源

### 线程中断机制与 InterruptedException 是什么关系

每个线程都有一个中断标志位，初始为 `false`。调用 `thread.interrupt()` 并不会强行杀死线程，而是发出“希望你停止”的协作信号。
如果线程在 `sleep()`、`wait()`、`join()`、`Condition.await()` 等可中断阻塞方法中，会抛出 `InterruptedException`；否则只是把中断标志设为 `true`，需要线程自己检查并退出。

## 线程安全与内存模型
### 怎么保证多线程安全

常见方案可以按“是否共享”和“如何保护共享”来分类：

| 方案        | 代表技术                                                     | 适用场景                     |
| ----------- | ------------------------------------------------------------ | ---------------------------- |
| 不共享      | 局部变量、无状态对象、`ThreadLocal`                          | 从根源避免竞争               |
| 互斥访问    | `synchronized`、`ReentrantLock`、`ReadWriteLock`             | 多线程读写同一份共享数据     |
| 可见性控制  | `volatile`                                                   | 状态标记、配置开关、单次发布 |
| 原子操作    | `AtomicInteger`、`AtomicReference`、`LongAdder`              | 计数器、状态 CAS 更新        |
| 并发容器    | `ConcurrentHashMap`、`CopyOnWriteArrayList`、`BlockingQueue` | 替代手写加锁集合             |
| 协作工具    | `CountDownLatch`、`CyclicBarrier`、`Semaphore`               | 控制线程执行顺序或并发数量   |
| 事务/版本号 | 数据库事务、乐观锁版本号                                     | 保证业务数据一致性           |

面试回答时先说三要素：原子性、可见性、有序性；再展开具体工具。

### 指令重排序是什么

为了提高性能，编译器和处理器可能调整指令执行顺序，但必须满足两个基本原则：

-   单线程下不能改变程序执行结果。
-   存在数据依赖关系的指令不能随意重排。

重排序在单线程下通常无感，但在多线程中，如果没有 `volatile`、锁或 happens-before 约束，其他线程可能看到不符合代码书写顺序的中间状态。

要保证多线程有序性，JMM 定义了 happens-before（先行发生）规则，满足规则的两个操作之间具有可见性和有序性保障：

-   程序次序规则：一个线程内书写在前的操作 happens-before 书写在后的操作
-   volatile 规则：volatile 变量的写 happens-before 后续对该变量的读
-   锁规则：解锁操作 happens-before 后续的加锁操作
-   线程启动规则：Thread.start() happens-before 该线程的所有操作
-   线程结束规则：线程的所有操作 happens-before 其他线程对该线程的 join() 返回
-   中断规则：interrupt() 调用 happens-before 被中断线程检测到中断
-   传递性：A happens-before B，B happens-before C → A happens-before C

掌握这些规则可以判断多线程场景下哪些操作是安全的，不需要额外加同步。

例如对象发布时，如果引用赋值被重排到构造初始化之前，其他线程可能拿到一个“未完全初始化”的对象。

### volatile 关键字有什么作用

`volatile` 有两个核心作用：

1.  保证可见性：对 `volatile` 变量的写会立即刷新到主内存，读会从主内存读取，其他线程能及时看到修改。
2.  禁止特定指令重排序：通过内存屏障保证 `volatile` 读写前后的普通读写不会被随意重排。

`volatile` 不保证复合操作的原子性，例如：

```java
volatile int count = 0;
count++; // 不是原子操作：读、加、写三个步骤可能被并发打断
```

内存屏障可以这样理解：

| 操作          | 屏障       | 目的                                           |
| ------------- | ---------- | ---------------------------------------------- |
| volatile 写前 | StoreStore | 保证前面的普通写先完成                         |
| volatile 写后 | StoreLoad  | 保证 volatile 写对后续读可见，是开销较大的屏障 |
| volatile 读后 | LoadLoad   | 保证后续普通读不能跑到 volatile 读之前         |
| volatile 读后 | LoadStore  | 保证后续普通写不能跑到 volatile 读之前         |

典型场景：状态标记、双重检查锁中的实例引用、配置开关。

### CAS 是什么，有什么缺点

CAS 全称 Compare And Swap，比较并交换。它包含三个值：内存值 V、预期值 A、新值 B。只有当 V 等于 A 时，才把 V 更新为 B，否则更新失败。

CAS 是乐观锁和 Java 原子类的基础，例如 `AtomicInteger.incrementAndGet()` 底层就是 CAS 自旋。

缺点：

-   ABA 问题：值从 A 变成 B 又变回 A，CAS 会误以为没有变化。可用 `AtomicStampedReference` 加版本号解决。
-   自旋开销：竞争激烈时 CAS 长时间失败，会浪费 CPU。
-   只能天然保证单个变量原子更新：多个变量的一致性需要 `AtomicReference` 封装对象，或使用锁。

### 悲观锁和乐观锁有什么区别

| 对比点 | 悲观锁                                      | 乐观锁                         |
| ------ | ------------------------------------------- | ------------------------------ |
| 思路   | 假设冲突一定会发生，操作前先加锁            | 假设冲突较少，提交更新时再检查 |
| 代表   | `synchronized`、`ReentrantLock`、数据库行锁 | CAS、版本号、时间戳            |
| 优点   | 逻辑简单，强一致                            | 无阻塞，性能好                 |
| 缺点   | 阻塞、上下文切换开销大                      | 冲突高时自旋重试成本高         |
| 适用   | 写多、竞争激烈                              | 读多写少、冲突较低             |

### 如何保证业务数据一致性

业务数据一致性不只靠 Java 锁，还要看数据是否跨线程、跨进程、跨服务。

-   单 JVM 内共享变量：使用锁、原子类、并发容器、不可变对象。
-   数据库内多条写操作：使用事务保证 ACID。
-   并发更新同一行数据：使用乐观锁版本号或悲观行锁。
-   分布式场景：需要分布式锁、幂等、唯一约束、消息事务或最终一致性方案。

面试中如果题目只问 Java 多线程，重点答 `synchronized`、`Lock`、`volatile`、`Atomic`、并发集合；如果问业务一致性，要补充事务和版本号。

### sleep 和 wait 有什么区别

| 对比点     | `Thread.sleep()`              | `Object.wait()`                |
| ---------- | ----------------------------- | ------------------------------ |
| 所属类     | `Thread` 静态方法             | `Object` 实例方法              |
| 是否释放锁 | 不释放锁                      | 释放当前对象 monitor 锁        |
| 使用条件   | 任意位置可调用                | 必须在 `synchronized` 中调用   |
| 唤醒方式   | 时间到或被 `interrupt()` 中断 | `notify/notifyAll`、超时或中断 |
| 线程状态   | `TIMED_WAITING`               | `WAITING` 或 `TIMED_WAITING`   |
| 用途       | 暂停当前线程                  | 线程间协作，等待条件满足       |

wait() 通常要放在 while 循环中检查条件，避免虚假唤醒：

```java
synchronized (lock) {
    while (!condition) {
        lock.wait();
    }
}
```

### JUC 包下常用的类有哪些

| 分类     | 常用类                                                       | 作用               |
| -------- | ------------------------------------------------------------ | ------------------ |
| 线程池   | `ThreadPoolExecutor`、`ScheduledThreadPoolExecutor`、`Executors` | 管理线程和任务执行 |
| 锁       | `ReentrantLock`、`ReadWriteLock`、`StampedLock`              | 显式加锁、读写分离 |
| 原子类   | `AtomicInteger`、`AtomicReference`、`LongAdder`              | CAS 原子更新       |
| 并发集合 | `ConcurrentHashMap`、`CopyOnWriteArrayList`、`BlockingQueue` | 线程安全容器       |
| 同步工具 | `CountDownLatch`、`CyclicBarrier`、`Semaphore`               | 线程协作           |
| 异步编排 | `FutureTask`、`CompletableFuture`                            | 异步结果和任务组合 |

注意：`Executors` 是工厂类，面试和生产实践中一般建议手动创建 `ThreadPoolExecutor`，避免无界队列或无限线程带来的资源风险

### CountDownLatch、CyclicBarrier、Semaphore 有什么区别

| 工具类           | 核心作用                                 | 是否可复用 | 典型场景                 |
| ---------------- | ---------------------------------------- | ---------- | ------------------------ |
| `CountDownLatch` | 一个或多个线程等待计数减到 0             | 不可复用   | 主线程等待多个子任务完成 |
| `CyclicBarrier`  | 一组线程互相等待，全部到达屏障后一起继续 | 可复用     | 多线程分阶段计算         |
| `Semaphore`      | 控制同时访问资源的线程数                 | 可复用     | 限流、连接池许可控制     |

区别重点：

-   `CountDownLatch` 是“别人完成后我继续”，常见是主线程 `await()`，子线程 `countDown()`。
-   `CyclicBarrier` 是“大家都到齐再继续”，每个参与线程都调用 `await()`。
-   `Semaphore` 不强调等待所有线程，而是控制并发许可证数量。

### ThreadLocal 的作用、原理和内存泄漏问题

`ThreadLocal` 为每个线程保存一份独立变量副本，常用于用户上下文、traceId、日期格式化对象、数据库连接上下文等。

原理：

-   每个 `Thread` 内部有一个 `ThreadLocalMap`。
-   `ThreadLocalMap` 的 key 是 `ThreadLocal` 对象，value 是线程自己的变量副本。
-   调用 `get/set/remove` 实际都是操作当前线程的 `ThreadLocalMap`。

优点：

-   线程隔离，避免共享变量竞争。
-   减少同一线程内跨方法传参。

内存泄漏风险：

-   `ThreadLocalMap` 的 key 是弱引用，`ThreadLocal` 外部强引用消失后 key 可能被回收。
-   但 value 仍然可能被线程持有，尤其在线程池中线程长期不销毁，导致 value 无法释放。

最佳实践：使用完一定在 `finally` 中调用 `remove()`。

```java
try {
    threadLocal.set(value);
    doSomething();
} finally {
    threadLocal.remove();
}
```

### 不同线程之间如何通信

常见线程通信方式：

-   共享变量：用 `volatile` 或锁保证可见性和线程安全。
-   `wait/notify/notifyAll`：基于对象 monitor 的等待和唤醒。
-   `Lock + Condition`：比 `wait/notify` 更灵活，可创建多个等待队列，实现精准唤醒。
-   `BlockingQueue`：生产者消费者模型首选，避免手写等待唤醒。
-   JUC 同步工具：`CountDownLatch`、`CyclicBarrier`、`Semaphore` 等。
-   `Future/CompletableFuture`：通过异步结果完成来传递信息。

生产者消费者场景一般优先使用 `BlockingQueue`，比自己写 `wait/notify` 更稳。



## 锁机制
### synchronized 的工作原理

`synchronized` 是 JVM 层面的内置锁，也叫 monitor 锁。它可以保证临界区代码的原子性、可见性和有序性。

实现方式：

-   同步代码块编译后会生成 `monitorenter` 和 `monitorexit` 字节码指令。
-   同步方法通过方法访问标志 `ACC_SYNCHRONIZED` 标识，由 JVM 隐式加锁。
-   每个对象都可以关联一个 monitor，线程进入同步块时尝试获取该 monitor。
-   获取锁失败的线程进入 EntryList 等待；调用 `wait()` 的线程进入 WaitSet。

内存语义：

-   加锁前必须读取主内存中的最新共享变量。
-   解锁前必须把工作内存中的修改刷新回主内存。

所以 `synchronized` 不只保证互斥，也保证可见性。

### synchronized 锁静态方法和普通方法有什么区别

| 场景         | 锁对象                | 互斥范围                           |
| ------------ | --------------------- | ---------------------------------- |
| 普通同步方法 | 当前实例对象 `this`   | 同一个实例内互斥，不同实例互不影响 |
| 静态同步方法 | 当前类的 `Class` 对象 | 该类所有实例共享同一把锁           |
| 同步代码块   | 括号中指定的对象      | 由开发者指定锁粒度                 |

示例：

```java
public synchronized void instanceMethod() {}
public static synchronized void staticMethod() {}
synchronized (lock) {}
```

如果保护的是实例字段，用普通同步方法或实例锁；如果保护的是静态共享资源，用静态同步方法或类锁。

### synchronized 支持重入吗，如何实现

`synchronized` 支持可重入。可重入指同一个线程已经持有某把锁时，可以再次获取这把锁，不会被自己阻塞。

实现思路：

-   monitor 记录当前持有锁的线程。
-   monitor 维护一个重入计数器。
-   同一线程再次进入同步块时，计数器加 1。
-   每退出一次同步块，计数器减 1。
-   计数器变为 0 时，锁才真正释放。

可重入解决了同步方法之间互相调用时的自我死锁问题。

### synchronized 锁升级过程是什么

对象头 Mark Word 中会记录锁状态。传统锁升级路径是：

无锁 -> 偏向锁 -> 轻量级锁 -> 重量级锁。

但要注意版本差异：JDK 1.6 到 JDK 14 中偏向锁默认开启且有延迟启动；从 JDK 15 开始偏向锁默认关闭并逐步废弃。因此现代 JDK 中更常见的理解是：

无锁 -> 轻量级锁（CAS 自旋）-> 重量级锁（monitor 阻塞）。

各状态含义：

-   无锁：没有线程进入同步块。
-   偏向锁（JDK 15 前默认，现已废弃）：早期优化，单线程反复获取锁时在对象头记录线程 ID，减少 CAS。
-   轻量级锁：存在轻微竞争时，通过 CAS 和自旋尝试获取锁，避免线程挂起。
-   重量级锁：竞争激烈或自旋失败时膨胀为 monitor 锁，线程阻塞和唤醒依赖操作系统，开销较大。

锁升级通常不可逆，目的是在不同竞争强度下平衡性能。

### JVM 对 synchronized 做了哪些优化

常见优化：

-   锁消除：JIT 通过逃逸分析发现对象不会被多线程共享，就去掉无意义的同步。
-   锁粗化：连续多次加锁解锁会被合并成更大范围的锁，减少频繁开销。
-   自适应自旋：线程短时间自旋等待锁释放，避免直接挂起；自旋次数会根据历史情况动态调整。
-   轻量级锁：通过 CAS 减少无竞争或低竞争下的重量级锁开销。
-   偏向锁（仅 JDK 14 及以下）：JDK 15 起默认关闭并逐步废弃，面试中了解即可。

### ReentrantLock 的工作原理

`ReentrantLock` 是 JDK 层面的显式锁，底层基于 AQS。

核心结构：

-   `state`：AQS 中的 `volatile int`，在 `ReentrantLock` 中表示锁状态和重入次数。`0` 表示未加锁，大于 `0` 表示已被持有。
-   owner thread：记录当前持锁线程。
-   CLH 双向等待队列：获取锁失败的线程会封装成 Node 入队，并通过 `LockSupport.park()` 挂起。

可重入逻辑：

-   如果 `state == 0`，通过 CAS 抢锁成功后设置当前线程为 owner。
-   如果当前线程已经是 owner，再次加锁时 `state++`。
-   每次释放锁 `state--`，直到 `state == 0` 才真正释放并唤醒后继节点。

扩展能力：

-   支持公平锁和非公平锁。
-   支持 `lockInterruptibly()` 响应中断。
-   支持 `tryLock()` 和超时获取锁。
-   支持多个 `Condition` 等待队列，实现精准唤醒。

### synchronized 和 ReentrantLock 有什么区别

| 对比点   | `synchronized`              | `ReentrantLock`                         |
| -------- | --------------------------- | --------------------------------------- |
| 实现层面 | JVM 内置 monitor            | JDK 代码，基于 AQS                      |
| 获取释放 | 自动加锁释放，异常也会释放  | 手动 `lock/unlock`，必须 `finally` 解锁 |
| 公平性   | 只支持非公平                | 支持公平和非公平                        |
| 中断响应 | 等锁过程不能响应中断        | `lockInterruptibly()` 可响应中断        |
| 超时获取 | 不支持                      | `tryLock(time, unit)` 支持              |
| 条件队列 | 一个 WaitSet，`wait/notify` | 多个 `Condition`，可精准唤醒            |
| 使用范围 | 方法、代码块                | 代码块                                  |

选择建议：简单同步优先 `synchronized`；需要公平锁、可中断、超时、多个条件队列时用 `ReentrantLock`。

### 公平锁和非公平锁有什么区别

公平锁按等待队列顺序获取锁，先来先得；非公平锁允许新来的线程直接尝试抢锁，抢不到再排队。

非公平锁吞吐量更高的原因：

-   刚释放锁时，新线程可能还在 CPU 上运行，直接 CAS 抢锁成功，减少线程唤醒和上下文切换。
-   公平锁需要严格检查队列，唤醒队首线程，线程从阻塞恢复到运行涉及调度开销。

代价：非公平锁可能导致排队线程长期拿不到锁，出现饥饿。

`ReentrantLock` 默认是非公平锁。公平锁通过 `hasQueuedPredecessors()` 判断队列中是否已有前驱节点，有前驱就不能插队。

### ReadWriteLock 适合什么场景

`ReadWriteLock` 的核心规则：

-   读读共享。
-   读写互斥。
-   写写互斥。

适合读多写少的场景，例如缓存、配置中心、本地路由表。如果写操作频繁，读写锁优势会下降，甚至因为锁管理更复杂而不如普通互斥锁。

常用实现是 `ReentrantReadWriteLock`。

StampedLock 是 Java 8 提供的读写锁改进版，支持乐观读模式。乐观读不加锁，不会阻塞写线程，读后验证版本戳，非常适合读多写少场景。吞吐量通常高于 ReadWriteLock。

## AQS
### AQS 是什么

AQS 全称 `AbstractQueuedSynchronizer`，是 JUC 中构建锁和同步工具的基础框架。`ReentrantLock`、`Semaphore`、`CountDownLatch`、`ReentrantReadWriteLock` 都基于 AQS。

核心组成：

-   `volatile int state`：同步状态。
-   FIFO 双向等待队列：获取资源失败的线程会封装成 Node 排队。
-   CAS：用于原子修改 `state`。
-   模板方法：子类重写 `tryAcquire`、`tryRelease`、`tryAcquireShared`、`tryReleaseShared`。

不同工具对 `state` 的含义不同：

-   `ReentrantLock`：`state` 表示锁是否被占用以及重入次数。
-   `Semaphore`：`state` 表示剩余许可证数量。
-   `CountDownLatch`：`state` 表示还需要倒数的次数。

AQS 解决的是“获取不到资源时如何排队、阻塞、唤醒”的通用问题，具体资源含义由子类定义。

### 如何用 AQS 实现一个可重入公平锁

实现思路：

1.  写一个内部类继承 `AbstractQueuedSynchronizer`。
2.  用 `state` 表示重入次数。
3.  在 `tryAcquire` 中：

-   如果 `state == 0`，先用 `hasQueuedPredecessors()` 判断是否有前驱节点，保证公平性。
-   没有前驱时 CAS 抢锁，成功后设置 owner 为当前线程。
-   如果当前线程已经持有锁，则 `state` 增加，实现可重入。

1.  在 `tryRelease` 中减少 `state`，减到 0 时清空 owner，真正释放锁。
2.  外部 `lock()` 调用 AQS 的 `acquire(1)`，`unlock()` 调用 `release(1)`。

关键代码骨架：

```java
protected boolean tryAcquire(int acquires) {
    Thread current = Thread.currentThread();
    int c = getState();
    if (c == 0) {
        if (!hasQueuedPredecessors() && compareAndSetState(0, acquires)) {
            setExclusiveOwnerThread(current);
            return true;
        }
    } else if (current == getExclusiveOwnerThread()) {
        setState(c + acquires);
        return true;
    }
    return false;
}

protected boolean tryRelease(int releases) {
    int c = getState() - releases;
    if (Thread.currentThread() != getExclusiveOwnerThread()) {
        throw new IllegalMonitorStateException();
    }
    if (c == 0) {
        setExclusiveOwnerThread(null);
        setState(0);
        return true;
    }
    setState(c);
    return false;
}
```

注意：`acquire()` 是 AQS 已实现的模板方法，子类主要重写 `tryAcquire()`。

## 线程池与异步编程
### 线程池的工作原理

`ThreadPoolExecutor` 提交任务后的核心流程：

1.  当前线程数小于 `corePoolSize`：创建核心线程执行任务。
2.  核心线程已满：任务进入 `workQueue`。
3.  队列已满且线程数小于 `maximumPoolSize`：创建非核心线程执行任务。
4.  线程数达到 `maximumPoolSize` 且队列已满：执行拒绝策略。

记忆公式：

先核心线程 -> 再队列 -> 再最大线程 -> 最后拒绝策略。

### 线程池有哪些核心参数

| 参数              | 含义                                   |
| ----------------- | -------------------------------------- |
| `corePoolSize`    | 核心线程数，默认不会因空闲而销毁       |
| `maximumPoolSize` | 最大线程数，包含核心和非核心线程       |
| `keepAliveTime`   | 非核心线程空闲多久后回收               |
| `unit`            | `keepAliveTime` 的时间单位             |
| `workQueue`       | 任务等待队列                           |
| `threadFactory`   | 线程工厂，可设置线程名、是否守护线程等 |
| `handler`         | 拒绝策略                               |

如果调用 allowCoreThreadTimeOut(true)，核心线程空闲超过 keepAliveTime 也可以被回收。

### 线程池有哪些拒绝策略

四种内置拒绝策略：

-   `AbortPolicy`：默认策略，直接抛出 `RejectedExecutionException`。
-   `CallerRunsPolicy`：由提交任务的线程自己执行，能形成反压。
-   `DiscardPolicy`：直接丢弃任务，不抛异常。
-   `DiscardOldestPolicy`：丢弃队列中最老的任务，再尝试提交当前任务。

生产中常见做法：自定义拒绝策略，记录日志、打点告警、持久化任务或返回明确失败。

### 线程池参数如何设置

经验值：

-   CPU 密集型：线程数约等于 CPU 核数或 CPU 核数 + 1，减少上下文切换。
-   IO 密集型：线程数可以大于 CPU 核数，常见是 CPU 核数 * 2 或按等待时间估算。

更通用的估算公式：

```
线程数 = CPU 核数 * (1 + 等待时间 / 计算时间)
```

实践建议：

-   使用 `Runtime.getRuntime().availableProcessors()` 获取核心数。
-   队列尽量有界，避免任务无限堆积导致 OOM。
-   设置有意义的线程名，方便排查。
-   根据监控指标动态调整：活跃线程数、队列长度、拒绝次数、任务耗时。

### 核心线程数设置为 0 可以吗

可以，但要结合队列类型理解。

当 `corePoolSize = 0` 时，线程池没有常驻核心线程。任务提交后通常会先进入队列，如果没有工作线程消费，线程池会创建非核心线程来执行任务。

这种配置适合任务非常零散、希望空闲时线程全部回收的场景，但不适合对响应时间要求很高的稳定服务，因为可能频繁创建和销毁线程。

### 为什么不建议直接用 Executors

`Executors` 常见工厂方法：

-   `newFixedThreadPool`：固定线程数，使用无界 `LinkedBlockingQueue`，任务堆积可能 OOM。
-   `newSingleThreadExecutor`：单线程顺序执行，也使用无界队列，任务堆积可能 OOM。
-   `newCachedThreadPool`：最大线程数接近无限，使用 `SynchronousQueue`，高并发下可能创建过多线程。
-   `newScheduledThreadPool`：定时或周期任务线程池。
-   `newSingleThreadScheduledExecutor`：单线程定时任务线程池。

不建议直接使用 `Executors` 的原因是参数隐藏，容易出现无界队列或无限线程风险。生产中建议手动 `new ThreadPoolExecutor`，明确线程数、队列大小、线程名和拒绝策略。

### 线程池中的 shutdown 和 shutdownNow 有什么区别

| 方法            | 状态变化      | 行为                                                         |
| --------------- | ------------- | ------------------------------------------------------------ |
| `shutdown()`    | 进入 SHUTDOWN | 不再接收新任务，已提交任务继续执行，包括队列中的任务         |
| `shutdownNow()` | 进入 STOP     | 不再接收新任务，尝试中断正在执行的任务，并返回队列中未执行的任务 |

`shutdownNow()` 只是调用线程的 `interrupt()`，不保证任务立即停止。如果任务不响应中断，线程池仍要等任务自己结束。

常见关闭流程：

```java
executor.shutdown();
if (!executor.awaitTermination(30, TimeUnit.SECONDS)) {
    executor.shutdownNow();
}
```

### 提交给线程池的任务可以撤回吗

可以。通过 `submit()` 提交任务会返回 `Future`，调用 `cancel(boolean mayInterruptIfRunning)` 可以尝试取消任务。

-   任务还没开始：可以取消，任务不会执行。
-   任务正在执行且参数为 `true`：会向执行线程发送中断信号。
-   任务正在执行且参数为 `false`：不会中断，只能等任务执行完。
-   任务已经完成：取消失败。

```java
Future<?> future = executor.submit(task);
future.cancel(true);
```

取消是否成功，取决于任务是否响应中断。

### Future、FutureTask 和 CompletableFuture 有什么区别

| 类型                | 作用                            | 特点                                     |
| ------------------- | ------------------------------- | ---------------------------------------- |
| `Future`            | 异步结果接口                    | 可 `get()`、取消、判断完成，但不方便编排 |
| `FutureTask`        | 同时实现 `Runnable` 和 `Future` | 可包装 `Callable` 后交给 `Thread` 执行   |
| `CompletableFuture` | Java 8 异步编排工具             | 支持链式转换、任务组合、异常处理         |

`Future` 的问题是 `get()` 会阻塞，多个异步任务组合不方便。

`CompletableFuture` 常用能力：

-   `supplyAsync/runAsync`：异步执行任务。
-   `thenApply/thenAccept/thenRun`：串行处理结果。
-   `thenCombine`：合并两个任务结果。
-   `allOf/anyOf`：等待全部或任意任务完成。
-   `exceptionally/handle`：处理异常。

示例：

```java
CompletableFuture<Integer> future = CompletableFuture
        .supplyAsync(() -> query())
        .thenApply(result -> result + 1)
        .exceptionally(e -> 0);
```

生产中建议为 `CompletableFuture` 指定自定义线程池，避免大量任务占用公共 `ForkJoinPool`。

thenApply vs thenCompose 区别：thenApply 对结果做同步转换，返回新值；thenCompose 返回一个新的 CompletableFuture，用于串联异步任务，类似于 flatMap。

```java
CompletableFuture<Integer> future = CompletableFuture
        .supplyAsync(() -> queryId())
        .thenApply(id -> id + 1); // 同步转换

CompletableFuture<String> chained = CompletableFuture
        .supplyAsync(() -> queryId())
        .thenCompose(id -> CompletableFuture.supplyAsync(() -> getDetail(id))); // 异步串联
```

超时处理：Java 9+ 支持 orTimeout() 和 completeOnTimeout()，避免 get() 无限阻塞。

```java
CompletableFuture.supplyAsync(this::query)
        .orTimeout(5, TimeUnit.SECONDS)  // 超时则抛出 TimeoutException
        .exceptionally(e -> defaultValue);
```

注意：默认使用 ForkJoinPool.commonPool()，该线程池被所有 CompletableFuture 共享，大量阻塞任务会耗尽公共线程。生产环境务必指定自定义线程池。

## 并发场景题
### 什么情况下会产生死锁，如何避免

死锁必须同时满足四个条件：

-   互斥：资源同一时刻只能被一个线程占用。
-   持有并等待：线程持有一个资源，同时等待其他资源。
-   不可剥夺：线程持有的资源不能被强制抢走。
-   循环等待：多个线程之间形成资源等待环。

破坏任意一个条件即可避免死锁。常见手段：

-   固定加锁顺序，破坏循环等待。
-   避免嵌套锁，减少持有并等待。
-   使用 `tryLock(time, unit)`，拿不到锁就释放已持有资源并重试。
-   缩小锁粒度，减少锁持有时间。
-   发生问题时用 `jstack`、线程 dump 排查 `BLOCKED` 和死锁信息。

面试重点：最常用、最可落地的是资源有序分配法。

### 如何设计一个生产者消费者模型

优先使用 `BlockingQueue`，不要手写复杂的 `wait/notify`。

核心思路：

-   生产者调用 `put()`，队列满时阻塞。
-   消费者调用 `take()`，队列空时阻塞。
-   队列负责线程安全和等待唤醒。

```java
BlockingQueue<Task> queue = new ArrayBlockingQueue<>(1000);

// producer
queue.put(task);

// consumer
Task task = queue.take();
handle(task);
```

如果需要停止消费者，可以使用中断，或放入特殊结束标记。

### 高并发计数器如何实现

可选方案：

-   低并发或需要精确即时值：`AtomicInteger`、`AtomicLong`。
-   高并发热点计数：`LongAdder`，通过分段累加降低 CAS 冲突。
-   强一致业务计数：数据库事务、行锁或版本号。

`LongAdder` 的吞吐量通常高于 `AtomicLong`，但读取 `sum()` 时是汇总多个分段，不适合要求每次读取都绝对线性一致的场景。
