# Java集合

# 概念
<details>
<summary>数组与集合有什么区别？常用集合有哪些？</summary>
	数组和集合的核心区别：
	- 长度：数组长度固定，创建后不能改变；集合长度动态，可按需扩容或缩容。
	- 元素类型：数组可以存基本类型和对象；集合只能存对象，基本类型会自动装箱。
	- 操作能力：数组适合按下标快速访问；集合提供了更丰富的增删改查、遍历、排序、去重等 API。
	- 使用场景：元素数量固定、追求极致简单访问时用数组；元素数量变化、需要复杂操作时用集合。
	常用集合类：
	- `ArrayList`：基于动态数组，查询快，尾部追加快，中间插入和删除需要移动元素。
	- `LinkedList`：基于双向链表，适合头尾插入、删除，也可实现队列或栈。
	- `HashSet`：基于 `HashMap` 实现，用于元素去重，不保证顺序。
	- `LinkedHashSet`：基于哈希表和双向链表，既去重又保持插入顺序。
	- `TreeSet`：基于红黑树，元素按自然顺序或比较器排序。
	- `HashMap`：基于哈希表存储键值对，通过 key 快速查找 value。
	- `LinkedHashMap`：在 `HashMap` 基础上维护双向链表，可保持插入顺序或访问顺序，常用于 LRU。
	- `TreeMap`：基于红黑树，按 key 排序。
	- `PriorityQueue`：优先队列，按自然顺序或比较器维护堆序。
</details>
<details>
<summary>Collection 和 Collections 有什么区别？</summary>
	- `Collection` 是集合框架的根接口之一，表示一组对象的容器，常见子接口有 `List`、`Set`、`Queue`。
	- `Collections` 是 `java.util` 包下的工具类，提供大量静态方法
</details>
<details>
<summary>集合有哪些遍历方式？</summary>
	常见遍历方式：
	- 普通 `for` 循环：适合 `List` 按下标遍历。
	- 增强 `for` 循环：写法简洁，底层依赖迭代器，不适合在遍历时直接结构性修改集合。
	- `Iterator`：适合遍历时删除元素，只能使用迭代器自己的 `remove()` 删除。
	- `ListIterator`：`Iterator` 的子接口，支持双向遍历，也支持在遍历过程中通过 `set()` 修改元素、通过 `add()` 添加元素。
	- `forEach`：Java 8 引入，适合简单遍历。
	- `Stream API`：适合过滤、映射、聚合等函数式操作。
	示例：
	```java
Iterator<String> iterator = list.iterator();
while (iterator.hasNext()) {
    String element = iterator.next();
    if ("a".equals(element)) {
        iterator.remove();
    }
}
	```
	```java
ListIterator<String> iterator = list.listIterator();
while (iterator.hasNext()) {
    String element = iterator.next();
    if ("a".equals(element)) {
        iterator.set("b");
    }
}
	```
	```java
map.forEach((key, value) -> System.out.println(key + ":" + value));
	```
</details>
<details>
<summary>Java 中有哪些线程安全集合？</summary>
	Java 线程安全集合主要分三类：
	- 历史遗留同步集合：`Vector`、`Stack`、`Hashtable`。这些类大多通过 `synchronized` 修饰方法实现线程安全，锁粒度粗，性能较差，现代开发一般不优先使用。
	- `Collections.synchronizedXXX` 包装器：例如 `Collections.synchronizedList(list)`、`Collections.synchronizedMap(map)`。本质是在外层加同步包装，锁粒度也偏粗，遍历时通常还需要手动同步。
	- `java.util.concurrent` 并发集合：例如 `ConcurrentHashMap`、`CopyOnWriteArrayList`、`ConcurrentLinkedQueue`、`BlockingQueue`，是并发场景的主流选择。
	常见并发集合：
	- `ConcurrentHashMap`：线程安全的高并发 Map。JDK 1.7 使用 `Segment` 分段锁；JDK 1.8 使用数组 + 链表 + 红黑树，并结合 CAS 和 `synchronized` 锁桶头节点。
	- `ConcurrentSkipListMap`：基于跳表的线程安全有序 Map，支持按 key 排序。
	- `ConcurrentSkipListSet`：基于 `ConcurrentSkipListMap` 的线程安全有序 Set。
	- `CopyOnWriteArrayList`：写时复制，读不加锁，适合读多写少场景，如白名单、监听器列表。
	- `CopyOnWriteArraySet`：基于 `CopyOnWriteArrayList` 实现的线程安全 Set，适合读多写少且元素数量不大的场景。
	- `ConcurrentLinkedQueue`：基于 CAS 的非阻塞并发队列。
	- `BlockingQueue`：阻塞队列，适合生产者消费者模型，例如 `ArrayBlockingQueue`、`LinkedBlockingQueue`。
	- `ConcurrentLinkedDeque`：基于链表的非阻塞并发双端队列。
	- `LinkedBlockingDeque`：基于链表的阻塞双端队列。
	补充：`Vector` 默认扩容为原容量的 2 倍，`ArrayList` 默认扩容为原容量的 1.5 倍。
</details>

# List

<table header-row="true" header-column="false">
<tr>
<td>集合类型</td>
<td>底层实现</td>
<td>线程安全</td>
<td>时间复杂度</td>
<td>核心特点与适用场景</td>
</tr>
<tr>
<td>`ArrayList`</td>
<td>动态数组，默认扩容 1.5 倍</td>
<td>否</td>
<td>随机访问 O(1)，中间增删 O(n)</td>
<td>查询多、增删少时优先使用</td>
</tr>
<tr>
<td>`LinkedList`</td>
<td>双向链表</td>
<td>否</td>
<td>按下标访问 O(n)，已定位节点后增删 O(1)</td>
<td>适合头尾操作、队列、栈；不适合频繁随机访问</td>
</tr>
<tr>
<td>`Vector`</td>
<td>动态数组，默认扩容 2 倍</td>
<td>是</td>
<td>随机访问 O(1)，中间增删 O(n)</td>
<td>早期同步容器，现代开发较少使用</td>
</tr>
<tr>
<td>`CopyOnWriteArrayList`</td>
<td>写时复制数组</td>
<td>是</td>
<td>读 O(1)，写 O(n)</td>
<td>适合读多写极少的并发场景</td>
</tr>
</table>
<details>
<summary>ArrayList 的扩容机制是什么？</summary>
	`ArrayList` 底层是 `Object[]` 数组。无参构造时，初始数组是空数组，第一次添加元素时扩容到默认容量 10；之后容量不够时，通常扩容为原容量的 1.5 倍。
	扩容过程：
	1. 添加元素前检查容量是否足够。
	2. 如果容量不足，计算新容量，通常是 `oldCapacity + oldCapacity >> 1`。
	3. 创建新数组。
	4. 使用 `Arrays.copyOf` 将旧数组元素复制到新数组。
	5. 将内部数组引用指向新数组。
	扩容涉及数组复制，成本较高。如果能预估元素数量，建议在构造时指定初始容量，减少扩容次数。
</details>
<details>
<summary>ArrayList 为什么线程不安全？具体哪里不安全？</summary>
	`ArrayList` 的线程不安全主要体现在 `add()` 不是原子操作，内部涉及容量检查、数组赋值、`size++` 等多个步骤。
	ArrayList 添加元素时，先检查底层数组容量够不够；够就放到 `elementData[size]`，然后 `size++`
	典型问题：
	- 元素覆盖：两个线程同时读取到相同的 `size`，都往同一个下标写入，后写入的元素覆盖先写入的元素。
	- `size` 不准确：`size++` 不是原子操作，多个线程并发更新可能丢失计数。
	- 数组越界：一个线程判断容量足够后还没写入，另一个线程完成写入并修改 `size`，前一个线程继续使用过期状态写入，可能触发越界。
	- 读到 `null`：并发写入和扩容交错时，可能出现数组内容与 `size` 状态不一致。
	所以多线程写 `ArrayList` 需要额外同步，或改用并发容器。
</details>
<details>
<summary>如何把 ArrayList 变成线程安全？</summary>
	常见方式：
	- 使用 `Collections.synchronizedList(new ArrayList<>())` 包装。
	- 使用 `CopyOnWriteArrayList`，适合读多写少。
	- 使用 `Vector`
	- 在业务代码中对访问 `ArrayList` 的临界区加锁。
	选择建议：普通并发读写优先考虑外部加锁或重新设计并发模型；读多写极少优先考虑 `CopyOnWriteArrayList`。
</details>
<details>
<summary>List 可以一边遍历一边修改吗？</summary>
	- 普通 `for` 循环：可以通过下标修改元素值，也可以谨慎删除元素，但删除时要处理索引变化。
	- 增强 `for` 循环：不要直接调用集合的 `add()`、`remove()` 做结构性修改，否则容易触发 `ConcurrentModificationException`。
	- `Iterator`：遍历时可以用 `iterator.remove()` 删除当前元素，不能用集合自己的 `remove()` 删除。
	- `ListIterator`：可以用 `set()` 修改当前元素，用 `add()` 添加元素，也可以双向遍历。
	- `CopyOnWriteArrayList`：遍历时允许其他线程修改，不会抛出 `ConcurrentModificationException`，但迭代器看到的是创建迭代器时的快照，可能读不到最新数据。
	示例：
	```java
ListIterator<Integer> iterator = list.listIterator();
while (iterator.hasNext()) {
    Integer value = iterator.next();
    if (value == 1) {
        iterator.set(100);
    }
}
	```
</details>

# Map

<table header-row="true" header-column="false">
<tr>
<td>集合类型</td>
<td>底层数据结构</td>
<td>线程安全</td>
<td>顺序性</td>
<td>核心特点与适用场景</td>
</tr>
<tr>
<td>`HashMap`</td>
<td>JDK 1.8：数组 + 链表 + 红黑树</td>
<td>否</td>
<td>无序</td>
<td>最常用 Map，查询性能好，多线程写不安全</td>
</tr>
<tr>
<td>`LinkedHashMap`</td>
<td>`HashMap` + 双向链表</td>
<td>否</td>
<td>插入顺序或访问顺序</td>
<td>可用于保持顺序、实现 LRU</td>
</tr>
<tr>
<td>`TreeMap`</td>
<td>红黑树</td>
<td>否</td>
<td>按 key 排序</td>
<td>适合需要按 key 排序或范围查询的场景</td>
</tr>
<tr>
<td>`Hashtable`</td>
<td>数组 + 链表</td>
<td>是</td>
<td>无序</td>
<td>早期同步 Map，不支持 null key/value，基本被淘汰</td>
</tr>
<tr>
<td>`ConcurrentHashMap`</td>
<td>JDK 1.8：数组 + 链表 + 红黑树 + CAS + synchronized</td>
<td>是</td>
<td>无序</td>
<td>高并发场景首选 Map</td>
</tr>
</table>
<details>
<summary>Map 有哪些遍历方式？哪种更推荐？</summary>
	常见方式：
	- `entrySet()`：同时需要 key 和 value 时推荐
	- `keySet()`：只需要 key 时使用
	- `values()`：只需要 value 时使用。
	- 迭代器：需要遍历时删除元素可使用 `Iterator`。
	- `forEach()`：Java 8 写法简洁。
	- `Stream API`：适合过滤、映射、收集等复杂操作。
	推荐写法：
	```java
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    System.out.println(entry.getKey() + ":" + entry.getValue());
}
	```
	Java 8 写法：
	```java
map.forEach((key, value) -> System.out.println(key + ":" + value));
	```
</details>
<details>
<summary>HashMap 的实现原理是什么</summary>
	- JDK 1.8 之前：底层是数组 + 链表。
	- JDK 1.8 开始：底层是数组 + 链表 + 红黑树。
	核心流程：
	1. 对 key 的 `hashCode()` 做扰动计算，得到 hash 值。
	2. 通过 `(n - 1) & hash` 定位数组下标，`n` 是数组长度。
	3. 如果桶为空，直接放入节点。
	4. 如果桶不为空，说明发生哈希冲突：
	- key 相同则覆盖 value。
	- key 不同则挂到链表或红黑树中。
	1. 当链表长度达到 8，且数组长度至少为 64 时，链表会树化为红黑树。
	2. 当红黑树节点数减少到 6 左右时，可能退化回链表。
	红黑树用于降低极端哈希冲突下的查询复杂度：链表查询是 O(n)，红黑树查询是 O(log n)。
</details>
<details>
<summary>HashMap 的 put 过程是什么？</summary>
	`HashMap.put(key, value)` 的核心过程：
	1. 如果数组 `table` 为空，先调用 `resize()` 初始化。无参构造下默认容量是 16；如果构造时指定了初始容量，会调整为大于等于该值的最小 2 的幂。
	2. 计算 key 的 hash 值，并通过 `(n - 1) & hash` 定位桶下标。
	3. 如果桶为空，直接创建新节点放入。
	4. 如果桶不为空，先判断桶头节点 key 是否相同，相同则覆盖 value。
	5. 如果桶头是红黑树节点，则按红黑树逻辑插入或覆盖。
	6. 如果桶头是链表节点，则遍历链表：
	- 找到相同 key，覆盖 value。
	- 没找到相同 key，尾插新节点。
	- 插入后如果链表长度达到树化阈值，尝试树化。
	1. 插入新节点后 `size++`，如果 `size > threshold`，触发扩容。
	补充：JDK 1.7 链表插入使用头插法，JDK 1.8 改为尾插法。
</details>
<details>
<summary>HashMap 如何解决哈希冲突？</summary>
	哈希冲突是指不同 key 计算出的数组下标相同。
	常见解决方法：
	- 链地址法：冲突元素放到同一个桶的链表或树中，`HashMap` 使用这种方式。
	- 开放寻址法：冲突后继续探测下一个可用位置，例如线性探测、二次探测。
	- 再哈希法：使用另一个哈希函数重新计算位置。
	- 扩容：增加桶数量，降低冲突概率。
	`HashMap` 的做法是链地址法 + 扩容 + JDK 1.8 红黑树优化。
</details>
<details>
<summary>HashMap 的扩容机制是什么？</summary>
	`HashMap` 的默认负载因子是 0.75，阈值 `threshold = capacity * loadFactor`。当元素数量超过阈值时触发扩容，容量通常变为原来的 2 倍。
	JDK 1.8 的扩容优化：
	- 因为容量始终是 2 的幂，扩容后新容量是旧容量的 2 倍。
	- 节点迁移时不需要重新完整计算 hash。
	- 只需要判断 `(hash & oldCap)`：
	- 结果为 0，节点留在原索引。
	- 结果不为 0，节点移动到 `原索引 + oldCap`。
	这样既减少了重新计算成本，也能把原来同一个桶中的节点分散到新桶中。
	注意：`resize()` 本身不是线程安全的。多线程并发扩容是 `HashMap` 出现死循环、数据丢失等问题的重要原因之一。
</details>
<details>
<summary>HashMap 的容量为什么必须是 2 的幂？</summary>
	主要原因有两个：
	- 计算下标更高效：当容量 `n` 是 2 的幂时，`hash % n` 可以优化为 `(n - 1) & hash`，位运算比取模更快。
	- 扩容迁移更高效：扩容为 2 倍后，元素的新位置只可能是原位置或 `原位置 + oldCap`，通过 `(hash & oldCap)` 即可判断。
	这也是 `HashMap` 构造时会把用户传入的初始容量调整为 2 的幂的原因。
</details>
