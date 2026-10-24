# 16 Java 日志与可观测性

Java 应用通过日志门面记录事件，由具体实现负责级别、格式、缓冲与输出。一次请求穿过线程池、回调和消息后，还需要维持关联上下文；否则日志即使齐全，也可能无法说明哪些事件属于同一次工作。

## 日志门面、实现与桥接

SLF4J 提供统一 API，Logback 或适配后的 Log4j2 等实现负责实际输出。应用应检查 API、provider/binding 与桥接包的兼容关系，避免多个实现竞争，或两个相反方向的桥接形成循环。

门面降低业务代码对实现的耦合，并不自动统一依赖版本与配置。启动日志和实际依赖树应能解释最终采用了哪个实现；字段、采集与存储机制见[日志与可观测性](../Delivery/日志与可观测性.md)。

## 参数化日志延迟了什么

log.info("order created, orderId={}", orderId) 避免无条件拼接输出字符串，但 Java 仍会先求值参数表达式。因此 log.debug("value={}", expensive()) 即使 DEBUG 关闭，也可能执行 expensive；昂贵计算应先检查级别，或按所用 API 采用惰性参数方式。

记录异常时传递异常对象，保留原因链和受抑异常。业务边界决定由哪一层记录，避免同一个失败在每层重复输出；级别表达影响与处理责任，不能只看异常类名机械选择 ERROR。

## MDC 绑定上下文，不复制业务对象

常见 MDC 实现按线程保存关联字段。线程池复用意味着上一项任务的值可能遗留到下一项；把当前请求 ID 写入 ThreadLocal，也不会自动传给另一个线程，更不会把可变对象深拷贝。

传播分为两个时点：提交时捕获调用方上下文，执行时保存执行线程原上下文、安装捕获值，并在 finally 恢复。下面的辅助类使用 SLF4J API，需要工程已配置兼容的日志依赖；它处理日志上下文，不传播数据库事务或授权结果。

```java
import java.util.Map;
import org.slf4j.MDC;

public final class MdcTasks {
    private MdcTasks() {}

    public static Runnable wrap(Runnable task) {
        Map<String, String> captured = MDC.getCopyOfContextMap();
        return () -> {
            Map<String, String> previous = MDC.getCopyOfContextMap();
            try {
                install(captured);
                task.run();
            } finally {
                install(previous);
            }
        };
    }

    private static void install(Map<String, String> context) {
        if (context == null) MDC.clear();
        else MDC.setContextMap(context);
    }
}
```

提交方式为 executor.execute(MdcTasks.wrap(work))。恢复旧值而非一律清空，也能处理 CallerRunsPolicy 在调用线程执行任务的情况；捕获动作若放到工作线程才做，取到的就不是提交方上下文。方法语义见[SLF4J MDC API](https://www.slf4j.org/apidocs/org/slf4j/MDC.html)。

Trace/Span 还应通过所用观测库传播完整上下文，不能仅把一个 trace_id 写进日志就认为链路已经正确连接。HTTP、RPC、消息和响应式执行边界各自需要相应传播机制。

## 输出失败与业务事实

普通诊断日志可以按明确策略降级，异步缓冲满时也需决定丢弃还是阻塞，并观察丢失量。落盘与采集各有容量、轮转和保留边界，单靠异步输出不能承诺事件已持久化。

业务或安全审计若要求可靠保存，应使用满足该承诺的记录机制，例如与业务事实同事务保存的审计表或待投递记录；不能把可丢弃的诊断日志当成唯一凭据。日志记录内容与关联字段也要遵循数据分类和脱敏规则。
