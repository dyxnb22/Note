# JUC

# 线程基础
<details>
<summary>Java 线程和操作系统线程是什么关系</summary>
	在现代主流 HotSpot JVM 中，Java 线程通常与操作系统内核线程是一对一映射关系，底层会通过 `pthread_create` 等系统调用创建系统线程，所以线程调度、阻塞、唤醒最终**依赖操作系统**。**主流 HotSpot 是 1:1 线程模型**。
</details>
<details>
<summary>使用多线程要注意哪些核心问题</summary>
	多线程的核心问题是**线程安全**，主要看三个维度：
	- 原子性：常见手段有 `synchronized`、`Lock`、`Atomic` 原子类。
	- 可见性：一个线程修改共享变量后，其他线程能及时看到。常见手段有 `volatile`、`synchronized`、`Lock`。
	- 有序性：程序执行顺序在多线程下仍符合预期。编译器和 CPU 可能为了优化进行**指令重排序**，Java 通过 `volatile`、`synchronized` 和 happens-before 规则限制重排序。
</details>
<details>
<summary>线程的创建方式有哪些</summary>
	<table header-row="true" header-column="false">
<tr>
<td>方式</td>
<td>写法</td>
<td>优点</td>
<td>缺点</td>
<td>适用场景</td>
</tr>
<tr>
<td>继承 `Thread`</td>
<td>重写 `run()`，调用 `start()`</td>
<td>简单，能直接使用 `this` 获取当前线程对象</td>
<td>Java 单继承，扩展性差</td>
<td>简单 demo，不推荐生产大量使用</td>
</tr>
<tr>
<td>实现 `Runnable`</td>
<td>实现 `run()`，交给 `Thread`</td>
<td>任务和线程解耦，可继承其他类，可多个线程共享同一个任务对象</td>
<td>没有返回值，不能直接抛受检异常</td>
<td>普通无返回值任务</td>
</tr>
<tr>
<td>实现 `Callable`</td>
<td>实现 `call()`，配合 `FutureTask` 或线程池</td>
<td>有返回值，可抛受检异常</td>
<td>写法比 `Runnable` 复杂</td>
<td>需要获取异步执行结果</td>
</tr>
<tr>
<td>使用线程池</td>
<td>`ExecutorService.submit/execute`</td>
<td>复用线程、控制并发量、统一管理生命周期</td>
<td>参数配置不当会导致 OOM、拒绝任务或排查困难</td>
<td>生产环境首选</td>
</tr>
	</table>
	示例：
	```java
Callable<Integer> task = () -> 1;
FutureTask<Integer> futureTask = new FutureTask<>(task);
new Thread(futureTask).start();
Integer result = futureTask.get();
	```
	生产中一般不手动频繁 `new Thread()`，而是使用自定义 `ThreadPoolExecutor`。
</details>
<details>
<summary>Java 线程有哪些状态</summary>
	可以通过 `Thread#getState()` 获取线程状态：
	<table header-row="true" header-column="false">
<tr>
<td>状态</td>
<td>含义</td>
</tr>
<tr>
<td>NEW</td>
<td>已创建但未调用 `start()`</td>
</tr>
<tr>
<td>RUNNABLE</td>
<td>可运行状态，包含就绪和正在 CPU 上运行</td>
</tr>
<tr>
<td>BLOCKED</td>
<td>等待进入 `synchronized` 临界区，即等待 monitor 锁</td>
</tr>
<tr>
<td>WAITING</td>
<td>无限期等待其他线程唤醒，例如 `wait()`、`join()`、`LockSupport.park()`</td>
</tr>
<tr>
<td>TIMED_WAITING</td>
<td>限时等待，例如 `sleep(time)`、`wait(time)`、`join(time)`</td>
</tr>
<tr>
<td>TERMINATED</td>
<td>线程执行结束</td>
</tr>
	</table>
	注意：Java 的 `RUNNABLE` 不等于一定正在运行，也可能正在等待操作系统调度。
</details>
<details>
<summary>BLOCKED 和 WAITING 有什么区别</summary>
	<table header-row="true" header-column="false">
<tr>
<td>对比点</td>
<td>BLOCKED</td>
<td>WAITING</td>
</tr>
<tr>
<td>触发原因</td>
<td>获取 `synchronized` 的 monitor 锁失败</td>
<td>主动等待其他线程动作</td>
</tr>
<tr>
<td>典型方法</td>
<td>进入同步方法或同步代码块</td>
<td>`Object.wait()`、`Thread.join()`、`LockSupport.park()`</td>
</tr>
<tr>
<td>是否持有锁</td>
<td>正在等待锁，尚未获得目标 monitor</td>
<td>`wait()` 会释放 monitor，`park()` 不涉及 monitor</td>
</tr>
<tr>
<td>唤醒方式</td>
<td>持锁线程释放锁后重新竞争</td>
<td>`notify/notifyAll`、目标线程结束、`unpark`、中断等</td>
</tr>
	</table>
	简单记忆：`BLOCKED` 是抢锁抢不到；`WAITING` 是自己进入等待，需要其他条件触发。
</details>
<details>
<summary>如何优雅停止一个线程</summary>
	不要使用 `Thread.stop()`、`suspend()`、`resume()`。`stop()` 会强制终止线程并释放锁，可能破坏共享数据一致性；`suspend()` 容易导致死锁。
	常用方式：
	- `volatile` 标志位
	- `interrupt()`
	- `Future.cancel(true)`
	- 关闭资源
</details>
<details>
<summary>线程中断机制与 InterruptedException 是什么关系</summary>
	每个线程都有一个中断标志位，初始为 `false`。调用 `thread.interrupt()` 并不会强行杀死线程，而是发出“希望你停止”的协作信号。
	如果线程在 `sleep()`、`wait()`、`join()`、`Condition.await()` 等可中断阻塞方法中，会抛出 `InterruptedException`；否则只是把中断标志设为 `true`，需要线程自己检查并退出。
</details>
# 线程安全与内存模型
<details>
<summary>volatile 关键字有什么作用</summary>
	`volatile` 保证可见性，并通过内存屏障限制重排序；但不保证复合操作的原子性。
</details>
<details>
<summary>CAS 是什么，有什么缺点</summary>
	CAS 是 Compare And Swap。缺点包括 ABA 问题、自旋开销，以及天然只适合单变量原子更新。
</details>
<details>
<summary>sleep 和 wait 有什么区别</summary>
	- `sleep()` 属于 `Thread`，不释放锁。
	- `wait()` 属于 `Object`，必须在同步块中使用，会释放当前 monitor。
</details>
<details>
<summary>JUC 包下常用的类有哪些</summary>
	- 锁：`ReentrantLock`、`ReadWriteLock`、`StampedLock`
	- 原子类：`AtomicInteger`、`AtomicReference`、`LongAdder`
	- 并发集合：`ConcurrentHashMap`、`CopyOnWriteArrayList`、`BlockingQueue`
	- 同步工具：`CountDownLatch`、`CyclicBarrier`、`Semaphore`
	- 线程池与异步：`ThreadPoolExecutor`、`FutureTask`、`CompletableFuture`
</details>
<details>
<summary>CountDownLatch、CyclicBarrier、Semaphore 有什么区别</summary>
	- `CountDownLatch`：等待倒数到 0，不可复用。
	- `CyclicBarrier`：一组线程都到齐后再继续，可复用。
	- `Semaphore`：控制并发访问数量，可复用。
</details>
<details>
<summary>ThreadLocal 的作用、原理和内存泄漏问题</summary>
	`ThreadLocal` 为每个线程保存独立副本，底层是 `Thread -> ThreadLocalMap`。
	在线程池场景下，如果用完不 `remove()`，value 可能长期挂在线程上，导致内存泄漏。
</details>
# 锁机制
<details>
<summary>synchronized 的工作原理</summary>
	`synchronized` 是 JVM 内置 monitor 锁，通过 `monitorenter` / `monitorexit` 或 `ACC_SYNCHRONIZED` 实现，保证原子性、可见性和有序性。
</details>
<details>
<summary>synchronized 支持重入吗，如何实现</summary>
	支持可重入。monitor 会记录持有线程和重入次数，同一线程再次进入时计数加一，退出时减一，归零后真正释放。
</details>
<details>
<summary>synchronized 锁升级过程是什么</summary>
	常见理解是：无锁 -> 偏向锁 -> 轻量级锁 -> 重量级锁。现代 JDK 中偏向锁已废弃，更常见是无锁 -> 轻量级锁 -> 重量级锁。
</details>
<details>
<summary>ReentrantLock 的工作原理</summary>
	`ReentrantLock` 基于 AQS，通过 `state` 记录锁状态和重入次数，获取失败的线程进入 CLH 队列等待。
</details>
<details>
<summary>synchronized 和 ReentrantLock 有什么区别</summary>
	- `synchronized`：JVM 内置，自动释放锁。
	- `ReentrantLock`：JDK 显式锁，支持公平锁、可中断、超时获取、多个 Condition。
</details>
<details>
<summary>公平锁和非公平锁有什么区别</summary>
	公平锁按队列顺序获取；非公平锁允许插队。非公平锁吞吐量更高，但可能导致饥饿。
</details>
<details>
<summary>ReadWriteLock 适合什么场景</summary>
	适合读多写少场景。`ReentrantReadWriteLock` 支持读读共享、读写互斥、写写互斥。
</details>
# AQS
<details>
<summary>AQS 是什么</summary>
	AQS 是 `AbstractQueuedSynchronizer`，是 JUC 中锁和同步器的基础框架，核心是 `state` + FIFO 等待队列 + CAS。
</details>
# 线程池与异步编程
<details>
<summary>线程池的工作原理</summary>
	提交任务后的核心流程：
	1. 线程数小于 `corePoolSize`，创建核心线程。
	2. 核心线程满，任务进入队列。
	3. 队列满且线程数小于 `maximumPoolSize`，创建非核心线程。
	4. 再满就执行拒绝策略。
</details>
<details>
<summary>线程池有哪些核心参数</summary>
	- `corePoolSize`
	- `maximumPoolSize`
	- `keepAliveTime`
	- `workQueue`
	- `threadFactory`
	- `handler`
</details>
<details>
<summary>线程池有哪些拒绝策略</summary>
	- `AbortPolicy`
	- `CallerRunsPolicy`
	- `DiscardPolicy`
	- `DiscardOldestPolicy`
</details>
<details>
<summary>为什么不建议直接用 Executors</summary>
	因为很多工厂方法隐藏了无界队列或近乎无限线程数，生产中容易造成 OOM 或线程失控。更推荐手动创建 `ThreadPoolExecutor`。
</details>
<details>
<summary>Future、FutureTask 和 CompletableFuture 有什么区别</summary>
	- `Future`：异步结果接口。
	- `FutureTask`：同时实现 `Runnable` 和 `Future`。
	- `CompletableFuture`：支持链式编排、组合和异常处理。
</details>
# 并发场景题
<details>
<summary>什么情况下会产生死锁，如何避免</summary>
	死锁要同时满足互斥、持有并等待、不可剥夺、循环等待。常见避免手段是固定加锁顺序、减少嵌套锁、使用 `tryLock` 和缩小锁粒度。
</details>
<details>
<summary>如何设计一个生产者消费者模型</summary>
	优先使用 `BlockingQueue`。生产者 `put()`，消费者 `take()`，由队列负责线程安全和阻塞唤醒。
</details>
<details>
<summary>高并发计数器如何实现</summary>
	- 精确即时值：`AtomicLong`
	- 高并发热点计数：`LongAdder`
	- 强一致业务计数：数据库事务或版本号
</details>
