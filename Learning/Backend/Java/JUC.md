# Java 并发编程

## 线程基础

## Java 线程和操作系统线程是什么关系？

在主流 HotSpot JVM 中，Java 平台线程通常与操作系统内核线程一对一映射，线程的调度、阻塞和唤醒最终依赖操作系统。虚拟线程是另一种调度模型，适合放在 Java 新特性中单独理解。

## 多线程主要解决哪些问题？

线程安全通常从三个维度理解：

- 原子性：操作不可被并发打断，常用 `synchronized`、`Lock`、`Atomic`。
- 可见性：一个线程的修改能被其他线程及时看到，常用 `volatile`、锁。
- 有序性：执行顺序符合预期，需要依赖锁、`volatile` 和 happens-before。

如果共享状态可以改为局部变量、不可变对象或线程隔离数据，应优先减少共享，而不是一开始就加锁。

## Java 线程有哪些创建方式？

| 方式 | 特点 | 适用场景 |
| --- | --- | --- |
| 继承 `Thread` | 写法简单，但受单继承限制 | Demo 或特殊线程类 |
| 实现 `Runnable` | 任务和线程解耦，无返回值 | 普通无返回值任务 |
| 实现 `Callable` | 有返回值，可抛受检异常 | 需要异步结果 |
| 使用线程池 | 复用线程、控制并发和生命周期 | 生产环境首选 |

```java
Callable<Integer> task = () -> 1;
FutureTask<Integer> futureTask = new FutureTask<>(task);
new Thread(futureTask).start();
Integer result = futureTask.get();
```

生产环境一般不频繁手动 `new Thread()`，而是使用自定义 `ThreadPoolExecutor`。

## 直接调用 `run()` 和调用 `start()` 有什么区别？

- `run()` 只是普通方法调用，在当前线程中同步执行，不会创建新线程。
- `start()` 才会创建并启动新线程，由 JVM 在新线程中调用 `run()`；同一个 `Thread` 只能成功调用一次 `start()`。

```java
Thread t = new Thread(() -> System.out.println(Thread.currentThread().getName()));
t.run();   // 当前线程执行
t.start(); // 新线程执行；只能调用一次
```

线程已经结束后再次调用 `start()` 会抛出 `IllegalThreadStateException`。

## Java 线程有哪些状态？

| 状态 | 含义 |
| --- | --- |
| `NEW` | 已创建但未调用 `start()` |
| `RUNNABLE` | 可运行，包含就绪和正在运行 |
| `BLOCKED` | 等待进入 `synchronized` 临界区 |
| `WAITING` | 无限期等待其他线程唤醒 |
| `TIMED_WAITING` | 限时等待 |
| `TERMINATED` | 执行结束 |

`RUNNABLE` 不等于一定正在 CPU 上运行，也可能正在等待操作系统调度。

## BLOCKED、WAITING 和 TIMED_WAITING 有什么区别？

- `BLOCKED`：抢不到 `synchronized` 的 monitor 锁，等待其他线程释放。
- `WAITING`：主动等待其他线程动作，例如 `wait()`、`join()`、`LockSupport.park()`。
- `TIMED_WAITING`：带超时的等待，例如 `sleep(time)`、`wait(time)`、`join(time)`。

`wait()` 会释放当前 monitor；`sleep()` 不释放锁；`park()` 不依赖 monitor。

## 如何优雅停止线程？中断机制是什么？

不要使用 `Thread.stop()`、`suspend()`、`resume()`。它们可能强制释放锁、破坏共享状态或造成死锁。

常用方式是让线程协作退出：

- 使用 `volatile` 标志位。
- 调用 `interrupt()`，让线程检查中断状态并退出。
- 使用 `Future.cancel(true)` 发送中断信号。
- 关闭阻塞中的资源，使线程从 I/O 调用返回。

`interrupt()` 不会强行杀死线程。线程在 `sleep()`、`wait()`、`join()`、`Condition.await()` 等可中断阻塞方法中通常会收到 `InterruptedException`；否则只是设置中断标志，需要业务代码主动检查。

## 守护线程和未捕获异常怎么处理？

守护线程只适合执行随进程生命周期结束即可丢弃的后台辅助工作。所有非守护线程结束后，JVM 可以退出，不会等待守护线程完成；必须在 `start()` 前调用 `setDaemon(true)`。需要持久化、提交事务或保证最终执行的任务不能依赖守护线程。

线程未捕获异常时，该线程会终止，可以通过 `Thread.UncaughtExceptionHandler` 记录和告警。在线程池中还要注意：`execute()` 的异常通常会交给线程的未捕获异常处理器，而 `submit()` 会把异常封装在 `Future` 中，需要调用 `Future.get()` 才能观察到。

## Java 内存模型与线程安全

## 如何保证多线程安全？

| 思路 | 代表技术 | 适用场景 |
| --- | --- | --- |
| 不共享 | 局部变量、不可变对象、`ThreadLocal` | 从根源避免竞争 |
| 互斥访问 | `synchronized`、`ReentrantLock` | 保护共享读写 |
| 可见性控制 | `volatile` | 状态标记、配置开关 |
| 原子更新 | `AtomicInteger`、`AtomicReference`、`LongAdder` | 计数和 CAS 更新 |
| 并发容器 | `ConcurrentHashMap`、`CopyOnWriteArrayList`、`BlockingQueue` | 替代手写加锁集合 |
| 协作工具 | `CountDownLatch`、`CyclicBarrier`、`Semaphore` | 控制线程协作和并发数量 |

业务数据跨线程、跨进程或跨服务时，还要结合数据库事务、唯一约束、版本号、幂等和最终一致性方案，不能只依赖 Java 锁。

## 指令重排序和 happens-before 是什么？

编译器和处理器可能为了优化调整指令顺序，但单线程结果不能被改变。多线程中如果缺少同步约束，其他线程可能看到不符合代码书写顺序的中间状态。

happens-before 表示前一个操作的结果对后一个操作可见，并约束相关重排序。常见规则：

- 程序次序：同一线程中，前面的操作 happens-before 后面的操作。
- volatile：对 volatile 变量的写 happens-before 后续读。
- 锁：解锁 happens-before 后续对同一把锁的加锁。
- 启动：`Thread.start()` happens-before 新线程中的操作。
- 结束：线程中的操作 happens-before 其他线程 `join()` 返回。
- 中断：`interrupt()` happens-before 被中断线程检测到中断。
- 传递性：A happens-before B，B happens-before C，则 A happens-before C。

## volatile 有什么作用？

`volatile` 主要提供：

1. 可见性：一个线程写入后，其他线程能按 JMM 规则观察到最新值。
2. 有序性：通过内存屏障限制特定的指令重排序。

它不保证复合操作的原子性：

```java
volatile int count = 0;
count++; // 读、加、写三个步骤，不是原子操作
```

典型场景是停止标志、配置开关、状态发布和双重检查锁中的实例引用。

## CAS 是什么？有什么缺点？

CAS（Compare And Swap）包含内存值 V、预期值 A 和新值 B：只有 V 等于 A 时，才把 V 更新为 B。它是 Java 原子类和许多无锁算法的基础。

缺点：

- ABA：值从 A 变成 B 又变回 A，CAS 可能误判；可用 `AtomicStampedReference` 加版本号。
- 自旋开销：竞争激烈时 CAS 反复失败，会浪费 CPU。
- 多变量一致性有限：需要用 `AtomicReference` 封装对象或使用锁。

## 悲观锁和乐观锁有什么区别？

| 对比项 | 悲观锁 | 乐观锁 |
| --- | --- | --- |
| 思路 | 假设冲突会发生，操作前加锁 | 假设冲突较少，提交时检查 |
| 代表 | `synchronized`、`ReentrantLock`、数据库行锁 | CAS、版本号、时间戳 |
| 优点 | 逻辑简单，适合强互斥 | 无阻塞，低冲突时性能好 |
| 缺点 | 可能阻塞和上下文切换 | 冲突高时重试成本高 |

## 锁机制与 AQS

## synchronized 的工作原理是什么？

`synchronized` 是 JVM 内置的 monitor 锁，可以保证互斥、可见性和有序性：

- 同步代码块编译后对应 `monitorenter` 和 `monitorexit`。
- 同步方法通过 `ACC_SYNCHRONIZED` 标记，由 JVM 隐式加锁。
- 获取不到锁的线程进入等待队列；调用 `wait()` 的线程进入 WaitSet。
- 解锁时会建立相应的内存可见性关系。

## synchronized 的实例锁、类锁和代码块锁有什么区别？

| 场景 | 锁对象 | 互斥范围 |
| --- | --- | --- |
| 普通同步方法 | 当前实例 `this` | 同一实例内互斥，不同实例不互斥 |
| 静态同步方法 | 当前类的 `Class` 对象 | 该类所有实例共享 |
| 同步代码块 | 括号中的对象 | 由开发者指定锁粒度 |

```java
public synchronized void instanceMethod() {}
public static synchronized void staticMethod() {}
synchronized (lock) {}
```

## synchronized 支持重入吗？

支持。同一线程已经持有某把锁时，可以再次进入由同一把锁保护的同步代码，不会被自己阻塞。

monitor 会记录持锁线程和重入次数；每进入一次计数加 1，每退出一次计数减 1，计数归零后才真正释放锁。

## synchronized 的锁升级和 JVM 优化是什么？

历史上常用“无锁 → 偏向锁 → 轻量级锁 → 重量级锁”描述锁状态变化。偏向锁是旧版本 HotSpot 的优化，JDK 15 起默认关闭并逐步废弃；现代 JDK 更应理解为无竞争或轻竞争时使用轻量级路径，竞争激烈时膨胀为重量级 monitor。

JIT 还可能进行：

- 锁消除：通过逃逸分析判断对象不共享时，消除无意义同步。
- 锁粗化：合并连续的加锁和解锁，减少频繁开销。
- 自适应自旋：短时间自旋等待锁释放，避免立即阻塞和唤醒。

这些属于具体 JVM 实现优化，不应当作 Java 语言层面的绝对保证。

## ReentrantLock 的工作原理和特点是什么？

`ReentrantLock` 是基于 AQS 的显式锁。AQS 中的 `state` 表示锁状态和重入次数，owner 表示当前持锁线程，获取失败的线程会进入等待队列并通过 `LockSupport.park()` 挂起。

核心逻辑：

- `state == 0` 时通过 CAS 抢锁并设置 owner。
- 当前线程已经是 owner 时，增加 `state` 实现重入。
- 每次释放锁减少 `state`，归零后唤醒后继线程。

它支持公平/非公平模式、可中断获取、超时获取和多个 `Condition` 等待队列。使用时必须在 `finally` 中释放锁。

## synchronized 和 ReentrantLock 有什么区别？

| 对比项 | `synchronized` | `ReentrantLock` |
| --- | --- | --- |
| 实现 | JVM monitor | JDK 实现，基于 AQS |
| 释放 | 自动释放 | 手动 `unlock()`，需要 `finally` |
| 公平性 | 不提供公平模式 | 支持公平和非公平 |
| 中断 | 等锁过程不能响应中断 | 支持 `lockInterruptibly()` |
| 超时 | 不支持 | 支持 `tryLock(time, unit)` |
| 条件队列 | 一个 WaitSet | 可创建多个 `Condition` |

简单同步优先使用 `synchronized`；需要超时、可中断、公平锁或多个条件队列时使用 `ReentrantLock`。

## 公平锁和非公平锁有什么区别？

公平锁按等待队列顺序获取锁；非公平锁允许新线程直接尝试抢锁，失败后再排队。

非公平锁通常吞吐更高，因为新线程可能直接 CAS 成功，减少线程唤醒和上下文切换；代价是可能造成饥饿。`ReentrantLock` 默认是非公平锁。

## ReadWriteLock 和 StampedLock 适合什么场景？

读写锁的规则是：读读共享，读写互斥，写写互斥。`ReentrantReadWriteLock` 适合读多写少的缓存、配置和路由表；写操作频繁时，锁管理成本可能抵消收益。

`StampedLock` 支持乐观读：读时不加互斥锁，读取后通过版本戳验证期间是否发生写入，适合读多写少但使用复杂度更高的场景。

## AQS 是什么？

AQS（`AbstractQueuedSynchronizer`）是构建锁和同步工具的基础框架。它解决“获取不到资源时如何排队、阻塞和唤醒”，具体资源含义由子类定义。

核心组成：

- `volatile int state`：同步状态。
- 基于 CLH 思想的 FIFO 双向等待队列。
- CAS：原子修改 `state`。
- 模板方法：子类实现 `tryAcquire`、`tryRelease` 等方法。

不同工具对 `state` 的含义不同：`ReentrantLock` 表示锁和重入次数，`Semaphore` 表示许可证数量，`CountDownLatch` 表示剩余倒计数。

## 如何用 AQS 实现可重入公平锁？

实现步骤：

1. 内部类继承 `AbstractQueuedSynchronizer`。
2. 用 `state` 表示重入次数，用 owner 记录持锁线程。
3. `tryAcquire` 中，`state == 0` 时先用 `hasQueuedPredecessors()` 保证公平，再 CAS 抢锁；当前线程已持锁时增加 `state`。
4. `tryRelease` 中减少 `state`，归零时清空 owner。
5. 外部 `lock()` 调用 `acquire(1)`，`unlock()` 调用 `release(1)`。

```java
protected boolean tryAcquire(int acquires) {
    Thread current = Thread.currentThread();
    int state = getState();
    if (state == 0) {
        if (!hasQueuedPredecessors()
                && compareAndSetState(0, acquires)) {
            setExclusiveOwnerThread(current);
            return true;
        }
    } else if (current == getExclusiveOwnerThread()) {
        setState(state + acquires);
        return true;
    }
    return false;
}
```

## 线程协作与 ThreadLocal

## sleep、wait 和 notify 有什么区别？

| 对比项 | `sleep()` | `wait()` |
| --- | --- | --- |
| 所属类 | `Thread` | `Object` |
| 是否释放锁 | 不释放 | 释放当前 monitor |
| 使用条件 | 任意位置 | 必须持有对应 monitor |
| 唤醒方式 | 到期或中断 | `notify/notifyAll`、超时或中断 |
| 作用 | 暂停线程 | 等待条件并进行线程协作 |

`wait()` 通常放在 while 循环中检查条件，避免虚假唤醒：

```java
synchronized (lock) {
    while (!condition) {
        lock.wait();
    }
}
```

## 不同线程之间如何通信？

- 共享变量：使用 `volatile` 或锁保证可见性和安全性。
- `wait/notify/notifyAll`：基于 monitor 的等待和唤醒。
- `Lock + Condition`：可以创建多个等待队列，精准唤醒。
- `BlockingQueue`：生产者消费者模型的常用方案。
- `CountDownLatch`、`CyclicBarrier`、`Semaphore`：控制线程协作和并发数量。
- `Future`、`CompletableFuture`：通过异步结果传递信息。

## CountDownLatch、CyclicBarrier 和 Semaphore 有什么区别？

| 工具 | 核心作用 | 是否可复用 | 典型场景 |
| --- | --- | --- | --- |
| `CountDownLatch` | 等待计数减到 0 | 不可复用 | 主线程等待多个子任务 |
| `CyclicBarrier` | 一组线程到齐后一起继续 | 可复用 | 多线程分阶段计算 |
| `Semaphore` | 控制许可证数量 | 可复用 | 限流、连接池 |

记忆方式：Latch 是“别人完成后我继续”，Barrier 是“大家到齐再继续”，Semaphore 是“控制同时进入的人数”。

## ThreadLocal 的作用、原理和内存泄漏是什么？

`ThreadLocal` 为每个线程保存独立变量副本，常用于用户上下文、traceId 和线程内资源上下文。

每个 `Thread` 内部有一个 `ThreadLocalMap`，key 是 `ThreadLocal` 的弱引用，value 是当前线程保存的副本。外部强引用消失后，key 可能被回收，但 value 仍可能被线程持有；在线程池中线程长期复用时，可能造成 value 长时间不释放。

使用完必须在 `finally` 中清理：

```java
try {
    threadLocal.set(value);
    doSomething();
} finally {
    threadLocal.remove();
}
```

## 线程池与异步编程

## ThreadPoolExecutor 提交任务的流程是什么？

1. 当前线程数小于 `corePoolSize`：创建核心线程执行任务。
2. 核心线程已满：任务进入 `workQueue`。
3. 队列已满且线程数小于 `maximumPoolSize`：创建非核心线程。
4. 线程数和队列都达到上限：执行拒绝策略。

记忆顺序：核心线程 → 队列 → 最大线程 → 拒绝。

## 线程池有哪些核心参数？

| 参数 | 含义 |
| --- | --- |
| `corePoolSize` | 核心线程数 |
| `maximumPoolSize` | 最大线程数，包含核心线程 |
| `keepAliveTime` | 非核心线程空闲回收时间 |
| `workQueue` | 等待队列 |
| `threadFactory` | 创建线程，设置名称和守护属性 |
| `handler` | 拒绝策略 |

调用 `allowCoreThreadTimeOut(true)` 后，核心线程空闲超时也可以回收。

## 线程池有哪些拒绝策略？

- `AbortPolicy`：默认策略，抛出 `RejectedExecutionException`。
- `CallerRunsPolicy`：提交任务的线程自己执行，形成反压。
- `DiscardPolicy`：直接丢弃，不抛异常。
- `DiscardOldestPolicy`：丢弃队列中最老任务，再尝试提交。

生产环境可以自定义拒绝策略，记录日志、告警、持久化任务或返回明确失败。

## 线程池参数如何设置？核心线程数可以是 0 吗？

常见经验：

- CPU 密集型：线程数约为 CPU 核数或核数 + 1。
- I/O 密集型：线程数可以大于 CPU 核数，可按等待时间与计算时间估算：

```text
线程数 = CPU 核数 × (1 + 等待时间 / 计算时间)
```

实践中应使用 `availableProcessors()`，优先使用有界队列，设置线程名，并监控活跃线程、队列长度、拒绝次数和任务耗时。

`corePoolSize = 0` 是允许的，任务通常先进入队列，再由非核心线程执行；适合任务零散、希望空闲时回收线程的场景，但不适合对延迟敏感的稳定服务。

## 为什么不建议直接使用 Executors？

- `newFixedThreadPool` 和 `newSingleThreadExecutor` 使用无界队列，任务积压可能导致 OOM。
- `newCachedThreadPool` 最大线程数接近无限，高并发下可能创建过多线程。
- 定时线程池也隐藏了关键参数，难以统一管理队列和拒绝策略。

生产中通常手动创建 `ThreadPoolExecutor`，明确线程数、队列、线程工厂和拒绝策略。

## 线程池如何关闭？任务可以撤回吗？

| 方法 | 行为 |
| --- | --- |
| `shutdown()` | 不接收新任务，已提交任务继续执行 |
| `shutdownNow()` | 不接收新任务，尝试中断执行中的任务，并返回未执行任务 |

`shutdownNow()` 只是发送中断信号，不保证任务立即结束。常见关闭流程：

```java
executor.shutdown();
if (!executor.awaitTermination(30, TimeUnit.SECONDS)) {
    executor.shutdownNow();
}
```

通过 `submit()` 得到 `Future` 后可以调用 `cancel(true)`：未开始的任务可以取消，执行中的任务只会收到中断信号，是否停止取决于任务是否响应中断。

## Future、FutureTask 和 CompletableFuture 有什么区别？

| 类型 | 作用 | 特点 |
| --- | --- | --- |
| `Future` | 异步结果接口 | 可获取结果、取消、判断完成，但编排能力弱 |
| `FutureTask` | `Runnable` + `Future` | 可包装 `Callable` 交给线程执行 |
| `CompletableFuture` | 异步编排 | 支持链式转换、组合、超时和异常处理 |

常用 API：

- `supplyAsync`/`runAsync`：异步执行。
- `thenApply`/`thenAccept`/`thenRun`：处理前一步结果。
- `thenCompose`：串联返回另一个 Future 的异步任务。
- `thenCombine`：合并两个任务结果。
- `allOf`/`anyOf`：等待全部或任意任务。
- `exceptionally`/`handle`：处理异常。
- Java 9+ 的 `orTimeout`/`completeOnTimeout`：处理超时。

```java
CompletableFuture<Integer> future = CompletableFuture
        .supplyAsync(this::query)
        .thenApply(result -> result + 1)
        .exceptionally(e -> 0);
```

默认异步任务可能使用公共 `ForkJoinPool.commonPool()`。生产环境应根据任务类型指定自定义线程池，尤其要避免阻塞 I/O 任务耗尽公共线程池。

## 并发场景题

## 什么情况下会产生死锁？如何避免？

死锁需要同时满足：互斥、持有并等待、不可剥夺、循环等待。

常见避免方式：

- 固定加锁顺序，破坏循环等待。
- 避免嵌套锁，缩短锁持有时间。
- 使用 `tryLock(time, unit)`，超时后释放已持有锁并重试。
- 缩小锁粒度，减少竞争。
- 使用 `jstack` 或线程 dump 排查 `BLOCKED` 和死锁信息。

## 如何设计生产者消费者模型？

优先使用 `BlockingQueue`，让队列负责线程安全、容量控制和等待唤醒：

```java
BlockingQueue<Task> queue = new ArrayBlockingQueue<>(1000);

// producer
queue.put(task);

// consumer
Task task = queue.take();
handle(task);
```

停止消费者可以使用中断，或放入特殊结束标记。

## 高并发计数器如何实现？

- 低并发或需要精确即时值：`AtomicInteger`、`AtomicLong`。
- 高并发热点计数：`LongAdder`，通过分散到多个分段降低 CAS 冲突。
- 强一致业务计数：数据库事务、行锁或版本号。

`LongAdder` 的吞吐量通常高于 `AtomicLong`，但 `sum()` 是多个分段的汇总，不适合要求每次读取都具备严格线性一致性的场景。

## 双重检查锁为什么需要 volatile？

```java
public final class Singleton {
    private static volatile Singleton instance;

    private Singleton() {}

    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

`volatile` 保证实例引用的可见性，并禁止“分配内存、初始化对象、发布引用”发生危险重排序。没有延迟加载要求时，可直接使用静态初始化或枚举单例，减少实现和反序列化风险。
