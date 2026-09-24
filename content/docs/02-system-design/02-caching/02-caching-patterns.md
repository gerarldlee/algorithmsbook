---
title: "Caching Patterns"
weight: 2
toc: true
---

## What it is
Caching patterns are read/write strategies that coordinate an application, its cache, and the backing database: cache-aside (lazy loading), read-through, write-through, and write-back/write-behind. They trade off freshness, latency, and write amplification, and are usually paired with TTLs and a frequency-aware eviction policy such as LFU (least-frequently-used).

## How it works
In cache-aside, the application checks the cache on read, loads from the database on miss, and writes through to both cache and DB (write-through) or defers the DB write (write-back). TTLs bound staleness, while a long TTL on a popular key risks a stampede when it expires and many callers rebuild it simultaneously. LFU eviction removes the least frequently accessed items: a hash map tracks each key's value and frequency, and a second map groups keys by frequency in insertion order, so an eviction removes the oldest key in the lowest frequency bucket in O(1).

```java
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.Map;

class LFUCache {
    private final int capacity;
    private int minFreq = 0;
    private final Map<Integer, int[]> cache = new HashMap<>();            // key -> {value, freq}
    private final Map<Integer, LinkedHashSet<Integer>> freq = new HashMap<>(); // freq -> ordered keys

    LFUCache(int capacity) {
        this.capacity = capacity;
    }

    public int get(int key) {
        int[] e = cache.get(key);
        if (e == null) return -1;
        bump(key, e);
        return e[0];
    }

    public void put(int key, int value) {
        if (capacity == 0) return;
        int[] e = cache.get(key);
        if (e != null) {
            e[0] = value;
            bump(key, e);
            return;
        }
        if (cache.size() == capacity) {
            LinkedHashSet<Integer> keys = freq.get(minFreq);
            int evict = keys.iterator().next();
            keys.remove(evict);
            if (keys.isEmpty()) freq.remove(minFreq);
            cache.remove(evict);
        }
        cache.put(key, new int[]{value, 1});
        freq.computeIfAbsent(1, k -> new LinkedHashSet<>()).add(key);
        minFreq = 1;
    }

    private void bump(int key, int[] e) {
        int f = e[1]++;
        LinkedHashSet<Integer> keys = freq.get(f);
        keys.remove(key);
        if (keys.isEmpty()) {
            freq.remove(f);
            if (minFreq == f) minFreq++;
        }
        freq.computeIfAbsent(f + 1, k -> new LinkedHashSet<>()).add(key);
    }
}
```

```c
#include <stdlib.h>

typedef struct Entry {
    int key, value, freq;
    struct Entry *prev, *next;   /* within its frequency bucket */
    struct Entry *hnext;         /* hash chain */
} Entry;

typedef struct {
    int capacity, size, min_freq;
    int nbuckets;
    Entry **buckets;
    Entry **freq_head;
    Entry **freq_tail;
    int nfreq;
} LFUCache;

static unsigned hash(int key, int n) {
    return (unsigned)(key * 2654435761u) % (unsigned)n;
}

LFUCache *lfu_cache_create(int capacity) {
    LFUCache *c = calloc(1, sizeof(*c));
    c->capacity = capacity;
    c->nbuckets = capacity * 2 + 1;
    c->nfreq = capacity + 1;
    c->buckets = calloc((size_t)c->nbuckets, sizeof(Entry *));
    c->freq_head = calloc((size_t)c->nfreq, sizeof(Entry *));
    c->freq_tail = calloc((size_t)c->nfreq, sizeof(Entry *));
    return c;
}

static void unlink(LFUCache *c, Entry *e) {
    int f = e->freq;
    if (e->prev) e->prev->next = e->next;
    else c->freq_head[f] = e->next;
    if (e->next) e->next->prev = e->prev;
    else c->freq_tail[f] = e->prev;
    e->prev = e->next = NULL;
}

static void link_back(LFUCache *c, Entry *e) {
    int f = e->freq;
    e->prev = c->freq_tail[f];
    e->next = NULL;
    if (c->freq_tail[f]) c->freq_tail[f]->next = e;
    else c->freq_head[f] = e;
    c->freq_tail[f] = e;
}

static Entry **find_bucket(LFUCache *c, int key) {
    Entry **p = &c->buckets[hash(key, c->nbuckets)];
    while (*p && (*p)->key != key) p = &(*p)->hnext;
    return p;
}

static void bump(LFUCache *c, Entry *e) {
    unlink(c, e);
    if (e->freq == c->min_freq && !c->freq_head[c->min_freq])
        c->min_freq++;
    e->freq++;
    link_back(c, e);
}

int lfu_cache_get(LFUCache *c, int key) {
    Entry **p = find_bucket(c, key);
    if (!*p) return -1;
    bump(c, *p);
    return (*p)->value;
}

void lfu_cache_put(LFUCache *c, int key, int value) {
    if (c->capacity == 0) return;
    Entry **p = find_bucket(c, key);
    if (*p) {
        (*p)->value = value;
        bump(c, *p);
        return;
    }
    if (c->size == c->capacity) {
        Entry *evict = c->freq_head[c->min_freq];
        unlink(c, evict);
        Entry **q = find_bucket(c, evict->key);
        *q = evict->hnext;
        free(evict);
        c->size--;
    }
    Entry *e = calloc(1, sizeof(*e));
    e->key = key;
    e->value = value;
    e->freq = 1;
    e->hnext = c->buckets[hash(key, c->nbuckets)];
    c->buckets[hash(key, c->nbuckets)] = e;
    link_back(c, e);
    c->size++;
    c->min_freq = 1;
}

void lfu_cache_free(LFUCache *c) {
    for (int i = 0; i < c->nbuckets; i++) {
        Entry *e = c->buckets[i];
        while (e) {
            Entry *n = e->hnext;
            free(e);
            e = n;
        }
    }
    free(c->buckets);
    free(c->freq_head);
    free(c->freq_tail);
    free(c);
}
```

```python
from collections import OrderedDict

class LFUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.min_freq = 0
        self.cache = {}      # key -> (value, freq)
        self.freqs = {}      # freq -> OrderedDict[key]

    def _bump(self, key: int, freq: int) -> None:
        freq_map = self.freqs[freq]
        freq_map.pop(key, None)
        if not freq_map:
            del self.freqs[freq]
            if self.min_freq == freq:
                self.min_freq += 1
        self.freqs.setdefault(freq + 1, OrderedDict())[key] = None
        self.cache[key] = (self.cache[key][0], freq + 1)

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        value, freq = self.cache[key]
        self._bump(key, freq)
        return value

    def put(self, key: int, value: int) -> None:
        if self.capacity == 0:
            return
        if key in self.cache:
            _, freq = self.cache[key]
            self.cache[key] = (value, freq)
            self._bump(key, freq)
            return
        if len(self.cache) == self.capacity:
            evict, _ = self.freqs[self.min_freq].popitem(last=False)
            if not self.freqs[self.min_freq]:
                del self.freqs[self.min_freq]
            del self.cache[evict]
        self.cache[key] = (value, 1)
        self.freqs.setdefault(1, OrderedDict())[key] = None
        self.min_freq = 1
```

```rust
use std::collections::{HashMap, VecDeque};

struct LFUCache {
    capacity: usize,
    min_freq: i32,
    cache: HashMap<i32, (i32, i32)>,     // key -> (value, freq)
    freqs: HashMap<i32, VecDeque<i32>>,  // freq -> keys in insertion order
}

impl LFUCache {
    fn new(capacity: i32) -> Self {
        LFUCache {
            capacity: capacity as usize,
            min_freq: 0,
            cache: HashMap::new(),
            freqs: HashMap::new(),
        }
    }

    fn bump(&mut self, key: i32, freq: i32) {
        let keys = self.freqs.get_mut(&freq).unwrap();
        keys.retain(|&k| k != key);
        if keys.is_empty() {
            self.freqs.remove(&freq);
            if self.min_freq == freq {
                self.min_freq += 1;
            }
        }
        self.freqs.entry(freq + 1).or_default().push_back(key);
        if let Some((_, f)) = self.cache.get_mut(&key) {
            *f = freq + 1;
        }
    }

    fn get(&mut self, key: i32) -> i32 {
        match self.cache.get(&key) {
            Some(&(v, f)) => {
                self.bump(key, f);
                v
            }
            None => -1,
        }
    }

    fn put(&mut self, key: i32, value: i32) {
        if self.capacity == 0 {
            return;
        }
        if let Some(&(_, f)) = self.cache.get(&key) {
            self.cache.insert(key, (value, f));
            self.bump(key, f);
            return;
        }
        if self.cache.len() == self.capacity {
            let evict = self.freqs.get_mut(&self.min_freq).unwrap().pop_front().unwrap();
            if self.freqs.get(&self.min_freq).map_or(true, |k| k.is_empty()) {
                self.freqs.remove(&self.min_freq);
            }
            self.cache.remove(&evict);
        }
        self.cache.insert(key, (value, 1));
        self.freqs.entry(1).or_default().push_back(key);
        self.min_freq = 1;
    }
}
```

```typescript
class LFUCache {
    private capacity: number;
    private minFreq = 0;
    private cache = new Map<number, [number, number]>();     // key -> [value, freq]
    private freqs = new Map<number, Map<number, null>>();    // freq -> ordered keys

    constructor(capacity: number) {
        this.capacity = capacity;
    }

    private bump(key: number, freq: number): void {
        const keys = this.freqs.get(freq)!;
        keys.delete(key);
        if (keys.size === 0) {
            this.freqs.delete(freq);
            if (this.minFreq === freq) this.minFreq++;
        }
        if (!this.freqs.has(freq + 1)) this.freqs.set(freq + 1, new Map());
        this.freqs.get(freq + 1)!.set(key, null);
        this.cache.set(key, [this.cache.get(key)![0], freq + 1]);
    }

    get(key: number): number {
        const e = this.cache.get(key);
        if (!e) return -1;
        this.bump(key, e[1]);
        return e[0];
    }

    put(key: number, value: number): void {
        if (this.capacity === 0) return;
        if (this.cache.has(key)) {
            const [, freq] = this.cache.get(key)!;
            this.cache.set(key, [value, freq]);
            this.bump(key, freq);
            return;
        }
        if (this.cache.size === this.capacity) {
            const keys = this.freqs.get(this.minFreq)!;
            const evict = keys.keys().next().value as number;
            keys.delete(evict);
            if (keys.size === 0) this.freqs.delete(this.minFreq);
            this.cache.delete(evict);
        }
        this.cache.set(key, [value, 1]);
        if (!this.freqs.has(1)) this.freqs.set(1, new Map());
        this.freqs.get(1)!.set(key, null);
        this.minFreq = 1;
    }
}
```

```go
package lfu

import "container/list"

type LFUCache struct {
	capacity int
	minFreq  int
	cache    map[int][2]int     // key -> [value, freq]
	freqs    map[int]*list.List // freq -> keys in insertion order
}

func NewLFUCache(capacity int) *LFUCache {
	return &LFUCache{capacity: capacity, cache: make(map[int][2]int), freqs: make(map[int]*list.List)}
}

func (c *LFUCache) bump(key, freq int) {
	l := c.freqs[freq]
	for e := l.Front(); e != nil; e = e.Next() {
		if e.Value.(int) == key {
			l.Remove(e)
			break
		}
	}
	if l.Len() == 0 {
		delete(c.freqs, freq)
		if c.minFreq == freq {
			c.minFreq++
		}
	}
	if c.freqs[freq+1] == nil {
		c.freqs[freq+1] = list.New()
	}
	c.freqs[freq+1].PushBack(key)
	v := c.cache[key]
	c.cache[key] = [2]int{v[0], freq + 1}
}

func (c *LFUCache) Get(key int) int {
	v, ok := c.cache[key]
	if !ok {
		return -1
	}
	c.bump(key, v[1])
	return v[0]
}

func (c *LFUCache) Put(key, value int) {
	if c.capacity == 0 {
		return
	}
	if v, ok := c.cache[key]; ok {
		c.cache[key] = [2]int{value, v[1]}
		c.bump(key, v[1])
		return
	}
	if len(c.cache) == c.capacity {
		l := c.freqs[c.minFreq]
		evict := l.Front()
		key := evict.Value.(int)
		l.Remove(evict)
		if l.Len() == 0 {
			delete(c.freqs, c.minFreq)
		}
		delete(c.cache, key)
	}
	c.cache[key] = [2]int{value, 1}
	if c.freqs[1] == nil {
		c.freqs[1] = list.New()
	}
	c.freqs[1].PushBack(key)
	c.minFreq = 1
}
```

## Tradeoffs
- **Freshness vs. latency**: write-through keeps the cache and DB consistent but makes every write pay the DB cost; write-back is fast but risks data loss on crash and leaves a window of staleness.
- **Read miss cost**: cache-aside reads miss cold and pay a full DB round trip; read-through hides this behind the cache layer but couples the cache to the loader.
- **Eviction fidelity**: LFU favors hot items but can starve newer keys that never accumulate frequency (unlike LRU) and needs the extra frequency bookkeeping.
- **TTL stampede**: long TTLs risk a thundering herd when a popular key expires; mitigation (locking, probabilistic early refresh) adds complexity.
- **Complexity**: write-back requires a flush/replay mechanism and can reorder writes; cache-aside is simplest but pushes invalidation correctness onto every caller.

## When to use
- Cache-aside when the application controls reads and the cache is optional (e.g. product catalogs, user profiles).
- Write-through for read-heavy workloads that must never serve stale data (e.g. configuration, inventory counts).
- Write-back when write throughput matters more than crash consistency (e.g. counters, analytics aggregates).
- LFU when access patterns are skewed and long-lived hot items should be retained.

## Alternatives
- **LRU** — simpler, recency-based eviction; better when popularity shifts quickly but can thrash under scans.
- **Redis cache-aside with TTL** — operationally battle-tested but leaves invalidation to the application.
- **No cache / query DB directly** — zero staleness and complexity at the cost of high read latency.

## Related
- [In-Memory Caching](01-in-memory-caching.md)
- [CDNs and Edge Computing](03-cdns-edge.md)
- [Rate Limiting](04-rate-limiting.md)
