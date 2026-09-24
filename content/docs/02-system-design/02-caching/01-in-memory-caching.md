---
title: "In-Memory Caching Engines (Redis, Memcached) & Eviction Policies (LRU, LFU, ARC)"
weight: 1
toc: true
---

## What it is
An in-memory caching engine stores hot data in RAM so an application can avoid a database, object-store, or network lookup. Redis adds data structures, persistence, replication, and atomic operations to its key-value core; Memcached provides a smaller, multithreaded cache for opaque values. When memory fills, an eviction policy such as **least recently used (LRU)**, **least frequently used (LFU)**, or **adaptive replacement cache (ARC)** decides which entries remain.

## How it works
An engine binds the storage policy to an explicit memory ceiling, as this launch configuration does for Redis and Memcached:

```yaml
engines:
  redis:
    command: redis-server redis.conf --maxmemory 4gb --maxmemory-policy allkeys-lfu
  memcached:
    command: memcached -m 4096
```

Redis accepts strings, hashes, lists, sets, sorted sets, and streams, so one service can serve caches, counters, locks, and queues. Memcached stores opaque key-value objects and is suitable for simple page, session, and query-result caches. Both keep a key index in memory; when Redis reaches `maxmemory`, its selected policy evicts keys, while Memcached evicts least-recently-used items within reclaimable memory.

Redis's `allkeys-lfu` policy uses an approximate frequency counter rather than an exact LFU implementation. The **LRU** policy instead uses recency. The **LRU** implementation below keeps a hash table from keys to nodes and a doubly-linked list ordered from most to least recently used; a hit moves its node to the front, and insertion beyond capacity removes the back. Both operations take expected O(1) time. LFU retains a per-key count, and ARC balances recent and frequent entries while keeping a bounded list of keys evicted recently from either partition. Google Caffeine implements ARC; Redis and Memcached do not expose ARC as a native policy.

```java
import java.util.HashMap;
import java.util.Map;

class LRUCache {
    static class Node {
        int key, value;
        Node prev, next;
        Node(int k, int v) { key = k; value = v; }
    }

    private final int capacity;
    private final Map<Integer, Node> map = new HashMap<>();
    private final Node head = new Node(0, 0), tail = new Node(0, 0);

    LRUCache(int capacity) {
        if (capacity <= 0) throw new IllegalArgumentException("capacity must be positive");
        this.capacity = capacity;
        head.next = tail;
        tail.prev = head;
    }

    public int get(int key) {
        Node n = map.get(key);
        if (n == null) return -1;
        remove(n);
        addFirst(n);
        return n.value;
    }

    public void put(int key, int value) {
        Node n = map.get(key);
        if (n != null) {
            n.value = value;
            remove(n);
            addFirst(n);
            return;
        }
        n = new Node(key, value);
        if (map.size() == capacity) {
            map.remove(tail.prev.key);
            remove(tail.prev);
        }
        map.put(key, n);
        addFirst(n);
    }

    private void remove(Node n) {
        n.prev.next = n.next;
        n.next.prev = n.prev;
    }

    private void addFirst(Node n) {
        n.next = head.next;
        n.prev = head;
        head.next.prev = n;
        head.next = n;
    }
}
```

```c
#include <stdlib.h>

typedef struct Node {
    int key, value;
    struct Node *prev, *next;   /* LRU list */
    struct Node *hnext;         /* hash chain */
} Node;

typedef struct {
    int capacity, size;
    Node *head, *tail;          /* LRU list sentinels */
    Node **buckets;
    int nbuckets;
} LRUCache;

static unsigned hash(int key, int n) {
    return (unsigned)(key * 2654435761u) % (unsigned)n;
}

LRUCache *lru_cache_create(int capacity) {
    if (capacity <= 0) return NULL;
    LRUCache *c = calloc(1, sizeof(*c));
    c->capacity = capacity;
    c->nbuckets = capacity * 2 + 1;
    c->buckets = calloc((size_t)c->nbuckets, sizeof(Node *));
    c->head = calloc(1, sizeof(Node));
    c->tail = calloc(1, sizeof(Node));
    c->head->next = c->tail;
    c->tail->prev = c->head;
    return c;
}

static void unlink_node(Node *n) {
    n->prev->next = n->next;
    n->next->prev = n->prev;
}

static void push_front(LRUCache *c, Node *n) {
    n->next = c->head->next;
    n->prev = c->head;
    c->head->next->prev = n;
    c->head->next = n;
}

static Node **find_bucket(LRUCache *c, int key) {
    Node **p = &c->buckets[hash(key, c->nbuckets)];
    while (*p && (*p)->key != key) p = &(*p)->hnext;
    return p;
}

int lru_cache_get(LRUCache *c, int key) {
    Node **p = find_bucket(c, key);
    if (!*p) return -1;
    unlink_node(*p);
    push_front(c, *p);
    return (*p)->value;
}

void lru_cache_put(LRUCache *c, int key, int value) {
    Node **p = find_bucket(c, key);
    if (*p) {
        (*p)->value = value;
        unlink_node(*p);
        push_front(c, *p);
        return;
    }
    Node *n = calloc(1, sizeof(Node));
    n->key = key;
    n->value = value;
    n->hnext = c->buckets[hash(key, c->nbuckets)];
    c->buckets[hash(key, c->nbuckets)] = n;
    push_front(c, n);
    c->size++;
    if (c->size > c->capacity) {
        Node *last = c->tail->prev;
        unlink_node(last);
        Node **q = find_bucket(c, last->key);
        *q = last->hnext;
        free(last);
        c->size--;
    }
}

void lru_cache_free(LRUCache *c) {
    Node *n = c->head;
    while (n) {
        Node *nx = n->next;
        free(n);
        n = nx;
    }
    free(c->buckets);
    free(c);
}
```

```python
class LRUCache:
    class _Node:
        __slots__ = ("key", "value", "prev", "next")

        def __init__(self, key=0, value=0):
            self.key = key
            self.value = value
            self.prev = None
            self.next = None

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self.map = {}
        self.head = self._Node()
        self.tail = self._Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _unlink(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _push_front(self, node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        node = self.map.get(key)
        if node is None:
            return -1
        self._unlink(node)
        self._push_front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        node = self.map.get(key)
        if node is not None:
            node.value = value
            self._unlink(node)
            self._push_front(node)
            return
        node = self._Node(key, value)
        if len(self.map) == self.capacity:
            last = self.tail.prev
            self._unlink(last)
            del self.map[last.key]
        self.map[key] = node
        self._push_front(node)
```

```rust
use std::cell::RefCell;
use std::collections::HashMap;
use std::rc::{Rc, Weak};

type Node = RefCell<NodeData>;

struct NodeData {
    key: i32,
    value: i32,
    prev: Weak<Node>,
    next: Weak<Node>,
}

struct LRUCache {
    capacity: usize,
    map: HashMap<i32, Node>,
    head: Node,
    tail: Node,
}

impl LRUCache {
    fn new(capacity: i32) -> Self {
        assert!(capacity > 0);
        let head = Rc::new(RefCell::new(NodeData {
            key: 0,
            value: 0,
            prev: Weak::new(),
            next: Weak::new(),
        }));
        let tail = Rc::new(RefCell::new(NodeData {
            key: 0,
            value: 0,
            prev: Weak::new(),
            next: Weak::new(),
        }));
        head.borrow_mut().next = Some(tail.clone());
        tail.borrow_mut().prev = Some(head.clone());
        LRUCache {
            capacity: capacity as usize,
            map: HashMap::new(),
            head,
            tail,
        }
    }

    fn unlink(&self, node: &Node) {
        let prev = node.borrow().prev.upgrade();
        let next = node.borrow().next.upgrade();
        if let Some(prev_node) = &prev {
            prev_node.borrow_mut().next = next.clone();
        }
        if let Some(next_node) = &next {
            next_node.borrow_mut().prev = prev.clone();
        }
        let mut data = node.borrow_mut();
        data.prev = Weak::new();
        data.next = Weak::new();
    }

    fn push_front(&self, node: &Node) {
        let first = self.head.borrow().next.upgrade();
        let mut data = node.borrow_mut();
        data.prev = Rc::downgrade(&self.head);
        data.next = first.clone();
        self.head.borrow_mut().next = Some(node.clone());
        if let Some(first_node) = first {
            first_node.borrow_mut().prev = Some(node.clone());
        }
    }

    fn get(&mut self, key: i32) -> i32 {
        let Some(node) = self.map.get(&key).cloned() else {
            return -1;
        };
        self.unlink(&node);
        self.push_front(&node);
        node.borrow().value
    }

    fn put(&mut self, key: i32, value: i32) {
        if let Some(node) = self.map.get(&key).cloned() {
            node.borrow_mut().value = value;
            self.unlink(&node);
            self.push_front(&node);
            return;
        }
        if self.map.len() == self.capacity {
            let last = self.tail.borrow().prev.upgrade().unwrap();
            let last_key = last.borrow().key;
            self.unlink(&last);
            self.map.remove(&last_key);
        }
        let node = Rc::new(RefCell::new(NodeData {
            key,
            value,
            prev: Weak::new(),
            next: Weak::new(),
        }));
        self.push_front(&node);
        self.map.insert(key, node);
    }
}
```

```typescript
class Node {
    key: number;
    value: number;
    prev: Node | null = null;
    next: Node | null = null;
    constructor(key = 0, value = 0) {
        this.key = key;
        this.value = value;
    }
}

class LRUCache {
    private capacity: number;
    private map = new Map<number, Node>();
    private head = new Node();
    private tail = new Node();

    constructor(capacity: number) {
        if (capacity <= 0) throw new Error("capacity must be positive");
        this.capacity = capacity;
        this.head.next = this.tail;
        this.tail.prev = this.head;
    }

    private unlink(node: Node): void {
        node.prev!.next = node.next;
        node.next!.prev = node.prev;
    }

    private pushFront(node: Node): void {
        node.next = this.head.next;
        node.prev = this.head;
        this.head.next!.prev = node;
        this.head.next = node;
    }

    get(key: number): number {
        const node = this.map.get(key);
        if (!node) return -1;
        this.unlink(node);
        this.pushFront(node);
        return node.value;
    }

    put(key: number, value: number): void {
        const node = this.map.get(key);
        if (node) {
            node.value = value;
            this.unlink(node);
            this.pushFront(node);
            return;
        }
        const created = new Node(key, value);
        if (this.map.size === this.capacity) {
            const last = this.tail.prev!;
            this.unlink(last);
            this.map.delete(last.key);
        }
        this.map.set(key, created);
        this.pushFront(created);
    }
}
```

```go
package lru

type node struct {
	key, value  int
	prev, next *node
}

type LRUCache struct {
	capacity int
	m        map[int]*node
	head     *node
	tail     *node
}

func NewLRUCache(capacity int) *LRUCache {
	if capacity <= 0 {
		panic("capacity must be positive")
	}
	head := &node{}
	tail := &node{}
	head.next = tail
	tail.prev = head
	return &LRUCache{capacity: capacity, m: make(map[int]*node), head: head, tail: tail}
}

func (c *LRUCache) unlink(n *node) {
	n.prev.next = n.next
	n.next.prev = n.prev
}

func (c *LRUCache) pushFront(n *node) {
	n.next = c.head.next
	n.prev = c.head
	c.head.next.prev = n
	c.head.next = n
}

func (c *LRUCache) Get(key int) int {
	n, ok := c.m[key]
	if !ok {
		return -1
	}
	c.unlink(n)
	c.pushFront(n)
	return n.value
}

func (c *LRUCache) Put(key, value int) {
	if n, ok := c.m[key]; ok {
		n.value = value
		c.unlink(n)
		c.pushFront(n)
		return
	}
	n := &node{key: key, value: value}
	if len(c.m) == c.capacity {
		last := c.tail.prev
		c.unlink(last)
		delete(c.m, last.key)
	}
	c.m[key] = n
	c.pushFront(n)
}
```

## Tradeoffs

| Engine or policy | Wins when | Costs or limits |
| --- | --- | --- |
| Redis | You need structured values, atomic commands, persistence, or replication. | A multi-purpose service requires capacity planning, access control, and monitoring for cache and non-cache data. |
| Memcached | You need a simple network cache for opaque objects. | Values have no built-in server-side structure, persistence, or replication. |
| LRU | Access recency predicts future use. | A one-off scan can evict repeatedly used items. |
| LFU | A small set of keys dominates reads. | Old winners can retain capacity, while approximate counters need periodic decay. |
| ARC | The working set shifts between recency and frequency. | More per-entry metadata and adaptation work than LRU or LFU. |

Cached values can remain stale until a write invalidates them or their TTL expires. Persistence does not make the cache the source of truth: readers must still handle misses, eviction, and a Redis or Memcached outage.

## When to use
- You need repeated reads of the same hot data to avoid a slower backing store.
- You need atomic counters, rate-limit state, or coordination with a short failure domain.
- You can define which source of truth repairs a miss and which events invalidate an entry.
- The working set fits a bounded memory budget and its staleness window is acceptable.

## Alternatives
- **In-process cache** — removes the network hop but duplicates state across application instances and needs invalidation broadcasts.
- **Content delivery network cache** — fits repeated public HTTP responses but cannot safely cache private or per-user state.
- **Backing-store reads** — provide fresh, authoritative data at the cost of database load and higher latency.

## Related
- [Application Caching Patterns: Cache-Aside, Write-Through, Write-Around, Write-Behind](02-caching-patterns.md)
- [Content Delivery Networks (CDNs), Edge Computing, and Static/Dynamic Content Acceleration](03-cdns-edge.md)
- [Rate Limiting & Traffic Shaping: Token Bucket, Leaky Bucket, Sliding Window Log, and Counter](04-rate-limiting.md)
- [Fundamentals of System Design: Latency, Throughput, Availability, and SLA/SLO/SLI](../01-system-design-fundamentals/01-fundamentals.md)
- [Queues vs Streams](../../03-messaging/01-messaging/01-queues-vs-streams.md)
