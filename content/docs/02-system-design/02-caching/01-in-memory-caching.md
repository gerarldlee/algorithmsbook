---
title: "In-Memory Caching"
weight: 1
toc: true
---

## What it is
In-memory caching stores frequently accessed data in RAM to serve reads at microsecond latency, avoiding disk or network round trips to the backing database. Redis and Memcached are the dominant open-source engines; both are key-value stores, but Redis adds rich data structures, persistence, and replication.

## How it works
A cache sits between the application and the database. Keys hash into slots and values live in main memory. Because memory is finite, the cache must evict entries when full; LRU (least-recently-used) drops the item that has gone longest without a read or write. LRU runs in O(1) per operation by keeping a doubly-linked list ordered by recency (front = most recent, back = least) plus a hash map from key to list node, so a `get` or `put` is a hash lookup plus a few pointer swaps.

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
use std::collections::HashMap;

struct Node {
    key: i32,
    value: i32,
    prev: Option<*mut Node>,
    next: Option<*mut Node>,
}

struct LRUCache {
    capacity: usize,
    map: HashMap<i32, *mut Node>,
    head: *mut Node,
    tail: *mut Node,
}

impl LRUCache {
    fn new(capacity: i32) -> Self {
        unsafe {
            let head = Box::into_raw(Box::new(Node { key: 0, value: 0, prev: None, next: None }));
            let tail = Box::into_raw(Box::new(Node { key: 0, value: 0, prev: None, next: None }));
            (*head).next = Some(tail);
            (*tail).prev = Some(head);
            LRUCache {
                capacity: capacity as usize,
                map: HashMap::new(),
                head,
                tail,
            }
        }
    }

    unsafe fn unlink(&mut self, node: *mut Node) {
        let p = (*node).prev.unwrap();
        let n = (*node).next.unwrap();
        (*p).next = Some(n);
        (*n).prev = Some(p);
    }

    unsafe fn push_front(&mut self, node: *mut Node) {
        let n = (*self.head).next.unwrap();
        (*node).next = Some(n);
        (*node).prev = Some(self.head);
        (*self.head).next = Some(node);
        (*n).prev = Some(node);
    }

    fn get(&mut self, key: i32) -> i32 {
        if let Some(&node) = self.map.get(&key) {
            unsafe {
                self.unlink(node);
                self.push_front(node);
                (*node).value
            }
        } else {
            -1
        }
    }

    fn put(&mut self, key: i32, value: i32) {
        if let Some(&node) = self.map.get(&key) {
            unsafe {
                (*node).value = value;
                self.unlink(node);
                self.push_front(node);
            }
            return;
        }
        let node = unsafe {
            let n = Box::into_raw(Box::new(Node { key, value, prev: None, next: None }));
            if self.map.len() == self.capacity {
                let last = (*self.tail).prev.unwrap();
                self.unlink(last);
                self.map.remove(&(*last).key);
            }
            self.push_front(n);
            n
        };
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
- **Latency**: reads drop from milliseconds (disk/network) to microseconds, but a cold-start miss still pays the full backend cost.
- **Volatility**: RAM is lost on restart; durability requires persistence (Redis RDB/AOF) at the cost of some write throughput.
- **Consistency**: cached values can go stale — TTLs and invalidation add complexity and a window of divergence from the source of truth.
- **Eviction**: LRU assumes uniform recency signals; skewed or scan-heavy workloads may thrash (see LFU in [Caching Patterns](02-caching-patterns.md)).
- **Operational cost**: RAM is expensive and capacity is bounded, so hot sets must fit; scaling is vertical (memory) before horizontal (sharding/cluster).

## When to use
- Hot read paths with a high read-to-write ratio — session stores, feature flags, leaderboards, and computed values.
- Storing counters or rate-limit state that must be read and incremented atomically at high throughput.
- Shielding a slow backing store (SQL database, external API) from repeated identical queries.

## Alternatives
- **Memcached** — simpler, multithreaded, string-only values; faster for flat cache workloads but no persistence or rich data structures.
- **Redis** — richer types, persistence, and replication; more features to operate but handles more use cases beyond a plain cache.
- **Database cache tables / disk cache** — larger capacity and durable, but much higher latency than RAM.

## Related
- [Caching Patterns](02-caching-patterns.md)
- [CDNs and Edge Computing](03-cdns-edge.md)
- [Rate Limiting](04-rate-limiting.md)
- [System Design Fundamentals](../01-system-design-fundamentals/01-fundamentals.md)
- [Bitwise Algorithms, Bitsets, and Bloom Filters](../../01-algorithms/01-linear-data-structures/05-bitwise-bloom-filters.md)
