# Java 集合

## 集合总览

## 数组和集合有什么区别？常用集合有哪些？

| 对比项 | 数组 | 集合 |
| --- | --- | --- |
| 长度 | 创建后固定 | 通常可以动态扩容 |
| 元素 | 可以保存基本类型和对象 | 只能保存对象，基本类型会自动装箱 |
| 能力 | 按下标访问简单高效 | 提供增删改查、遍历、排序、去重等 API |
| 适用场景 | 元素数量固定、结构简单 | 元素数量变化或需要丰富操作 |

常用集合：

- `ArrayList`：动态数组，随机访问快，尾部追加通常较快。
- `LinkedList`：双向链表，实现了 `List` 和 `Deque`，适合两端操作，不适合随机访问。
- `HashSet`：基于 `HashMap`，用于去重，不保证遍历顺序。
- `LinkedHashSet`：去重并保持插入顺序。
- `TreeSet`：基于红黑树，按自然顺序或比较器排序。
- `HashMap`：哈希表键值映射。
- `LinkedHashMap`：在 `HashMap` 上维护链表，可保持插入顺序或访问顺序。
- `TreeMap`：按 key 排序，适合范围查询。
- `PriorityQueue`：基于堆，保证队头是最高优先级元素，但遍历结果不等于完整排序结果。

## Collection 和 Collections 有什么区别？

- `Collection`：集合框架的根接口之一，`List`、`Set`、`Queue` 等接口继承它。
- `Collections`：`java.util` 下的工具类，提供排序、查找、同步包装、不可变包装等静态方法。
- `Map` 不继承 `Collection`，因为它表示 key-value 映射，而不是单值元素集合。

## 集合使用有哪些常见陷阱？

- `Arrays.asList(array)` 返回的是数组的定长视图：可以 `set()`，但不能 `add()`/`remove()`；需要可变列表时使用 `new ArrayList<>(Arrays.asList(array))`。
- 遍历时删除元素使用 `Iterator.remove()` 或 `removeIf()`，不要直接调用集合的 `remove()`；否则可能触发 `ConcurrentModificationException` 或跳过元素。
- 避免使用原始类型集合（如 `List list`），使用泛型让类型错误尽早暴露，并减少强制类型转换。

## 集合有哪些遍历方式？

- 普通 `for`：适合 `List` 按下标遍历。
- 增强 `for`：语法简洁，底层依赖迭代器。
- `Iterator`：可以通过 `iterator.remove()` 删除当前元素。
- `ListIterator`：支持双向遍历，以及 `set()` 修改、`add()` 添加。
- `forEach`：Java 8 的简洁遍历方式。
- Stream：适合过滤、映射、聚合等链式处理。

```java
Iterator<String> iterator = list.iterator();
while (iterator.hasNext()) {
    if ("a".equals(iterator.next())) {
        iterator.remove();
    }
}

map.forEach((key, value) ->
        System.out.println(key + ":" + value));
```

增强 `for` 中直接调用集合的 `add()` 或 `remove()` 做结构性修改，通常会触发 `ConcurrentModificationException`。需要删除时使用迭代器自己的 `remove()`。

## 什么是 fail-fast、弱一致迭代和快照迭代？

- 普通集合迭代器通常是 fail-fast：发现结构被非法修改时尽快抛出 `ConcurrentModificationException`，但它不是并发安全保证。
- 并发集合迭代器通常是弱一致的：允许并发修改，不保证一定看到所有最新数据。
- `CopyOnWriteArrayList` 的迭代器基于创建时的数组快照，不会看到之后的修改。

## List

## ArrayList、LinkedList、Vector 和 CopyOnWriteArrayList 有什么区别？

| 类型 | 底层结构 | 线程安全 | 适用场景 |
| --- | --- | --- | --- |
| `ArrayList` | 动态数组 | 否 | 查询多、尾部追加多 |
| `LinkedList` | 双向链表 | 否 | 两端插入删除、实现 `Deque` |
| `Vector` | 动态数组 | 是 | 早期遗留同步容器，不建议新代码使用 |
| `CopyOnWriteArrayList` | 写时复制数组 | 是 | 读多写少、数据量不大的并发场景 |

`ArrayList` 随机访问通常是 O(1)，中间插入和删除需要移动元素；`LinkedList` 按下标访问是 O(n)，只有已经定位到节点时插入删除才是 O(1)。需要队列或栈时通常优先考虑 `ArrayDeque`。

## ArrayList 如何扩容？

`ArrayList` 底层是 `Object[]`。现代 JDK 中无参构造通常先使用空数组，第一次添加元素时再分配默认容量；容量不足时创建更大的数组并复制旧元素，常见实现是扩容为原容量的约 1.5 倍。

扩容过程：

1. 添加前检查容量。
2. 计算新容量。
3. 创建新数组并复制旧元素。
4. 将内部数组引用切换到新数组。

扩容涉及数组复制。如果能预估元素数量，建议构造时指定初始容量。

## ArrayList 为什么不是线程安全的？

`add()` 涉及容量检查、数组写入和 size 更新，并不是一个原子操作。多个线程同时写入时可能出现元素覆盖、数据丢失和 size 不准确；并发扩容还可能导致更严重的数据问题。

普通并发读写不要直接共享 `ArrayList`，可根据场景选择：

- 临界区外部加锁。
- `Collections.synchronizedList()`。
- 读多写少使用 `CopyOnWriteArrayList`。
- 重新设计数据共享方式，避免不必要的共享可变状态。

## List 可以一边遍历一边修改吗？

- 修改元素值：普通下标遍历或 `ListIterator.set()` 都可以。
- 删除当前元素：使用 `Iterator.remove()`。
- 添加或双向修改：使用 `ListIterator.add()`、`set()`。
- 直接使用集合的 `add()`/`remove()`：增强 `for` 遍历时通常会触发 fail-fast。

## Map

## HashMap、LinkedHashMap、TreeMap 和 Hashtable 有什么区别？

| 类型 | 底层结构 | 顺序 | null 支持 | 线程安全 |
| --- | --- | --- | --- | --- |
| `HashMap` | 数组 + 链表/红黑树 | 不保证 | 支持一个 null key 和多个 null value | 否 |
| `LinkedHashMap` | HashMap + 双向链表 | 插入顺序或访问顺序 | 同 HashMap | 否 |
| `TreeMap` | 红黑树 | 按 key 排序 | 通常不支持 null key | 否 |
| `Hashtable` | 数组 + 链表 | 不保证 | 不支持 null key/value | 是，但锁粒度粗 |

`LinkedHashMap` 设置 `accessOrder = true` 后可以按访问顺序维护元素，结合 `removeEldestEntry()` 可实现简单 LRU。

## Map 有哪些遍历方式？

- 同时需要 key 和 value：优先使用 `entrySet()`。
- 只需要 key：使用 `keySet()`。
- 只需要 value：使用 `values()`。
- 需要遍历删除：使用 `Iterator<Map.Entry<K, V>>`。
- Java 8：简单逻辑可使用 `forEach()`，复杂转换可使用 Stream。

推荐写法：

```java
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    System.out.println(entry.getKey() + ":" + entry.getValue());
}
```

## HashMap 的实现原理和 put 过程是什么？

JDK 1.8 的 HashMap 底层是数组 + 链表 + 红黑树：

1. 对 key 的 `hashCode()` 做扰动计算。
2. 通过 `(n - 1) & hash` 定位桶下标。
3. 桶为空时直接放入节点。
4. 桶不为空时，先比较 key；相同则覆盖 value，不同则插入链表或红黑树。
5. 新增节点后更新 size，超过阈值时触发扩容。

当链表长度达到树化阈值且数组容量不小于 64 时，桶可能树化为红黑树；树化的目的，是避免极端哈希冲突时链表查询退化为 O(n)。树节点减少时可能退化回链表。

## HashMap 如何解决哈希冲突？

哈希冲突是不同 key 定位到了同一个桶。常见方案有链地址法、开放寻址法和再哈希法。

HashMap 使用链地址法：冲突节点放入同一桶的链表或红黑树，并通过扩容降低冲突概率。

## HashMap 为什么扩容？容量为什么是 2 的幂？

HashMap 默认负载因子通常为 `0.75`，当 `size` 超过 `capacity * loadFactor` 时扩容，容量通常变为原来的 2 倍。

容量使用 2 的幂主要有两个原因：

- 下标计算可以使用 `(n - 1) & hash`，代替取模。
- 扩容为 2 倍时，节点的新位置只可能是原索引或 `原索引 + oldCap`，通过 `(hash & oldCap)` 即可判断，无需重新完整计算。

JDK 1.8 扩容时会将节点拆分为低位链和高位链，再迁移到新表。

## 为什么 HashMap 使用红黑树，而不是 AVL 树？

AVL 树严格平衡，查询略快，但插入和删除时旋转调整更频繁。红黑树是弱平衡树，在查询、插入和删除之间取得更均衡的成本。

HashMap 桶内树化的目标不是提供完整排序，而是避免严重哈希冲突时链表退化，因此红黑树更适合这个场景。

## HashMap 是线程安全的吗？和 Hashtable 有什么区别？

HashMap 不是线程安全的。并发写入可能出现数据覆盖、数据丢失、size 不准确和扩容问题。JDK 1.7 的头插法扩容还可能形成环形链表，导致查询死循环；这是历史实现问题。

`Hashtable` 通过方法级 `synchronized` 保证线程安全，但锁住整个表，并且不支持 null key/value，现代并发场景通常使用 `ConcurrentHashMap`。

## TreeMap、TreeSet 如何判断顺序和重复？

它们使用自然排序或 `Comparator` 排序。对 `TreeSet` 来说，如果 `compareTo()` 或 `compare()` 返回 0，就会被视为重复元素，即使 `equals()` 不一定返回 true。因此比较器应与 equals 语义保持一致。

## Set

## HashSet、LinkedHashSet 和 TreeSet 有什么区别？

| 类型 | 底层结构 | 顺序 | 线程安全 | 核心特点 |
| --- | --- | --- | --- | --- |
| `HashSet` | 基于 `HashMap` | 不保证 | 否 | 去重，平均性能好 |
| `LinkedHashSet` | 哈希表 + 双向链表 | 插入顺序 | 否 | 去重并保持插入顺序 |
| `TreeSet` | 红黑树 | 排序顺序 | 否 | 按自然顺序或比较器排序 |

“有序”要区分：`TreeSet` 是排序有序，`LinkedHashSet` 是插入有序。

## 并发集合

## Java 中有哪些线程安全集合？

主要分为三类：

- 历史同步集合：`Vector`、`Stack`、`Hashtable`，通常使用方法级同步，锁粒度较粗。
- 同步包装器：`Collections.synchronizedList()`、`synchronizedMap()`，遍历时通常还要手动同步。
- 并发集合：`ConcurrentHashMap`、`CopyOnWriteArrayList`、`ConcurrentLinkedQueue`、`BlockingQueue` 等，是现代并发场景的主流选择。

## ConcurrentHashMap 如何保证线程安全？

JDK 1.7：

- 使用 `Segment[]` 分段锁，每个 Segment 管理一部分桶。
- `Segment` 继承 `ReentrantLock`，不同 Segment 可以并发写入。

JDK 1.8：

- 取消 Segment，底层为数组 + 链表 + 红黑树。
- 桶为空时使用 CAS 插入。
- 桶不为空时使用 `synchronized` 锁住桶头节点，再操作链表或红黑树。
- 扩容时允许多个线程协助迁移。

因此，CAS 负责低冲突场景的快速插入，`synchronized` 负责桶内冲突场景的互斥修改。`ConcurrentHashMap` 不允许 null key 和 null value。

## CopyOnWriteArrayList 适合什么场景？

写入时复制底层数组，读操作通常不加锁，写操作成本较高，适合读多写少且元素数量不大的场景，例如白名单和监听器列表。

它的迭代器基于快照，不会抛出普通集合那样的并发修改异常，但可能读不到迭代器创建之后的最新数据。

## ConcurrentSkipListMap 和 ConcurrentSkipListSet 适合什么场景？

- `ConcurrentSkipListMap`：基于跳表的线程安全有序 Map。
- `ConcurrentSkipListSet`：基于 `ConcurrentSkipListMap` 的线程安全有序 Set。

如果既需要并发安全又需要按 key 或元素排序，可以考虑它们；如果只需要高并发无序 Map，通常优先 `ConcurrentHashMap`。

## BlockingQueue 和其他并发队列有什么区别？

- `ConcurrentLinkedQueue`：基于 CAS 的非阻塞队列。
- `BlockingQueue`：支持阻塞入队和出队，适合生产者-消费者模型。
- `ArrayBlockingQueue`：数组实现，有界队列。
- `LinkedBlockingQueue`：链表实现，可有界也可近似无界。
- `ConcurrentLinkedDeque`：非阻塞并发双端队列。
- `LinkedBlockingDeque`：阻塞双端队列。

## Queue 与 Deque

## Queue、Deque、ArrayDeque 和 PriorityQueue 有什么区别？

- `Queue`：通常表示先进先出的队列。
- `Deque`：双端队列，支持从头尾两端插入和删除，也可以实现栈。
- `ArrayDeque`：基于循环数组，通常比 `LinkedList` 更适合作为栈或普通双端队列；不支持 null 元素。
- `PriorityQueue`：基于堆，队头是最小或最高优先级元素；它只保证队头顺序，遍历并不会得到完整排序结果。

需要阻塞语义时使用 `BlockingQueue`，需要排序语义时使用 `PriorityQueue` 或有序 Map/Set。
