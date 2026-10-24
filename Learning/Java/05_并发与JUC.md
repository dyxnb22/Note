# 05 并发与 JUC

线程生命周期解释工作何时开始和结束，内存模型解释共享状态何时可见，锁与队列负责协调，线程池把资源约束落到执行过程。

## 线程与生命周期

任务是需要完成的工作，线程是运行工作的一种执行资源。启动、等待、取消和退出必须形成完整协议。
### 平台线程与操作系统线程

在主流 HotSpot JVM 中，Java 平台线程通常与操作系统内核线程**一对一映射**，线程的调度、阻塞和唤醒最终依赖操作系统
### 并发、并行与等待

线程安全通常从三个维度理解：

- 原子性：操作不可被并发打断，常用 `synchronized`、`Lock`、`Atomic`。
- 可见性：一个线程的修改能被其他线程及时看到，常用 `volatile`、锁。
- **有序性**：执行顺序符合预期，需要依赖**锁、`volatile` 和 happens-before**。

如果共享状态可以改为局部变量、不可变对象或线程隔离数据，应优先减少共享，而不是一开始就加锁。

### 任务与线程的创建

| 方式            | 特点               | 适用场景        |
| ------------- | ---------------- | ----------- |
| 继承 `Thread`   | 写法简单，但受单继承限制     | Demo 或特殊线程类 |
| 实现 `Runnable` | 任务和线程解耦，**无返回值** | 普通无返回值任务    |
| 实现 `Callable` | 有返回值，**可抛受检异常**  | 需要异步结果      |
| 使用线程池         | 复用线程、控制并发和生命周期   | 生产环境首选      |


```java
Callable<Integer> task = () -> 1;
FutureTask<Integer> futureTask = new FutureTask<>(task);
new Thread(futureTask).start();
Integer result = futureTask.get();
```

生产环境一般不频繁手动 `new Thread()`，而是使用自定义 `ThreadPoolExecutor`。

### Run 与 Start 的执行方式

- `run()` 只是**普通方法调用**，在当前线程中同步执行，不会创建新线程。
- `start()` 才会**创建并启动新线程**，由 JVM 在新线程中调用 `run()`；**同一个 `Thread` 只能成功调用一次 `start()`。**

```java
Thread t = new Thread(() -> System.out.println(Thread.currentThread().getName()));
t.run();   // 当前线程执行
t.start(); // 新线程执行；只能调用一次
```

线程**已经结束后再次调用 `start()` 会抛出 `IllegalThreadStateException`**。

### 线程状态与转移

| 状态              | 含义                      |
| --------------- | ----------------------- |
| `NEW`           | 已创建但未调用 `start()`       |
| `RUNNABLE`      | 可运行，包含就绪和正在运行           |
| `BLOCKED`       | 等待进入 `synchronized` 临界区 |
| `WAITING`       | 无限期等待其他线程唤醒             |
| `TIMED_WAITING` | 限时等待                    |
| `TERMINATED`    | 执行结束                    |

**`RUNNABLE` 不等于一定正在 CPU 上运行，也可能正在等待操作系统调度**。

### 阻塞、等待与定时等待

- `BLOCKED`：抢不到 `synchronized` 的 **monitor 锁，等待其他线程释放**。
- `WAITING`：**主动等待其他线程动作**，例如 `wait()`、`join()`、`LockSupport.park()`。
- `TIMED_WAITING`：**带超时的等待**，例如 `sleep(time)`、`wait(time)`、`join(time)`。

**`wait()` 会释放当前 monitor；`sleep()` 不释放锁；`park()` 不依赖 monitor。**

### 中断与协作停止

不要使用 `Thread.stop()`、`suspend()`、`resume()`。它们可能**强制释放锁**、破坏共享状态或造成死锁。

常用方式是**让线程协作退出**：

- 使用 `volatile` 标志位。
- 调用 `interrupt()`，让**线程检查中断状态并退出**。
- 对支持执行线程中断的 Future 实现使用 cancel(true)，例如 Executor 提交任务对应的 FutureTask；取消结果与线程退出仍需分别确认。
- **关闭阻塞中的资源，使线程从 I/O 调用返回**。

Thread.stop 可能在任意位置终止并释放监视器，suspend 则可能让持锁线程暂停，这也是这些旧 API 不能用于正常取消协议的原因。

interrupt 不会强行杀死线程，响应方式取决于所在 API。sleep、wait、join、Condition.await 等可中断等待会按相应API的约定抛出InterruptedException；可中断通道可能关闭并抛出相关 I/O 异常。普通计算代码需要检查中断标志并协作退出，不能假设任意阻塞操作都能被中断唤醒。[Thread中断行为](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/Thread.html#interrupt())

### 守护线程与未捕获异常

守护线程只适合执行随进程生命周期结束即可丢弃的后台辅助工作。所有非守护线程结束后，JVM 可以退出，**不会等待守护线程完成**；必须在 `start()` 前调用 `setDaemon(true)`。需要**持久化、提交事务或保证最终执行的任务不能依赖守护线程**。

线程未捕获异常时，该线程会终止，可以通过 `Thread.UncaughtExceptionHandler` 记录和告警。在线程池中还要注意：`execute()` 的异常通常会交给**线程的未捕获异常处理器**，而 `submit()` 会把异常**封装在 `Future` 中，需要调用 `Future.get()` 才能观察到**。

## Java 内存模型与线程安全

多线程同时访问共享可变状态时，既要保护复合操作，也要建立可见性。原子性、可见性和顺序性需要分别分析。
### 共享状态与线程安全

| 思路        | 代表技术                                                       | 适用场景        |
| --------- | ---------------------------------------------------------- | ----------- |
| 状态隔离 | 独占状态、ThreadLocal 独立绑定 | 减少共享可变状态，仍要分析引用对象 |
| 不可变共享 | 正确构造和发布的不可变对象 | 安全共享只读内容，引用替换另需协议 |
| **互斥访问**  | `synchronized`、`ReentrantLock`                             | 保护共享读写      |
| **可见性控制** | `volatile`                                                 | 状态标记、配置开关   |
| 原子更新      | `AtomicInteger`、`AtomicReference`、`LongAdder`              | 计数和 CAS 更新  |
| 并发容器      | `ConcurrentHashMap`、`CopyOnWriteArrayList`、`BlockingQueue` | 替代手写加锁集合    |
| 协作工具      | `CountDownLatch`、`CyclicBarrier`、`Semaphore`               | 控制线程协作和并发数量 |

业务数据**跨线程、跨进程或跨服务**时，还要结合数据库事务、唯一约束、版本号、幂等和最终一致性方案，不能只依赖 Java 锁。

### 重排序与 happens-before

JMM 规定的是可观察行为与同步关系，不要求机器逐行照源码顺序执行。同一线程必须保持相应程序语义；跨线程读取共享状态则需要 happens-before 关系，不能用“我大概先写完了”或日志先后建立保证。

同一 monitor 的解锁与后续加锁、对同一 volatile 的写与同步顺序中后续读、线程 start 与新线程中的操作，以及成功检测到线程终止，都能形成相应关系，再通过传递性发布之前的普通字段。带超时的 join 如果只是超时返回，不能据此认为线程已结束。

下面先写普通字段，再发布 volatile 标志；读者观察到标志后才读取字段。末尾 join 负责收尾，并没有被用来代替标志读取之前的发布协议。

```java
import java.util.concurrent.TimeUnit;

public class PublicationDemo {
    static int value;
    static volatile boolean ready;

    public static void main(String[] args) throws InterruptedException {
        Thread writer = new Thread(() -> {
            value = 42;
            ready = true;
        });
        writer.start();
        long started = System.nanoTime();
        while (!ready) {
            if (System.nanoTime() - started > TimeUnit.SECONDS.toNanos(5))
                throw new AssertionError("等待发布超时");
            Thread.onSpinWait();
        }
        int observed = value;
        writer.join();
        assert observed == 42;
    }
}
```

这个例子使用短暂自旋说明内存语义；长期任务协调通常用锁、条件或阻塞队列，避免持续占用 CPU。volatile 保证相应读写关系，不保证线程会按期得到调度，也不提供整组字段的原子事务。

### Volatile 与可见性

volatile 适合发布状态或不可变快照引用。读者需要通过同一变量的相应读写关系观察之前的普通写入，不能把它理解成“任意字段随时自动同步到最新”。

volatile 的单次读写与复合操作不同：counter++ 包含读、计算、写，仍可能丢更新。多个字段需要共同保持不变量时，使用同一锁或完整状态的原子替换；双重检查锁中的实例引用也是发布协议，而不是把所有对象字段都变成线程安全。

### CAS、竞争与 ABA

CAS（Compare And Swap）包含**内存值 V、预期值 A 和新值 B：只有 V 等于 A 时，才把 V 更新为 B**。它是 Java 原子类和许多无锁算法的基础。

缺点：

- ABA：值从 A 变成 B 又变回 A，CAS 可能误判；可用 **`AtomicStampedReference` 加版本号**。
- 自旋开销：竞争激烈时 **CAS 反复失败，会浪费 CPU**。
- **多变量**一致性有限：需要用 `AtomicReference` **封装对象或使用锁**。

### 原子计数与分片累加

AtomicLong.incrementAndGet 为单个实例分配本次原子更新后的值；在未溢出、未重置的区间内，可形成不同的序号。调用者完成顺序、业务成功顺序与序号分配顺序仍可能不同，也不提供进程重启后的持久全局编号。

LongAdder 把竞争更新分散到多个单元，sum 在并发更新期间不是原子快照。所有写线程完成并经 join 等方式交接后，sum 可以准确读取最终总和；不能把这种情况写成“线程已经完成仍必然少计”。它不返回每次增量专属的新序号，increment 后再 sum 也可能与别人拿到相同结果。[LongAdder API](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/atomic/LongAdder.html)

```java
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.LongAdder;

public class CountingSemanticsDemo {
    public static void main(String[] args) throws InterruptedException {
        AtomicLong sequence = new AtomicLong();
        LongAdder total = new LongAdder();
        Set<Long> ids = ConcurrentHashMap.newKeySet();
        Runnable work = () -> {
            for (int i = 0; i < 1000; i++) {
                long id = sequence.incrementAndGet();
                ids.add(id);
                total.increment();
            }
        };
        Thread first = new Thread(work), second = new Thread(work);
        first.start(); second.start();
        first.join(); second.join();
        assert sequence.get() == 2000;
        assert total.sum() == 2000;
        assert ids.size() == 2000;
    }
}
```

AtomicLong 适合需要更新返回值或条件修改的单点状态，LongAdder 常用于允许采集期间统计偏差的热点指标。两者的收益取决于竞争与读写比例，sumThenReset 也不能直接作为并发无损结算边界。

### 悲观与乐观并发控制

| 对比项 | 悲观锁                                  | 乐观锁              |
| --- | ------------------------------------ | ---------------- |
| 思路  | 假设冲突会发生，操作前加锁                        | 假设冲突较少，**提交时检查** |
| 代表  | `synchronized`、`ReentrantLock`、数据库行锁 | CAS、版本号、时间戳      |
| 优点  | 逻辑简单，适合强互斥                           | 无阻塞，低冲突时性能好      |
| 缺点  | 可能阻塞和上下文切换                           | **冲突高时重试成本高**    |

## Java 锁机制与 AQS

### Monitor 与 synchronized

`synchronized` 是 JVM 内置的 monitor 锁，可以保证**互斥、可见性和有序性**：

- 同步代码块编译后对应 `monitorenter` 和 `monitorexit`。
- 同步方法通过 **`ACC_SYNCHRONIZED` 标记，由 JVM 隐式加锁**。
- 获取不到锁的线程进入**等待队列**；**调用 `wait()` 的线程进入 WaitSet**。
- 解锁时会建立相应的内存可见性关系。

### 实例锁、类锁与锁对象

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

### 可重入与持有计数

可重入意味着同一线程已经持有某把锁时，可以再次进入由同一把锁保护的同步代码，不会被自己阻塞。

**monitor 会记录持锁线程和重入次数**；每进入一次计数加 1，每退出一次计数减 1，计数归零后才真正释放锁。

### 锁实现演进与编译优化

历史上常用“**无锁 → 偏向锁 → 轻量级锁 → 重量级锁**”描述锁状态变化。偏向锁是旧版本 HotSpot 的优化，JDK 15 起默认关闭并逐步废弃；现代 JDK 更应理解为无竞争或轻竞争时使用轻量级路径，竞争激烈时膨胀为重量级 monitor。

JIT 还可能进行：

- 锁消除：通过逃逸分析判断对象不共享时，**消除无意义同步**。
- 锁粗化：**合并连续的加锁和解锁，减少频繁开销**。
- 自适应自旋：**短时间自旋等待锁释放，避免立即阻塞和唤醒**。

这些属于具体 JVM 实现优化，不应当作 Java 语言层面的绝对保证。

### ReentrantLock 与显式解锁

`ReentrantLock` 是**基于 AQS 的显式锁**。AQS 中的 **`state` 表示锁状态和重入次数**，owner 表示当前持锁线程，获取失败的线程会进入等待队列并通过 `LockSupport.park()` 挂起。

核心逻辑：

- `state == 0` 时通过 CAS 抢锁并设置 owner。
- 当前线程已经是 owner 时，**增加 `state` 实现重入**。
- 每次释放锁减少 `state`，归零后唤醒后继线程。

它支持公平/非公平模式、可中断获取、超时获取和多个 `Condition` 等待队列。使用时必须在 `finally` 中释放锁。

### 内置锁与显式锁的选择

| 对比项  | `synchronized` | `ReentrantLock`            |
| ---- | -------------- | -------------------------- |
| 实现   | JVM monitor    | JDK 实现，基于 AQS              |
| 释放   | 自动释放           | 手动 `unlock()`，需要 `finally` |
| 公平性  | 不提供公平模式        | 支持公平和非公平                   |
| 中断   | 等锁过程不能响应中断     | 支持 `lockInterruptibly()`   |
| 超时   | 不支持            | 支持 `tryLock(time, unit)`   |
| 条件队列 | 一个 WaitSet     | 可创建多个 `Condition`          |

简单同步优先使用 `synchronized`；需要超时、可中断、公平锁或多个条件队列时使用 `ReentrantLock`。

### 公平性与吞吐

公平锁按等待队列顺序获取锁；非公平锁允许新线程直接尝试抢锁，失败后再排队。

非公平锁**通常吞吐更高**，因为**新线程可能直接 CAS 成功，减少线程唤醒和上下文切换；代价是可能造成饥饿**。`ReentrantLock` 默认是非公平锁。

### 读写锁与乐观读

ReentrantReadWriteLock 允许多个读者共享，写入则排斥其他读者和写者。收益取决于读写比例、临界区长度与争用，读多也不保证比普通锁快；持有读锁再升级写锁尤其需要避免等待死锁。

StampedLock 的乐观读先把字段读入局部变量，再验证 stamp；验证失败时重新加读锁获取一致值，不能在验证前就拿可能不一致的字段执行不可撤销动作。它不提供与 ReentrantLock 相同的可重入语义，不能机械替换原有锁。

### AQS 的状态与等待队列

AQS 为同步器提供状态、等待、取消与唤醒框架，子类定义 tryAcquire/tryRelease 等方法。volatile state 的含义由具体同步器决定：可重入锁表示占用计数，Semaphore 表示许可证，CountDownLatch 表示剩余计数。

等待节点用前后链接组织，取消或链接暂时不完整时可辅助寻找前驱与后继。队列具有先后关系，不代表所有同步器必然公平；是否允许新请求插队由获取策略决定，hasQueuedPredecessors 等检查用于相应策略，不应简化成每次公平判断都从 tail 遍历到 head。

### 可重入公平锁的状态设计

获取逻辑需要同时解释空闲状态、排队者与重入：空闲时先检查更早等待者，再 CAS；当前线程已持有时增加计数，且检查溢出。下面仅为 AQS 子类中的获取片段，并非完整锁实现。

```java
protected boolean tryAcquire(int acquires) {
    Thread current = Thread.currentThread();
    int held = getState();
    if (held == 0) {
        if (!hasQueuedPredecessors() && compareAndSetState(0, acquires)) {
            setExclusiveOwnerThread(current);
            return true;
        }
    } else if (current == getExclusiveOwnerThread()) {
        int next = held + acquires;
        if (next < 0) throw new Error("重入计数溢出");
        setState(next);
        return true;
    }
    return false;
}
```

完整实现还需校验释放者、逐次减少计数、归零清空 owner，并实现条件等待需要的持锁判断等协议。实际使用优先选择已验证的 ReentrantLock；即便启用公平模式，也不意味着操作系统调度绝对公平，不带超时的 tryLock 还允许直接尝试获取。

## Java 线程协作与 ThreadLocal

### 休眠、等待与唤醒

| 对比项   | `sleep()` | `wait()`                     |
| ----- | --------- | ---------------------------- |
| 所属类   | `Thread`  | `Object`                     |
| 是否释放锁 | 不释放       | **释放当前 monitor**             |
| 使用条件  | 任意位置      | 必须持有对应 monitor               |
| 唤醒方式  | **到期或中断** | **`notify/notifyAll`、超时或中断** |
| 作用    | 暂停线程      | 等待条件并进行线程协作                  |

`wait()` 通常放在 **while 循环中检查条件**，避免虚假唤醒：

```java
synchronized (lock) {
    while (!condition) {
        lock.wait();
    }
}
```

### 线程通信与条件队列

- **共享变量**：使用 `volatile` 或锁保证可见性和安全性。
- `wait/notify/notifyAll`：基于 monitor 的等待和唤醒。
- `Lock + Condition`：可以创建多个**等待队列**，精准唤醒。
- `BlockingQueue`：生产者消费者模型的常用方案。
- `CountDownLatch`、`CyclicBarrier`、`Semaphore`：控制线程协作和并发数量。
- `Future`、`CompletableFuture`：通过异步结果传递信息。

### Latch、Barrier 与 Semaphore

| 工具               | 核心作用            | 是否可复用 | 典型场景       |
| ---------------- | --------------- | ----- | ---------- |
| `CountDownLatch` | **等待计数减到 0**    | 不可复用  | 主线程等待多个子任务 |
| `CyclicBarrier`  | **一组线程到齐后一起继续** | 可复用   | 多线程分阶段计算   |
| `Semaphore`      | **控制许可证数量**     | 可复用   | 限流、连接池     |

记忆方式：Latch 是“别人完成后我继续”，Barrier 是“大家到齐再继续”，Semaphore 是“控制同时进入的人数”。

### ThreadLocal 与生命周期

ThreadLocal 为每个线程保存独立的值绑定，常用于用户上下文或线程内资源。它不会自动深拷贝值；若两个线程 set 同一个可变对象，仍共享该对象并需要同步。

每个 `Thread` 内部有一个 `ThreadLocalMap`，key 是 **`ThreadLocal` 的弱引用**，value 是当前线程绑定的对象引用。外部强引用消失后，key 可能被回收，但 value 仍可能被线程持有；在线程池中线程长期复用时，可能造成 value 长时间不释放。

在线程池任务边界通常需要在 finally 清理；若存在嵌套上下文或调用方线程内执行，还应保存并恢复旧值。下面是本任务独占该绑定时的清理片段：

```java
try {
    threadLocal.set(value);
    doSomething();
} finally {
    threadLocal.remove();
}
```

## Java 线程池与异步编程

线程池复用执行资源，队列缓冲任务，但也会把过载变成排队。资源上限、拒绝策略与超时需要一起设计。
### 线程池的任务接收流程

1. 当前线程数小于 `corePoolSize`：创建核心线程执行任务。
2. 核心线程已满：任务进入 **`workQueue`**。
3. 队列已满且线程数小于 `maximumPoolSize`：创建**非核心线程**。
4. 线程数和队列都达到上限：执行拒绝策略。

记忆顺序：**核心线程 → 队列 → 最大线程 → 拒绝**。

### 线程池容量与核心参数

| 参数                | 含义              |
| ----------------- | --------------- |
| `corePoolSize`    | 核心线程数           |
| `maximumPoolSize` | 最大线程数，包含核心线程    |
| `keepAliveTime`   | 非核心线程**空闲回收时间** |
| `workQueue`       | 等待队列            |
| `threadFactory`   | 创建线程，设置名称和守护属性  |
| `handler`         | **拒绝策略**        |

调用 `allowCoreThreadTimeOut(true)` 后，核心线程空闲超时也可以回收。

### 饱和后的拒绝策略

- `AbortPolicy`：默认策略，抛出 `RejectedExecutionException`。
- CallerRunsPolicy：执行器尚未关闭时由提交线程运行，形成背压；关闭后会丢弃，不能当成总会执行的承诺。
- `DiscardPolicy`：直接丢弃，**不抛异常**。
- DiscardOldestPolicy：未关闭时丢弃队头并重试提交。FIFO 队列的队头通常最早入队，优先队列的队头则可能是最高优先级任务。

拒绝必须形成可观察结果。使用 submit 却静默丢弃其 FutureTask 时，调用方的 Future 可能一直未完成；需要明确失败、取消或持久化重试，不能只记录一行日志就让调用者永久等待。

### 线程数、队列与负载模型

平台线程池的规模可从可用 CPU、目标利用率和等待/计算时间比估算，但只是负载模型的起点。CPU 密集工作受可用核数约束，阻塞较多的工作可用更多线程隐藏等待，最终仍受到连接池、下游配额、内存与超时约束。

无界队列几乎总能接受任务，线程池便很少走 maximumPoolSize 的扩容分支；corePoolSize=0 配无界队列还可能只补出一个工作线程排空任务。SynchronousQueue、有限容量队列与无界队列会形成不同调度行为，不能只看核心线程数判断容量。

用目标负载比较活跃线程、排队时间、拒绝数和完成速率，再决定上限与等待预算。增加线程只会增加排队者的场景，不应继续用经验公式放大并发。

### Executors 工厂与默认策略

- `newFixedThreadPool` 和 `newSingleThreadExecutor` 使用无界队列，**任务积压可能导致 OOM**。
- `newCachedThreadPool` **最大线程数接近无限**，高并发下可能创建过多线程。
- 定时线程池也需要观察待执行任务、周期任务失败与关闭策略；工厂方法的便捷不等于资源与故障边界已经设计完成。

生产中通常手动创建 `ThreadPoolExecutor`，明确线程数、队列、线程工厂和拒绝策略。

### 线程池关闭与任务取消

| 方法              | 行为                             |
| --------------- | ------------------------------ |
| `shutdown()`    | 不接收新任务，**已提交任务继续执行**           |
| `shutdownNow()` | 不接收新任务，尝试中断执行中的任务，**并返回未执行任务** |

`shutdownNow()` **只是发送中断信号，不保证任务立即结束**。常见关闭流程：

```java
executor.shutdown();
if (!executor.awaitTermination(30, TimeUnit.SECONDS)) {
    executor.shutdownNow();
}
```

awaitTermination 被中断时需按调用约定传播或恢复中断标志，并触发适当停止；升级到 shutdownNow 后还要再次有界等待，才能确认执行器是否终止。返回的未开始任务也要进入取消或恢复流程，尤其是关联 Future 的任务不能永远悬空。

Executor 常见 FutureTask 的 cancel(true) 会尝试中断执行线程，但取消成功不等于动作已退出；CompletableFuture 的取消则有不同语义，见下节。

### Future 与异步组合

Future 表达一个结果的等待与取消，FutureTask 还能作为 Runnable 执行；CompletableFuture 增加转换、组合和异常完成。thenApply 转换结果，thenCompose 展开下一异步阶段，thenCombine 合并两个结果；allOf 提供全体完成信号，本身不自动收集结果值。

非 Async 的后续操作可能在完成前一阶段的线程中运行，也可能在附加操作的调用线程中运行；Async 版本再按配置选择执行器。阻塞工作、上下文与容量需按这些执行边界安排。

CompletableFuture.cancel(true) 将阶段标为取消，不会因为 true 自动中断其底层计算。下面用两个闩锁分开“任务已开始”“允许任务完成”，观察取消之后任务仍需自己走完。

```java
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

public class CompletableCancellationDemo {
    public static void main(String[] args) throws Exception {
        var executor = Executors.newSingleThreadExecutor();
        CountDownLatch entered = new CountDownLatch(1);
        CountDownLatch release = new CountDownLatch(1);
        AtomicBoolean interrupted = new AtomicBoolean();
        try {
            CompletableFuture<Integer> future = CompletableFuture.supplyAsync(() -> {
                entered.countDown();
                try {
                    release.await();
                    return 42;
                } catch (InterruptedException error) {
                    interrupted.set(true);
                    Thread.currentThread().interrupt();
                    throw new CompletionException(error);
                }
            }, executor);
            if (!entered.await(5, TimeUnit.SECONDS))
                throw new AssertionError("任务未启动");
            boolean cancelled = future.cancel(true);
            assert cancelled && future.isCancelled();
            release.countDown();
            executor.shutdown();
            boolean stopped = executor.awaitTermination(5, TimeUnit.SECONDS);
            assert stopped && !interrupted.get();
        } finally {
            release.countDown();
            executor.shutdownNow();
        }
    }
}
```

这段代码只提交一个受控任务，用单线程执行器观察 API 行为。实际外部调用还需自己的超时和协作取消；阶段完成、计算结束、业务终态是三件事。[CompletableFuture 取消语义](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/CompletableFuture.html#cancel(boolean))

### 异步异常、超时与线程隔离

先为不同依赖使用有界且可观测的执行器，再让每个外部调用自己有 deadline；组合层显式规定“一个失败是否取消兄弟任务、能否返回部分结果、fallback 是否掩盖错误”。`orTimeout` 只会让 Future 以超时异常完成，不保证底层阻塞 I/O 已经停止，因此还要向客户端/任务传播取消并配置底层连接与读取超时。

```java
CompletableFuture<Result> left = CompletableFuture
        .supplyAsync(() -> queryLeft(requestId), ioExecutor)
        .orTimeout(300, TimeUnit.MILLISECONDS);

CompletableFuture<Result> right = CompletableFuture
        .supplyAsync(() -> queryRight(requestId), ioExecutor)
        .orTimeout(300, TimeUnit.MILLISECONDS);

return left.thenCombine(right, this::merge)
        .whenComplete((value, error) -> recordOutcome(requestId, error));
```

在 `exceptionally` 中无条件返回空对象，会把依赖故障伪装成业务成功。异步阶段若依赖ThreadLocal，还可能丢失认证或Trace上下文。

`allOf()`只返回完成信号，调用方仍需逐个读取结果并处理异常。

验证这些行为时，覆盖单分支失败、整体超时、队列满、取消与服务关闭，并观察活跃线程、队列长度、拒绝数和端到端P95/P99。


## 并发约束的组合应用

锁、队列和线程池分别解决局部协调问题。多个机制组合后，还需要检查资源等待顺序、任务取消和业务状态是否能够一起收敛。

### 死锁条件与资源顺序

死锁需要同时满足：**互斥、持有并等待、不可剥夺、循环等待**。

常见避免方式：
- 固定**加锁顺序**，破坏循环等待。
- 避免嵌套锁，**缩短锁持有时间**。
- 使用 `tryLock(time, unit)`，**超时后释放已持有锁并重试**。
- **缩小锁粒度**，减少竞争。
- 使用 `jstack` 或线程 dump 排查 `BLOCKED` 和死锁信息。

### 生产者消费者与背压

优先使用 **`BlockingQueue`，让队列负责线程安全、容量控制和等待唤醒**：

```java
BlockingQueue<Task> queue = new ArrayBlockingQueue<>(1000);

// producer
queue.put(task);

// consumer
Task task = queue.take();
handle(task);
```

停止消费者可以使用中断，或放入特殊结束标记。

### 并发计数与精确快照

单个原子字段的读取不等于一组业务数据的同一时刻快照。例如 count 与 total 各自是 AtomicLong，分别读取时仍可能跨过一次更新，得到彼此不对应的两个值。

需要共同不变量时，可在同一锁下读写，或用 AtomicReference 发布完整不可变状态；跨进程时再选择共享存储与事务协议。对 CAS 更新函数还要避免不可重试的外部副作用，因为竞争失败后的计算可能再次执行。

### 单例发布与双重检查

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

`volatile` 保证实例引用的**可见性**，并禁止“分配内存、初始化对象、发布引用”发生危险重排序。没有延迟加载要求时，可直接使用静态初始化或枚举单例，减少实现和反序列化风险。

### 许可交接与顺序执行

这个例子连接了同步与执行顺序。核心是“轮到谁”这个状态必须原子可见、唤醒要精确。用 `Semaphore` 传递许可是最短写法：

```java
Semaphore sa = new Semaphore(1), sb = new Semaphore(0), sc = new Semaphore(0);

// 线程 A：拿 sa，打印后把许可交给 B
sa.acquire();
System.out.print("A");
sb.release();
// 线程 B：sb.acquire() → 打印 B → sc.release()
// 线程 C：sc.acquire() → 打印 C → sa.release()
```

另两种等价写法：`ReentrantLock` + 每个线程一个 `Condition`，`signal` 精确唤醒下一个；`synchronized` + `wait/notifyAll`，单一通知队列只能全员唤醒，靠共享 state 判断是否轮到自己（有惊群开销）。

易错点：等待条件用 `if` 而不是 `while`（虚假唤醒后继续跑）；`state++` 没在锁内做（原子性、可见性都不保证）；异常路径没有组级退出协议，其余线程可能永久等待。中断导致 acquire 失败时不能无条件释放一个从未取得的许可；失败应触发整体取消或明确终止状态，而非继续按成功顺序交接。

### 并发 LRU 的一致不变量

基线版本：`LinkedHashMap` 开启 access-order，重写 `removeEldestEntry`，访问加同一把锁：

```java
class LruCache<K, V> {
    private final Map<K, V> map;

    LruCache(int capacity) {
        this.map = new LinkedHashMap<>(capacity, 0.75f, true) {
            @Override
            protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
                return size() > capacity;
            }
        };
    }

    synchronized V get(K key) { return map.get(key); }
    synchronized void put(K key, V value) { map.put(key, value); }
}
```

上面的实现用一把锁保护整个 Map 与访问链，get 也会调整顺序，所以不能仅把它当只读操作放开同步。不同 Key 也竞争同一把锁；进一步优化要同时说明成本与淘汰语义的变化：

- 分片维护 LinkedHashMap 与锁可减少竞争，但得到的是分片内 LRU；热点分片可能已淘汰，其他分片仍有空余，不能继续声称严格全局 LRU。
- **读写路径分离**：`ConcurrentHashMap` 存数据承担并发读写，访问顺序链表单独同步；顺序维护本身仍有竞争，缓冲访问记录、批量修剪还会延迟顺序更新，需要说明是否接受近似淘汰。
- **TTL 淘汰**：节点带过期时间戳，读时惰性检查过期，再配后台清扫，避免定时线程全表扫描。

同一思想在其他层的实现：Redis 的近似 LRU 与淘汰池见 [Redis](../Data/Redis.md)，纯数据结构的实现思路见 [数据结构](../CS/数据结构.md)。

### 并发模式的行为与边界

这些并发模式共享同一套推理过程：确定状态、不变量、等待条件与退出路径，再选择同步原语。

| 使用场景 | 核心机制 | 易错点 |
|---|---|---|
| 交替打印 ABC / 1~100 | Condition 精确唤醒、Semaphore 传递、wait/notifyAll + 状态 | 用 if 判断状态；漏 signal/release |
| 生产者消费者 | `BlockingQueue` 或手写有界队列 | 停止语义（中断还是毒丸对象）没说清 |
| 有界任务交接 | `ReentrantLock` + notFull/notEmpty 两个 Condition | 满队 put、空队 take 的阻塞边界 |
| 并发安全 LRU | access-order + 锁粒度演进 | 只保护 Map，遗漏访问顺序的同步 |
| 令牌桶/滑动窗口限流器 | CAS 更新时间戳与令牌数 | 时间回拨、惰性补发令牌的边界 |

算法类实现（纯数据结构版 LRU/LFU、链表与堆类）见 [数据结构](../CS/数据结构.md)。
