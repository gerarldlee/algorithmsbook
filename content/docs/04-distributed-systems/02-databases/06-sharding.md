---
title: "Sharding"
weight: 6
toc: true
---

## What it is
Sharding partitions a dataset across many nodes so no single machine holds all data or serves all traffic. Each shard owns a subset of keys; the sharding function maps a key to the shard that stores it. Consistent hashing is the canonical algorithm for key-based sharding that minimizes reshuffling when nodes join or leave.

## How it works
Consistent hashing places every node at one or more positions on a hash ring (the hash space `0..2^32-1`). To locate a key, hash the key and walk clockwise to the first node position at or after it, wrapping around. Adding a node only moves the keys in the segment it now owns; each physical node is mapped to many *virtual nodes* spread around the ring to smooth load and reduce hot spots. Range-based sharding instead assigns contiguous key ranges to shards (better for range scans), while hash-based sharding spreads keys uniformly (better for balance but no locality).

```java
import java.util.SortedMap;
import java.util.TreeMap;
import java.security.MessageDigest;

public class ConsistentHash {
    private final SortedMap<Long, String> ring = new TreeMap<>();
    private final int virtualNodes;

    public ConsistentHash(int virtualNodes) {
        this.virtualNodes = virtualNodes;
    }

    private long hash(String key) {
        try {
            byte[] d = MessageDigest.getInstance("MD5").digest(key.getBytes("UTF-8"));
            long h = 0;
            for (int i = 0; i < 8; i++) h = (h << 8) | (d[i] & 0xffL);
            return h;
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    public void addNode(String node) {
        for (int i = 0; i < virtualNodes; i++) {
            ring.put(hash(node + "#" + i), node);
        }
    }

    public void removeNode(String node) {
        for (int i = 0; i < virtualNodes; i++) {
            ring.remove(hash(node + "#" + i));
        }
    }

    public String getNode(String key) {
        if (ring.isEmpty()) return null;
        long h = hash(key);
        SortedMap<Long, String> tail = ring.tailMap(h);
        Long first = tail.isEmpty() ? ring.firstKey() : tail.firstKey();
        return ring.get(first);
    }
}
```

```c
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

/* FNV-1a 64-bit hash */
static uint64_t fnv1a(const char *s) {
    uint64_t h = 1469598103934665603ULL;
    while (*s) { h ^= (unsigned char)*s++; h *= 1099511628211ULL; }
    return h;
}

typedef struct { uint64_t point; char *node; } Slot;

typedef struct {
    Slot *ring;
    size_t len, cap;
    int virtual_nodes;
} ConsistentHash;

static int slot_cmp(const void *a, const void *b) {
    const Slot *x = a, *y = b;
    return (x->point > y->point) - (x->point < y->point);
}

static void add_point(ConsistentHash *ch, uint64_t p, const char *node) {
    if (ch->len == ch->cap) {
        ch->cap = ch->cap ? ch->cap * 2 : 16;
        ch->ring = realloc(ch->ring, ch->cap * sizeof(Slot));
    }
    ch->ring[ch->len].point = p;
    ch->ring[ch->len].node = strdup(node);
    ch->len++;
}

void ch_add_node(ConsistentHash *ch, const char *node) {
    char buf[256];
    for (int i = 0; i < ch->virtual_nodes; i++) {
        snprintf(buf, sizeof buf, "%s#%d", node, i);
        add_point(ch, fnv1a(buf), node);
    }
    qsort(ch->ring, ch->len, sizeof(Slot), slot_cmp);
}

char *ch_get_node(ConsistentHash *ch, const char *key) {
    if (ch->len == 0) return NULL;
    uint64_t h = fnv1a(key);
    /* first slot with point >= h, else wrap to ring[0] */
    size_t lo = 0, hi = ch->len;
    while (lo < hi) {
        size_t mid = (lo + hi) / 2;
        if (ch->ring[mid].point < h) lo = mid + 1; else hi = mid;
    }
    return ch->ring[lo == ch->len ? 0 : lo].node;
}
```

```python
import bisect
import hashlib

class ConsistentHash:
    def __init__(self, virtual_nodes: int = 150):
        self.virtual_nodes = virtual_nodes
        self.ring: list[tuple[int, str]] = []   # sorted by hash point

    def _hash(self, key: str) -> int:
        return int.from_bytes(hashlib.md5(key.encode()).digest()[:8], "big")

    def add_node(self, node: str) -> None:
        for i in range(self.virtual_nodes):
            bisect.insort(self.ring, (self._hash(f"{node}#{i}"), node))

    def remove_node(self, node: str) -> None:
        self.ring = [(p, n) for p, n in self.ring if n != node]

    def get_node(self, key: str) -> str | None:
        if not self.ring:
            return None
        h = self._hash(key)
        idx = bisect.bisect_right(self.ring, (h, ""))
        if idx == len(self.ring):
            idx = 0
        return self.ring[idx][1]
```

```rust
use std::collections::BTreeMap;
use std::hash::{Hash, Hasher};

#[derive(Default)]
pub struct ConsistentHash {
    ring: BTreeMap<u64, String>,
    virtual_nodes: usize,
}

fn hash(key: &str) -> u64 {
    let mut h = std::collections::hash_map::DefaultHasher::new();
    key.hash(&mut h);
    h.finish()
}

impl ConsistentHash {
    pub fn new(virtual_nodes: usize) -> Self {
        Self { ring: BTreeMap::new(), virtual_nodes }
    }

    pub fn add_node(&mut self, node: &str) {
        for i in 0..self.virtual_nodes {
            let key = format!("{}#{}", node, i);
            self.ring.insert(hash(&key), node.to_string());
        }
    }

    pub fn remove_node(&mut self, node: &str) {
        self.ring.retain(|_, n| n != node);
    }

    pub fn get_node(&self, key: &str) -> Option<&str> {
        let h = hash(key);
        self.ring
            .range(h..)
            .next()
            .or_else(|| self.ring.iter().next())
            .map(|(_, n)| n.as_str())
    }
}
```

```typescript
interface RingEntry { point: number; node: string }

export class ConsistentHash {
  private ring: RingEntry[] = [];

  constructor(private virtualNodes = 150) {}

  private hash(key: string): number {
    let h = 2166136261; // FNV-1a 32-bit
    for (let i = 0; i < key.length; i++) {
      h ^= key.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return h >>> 0;
  }

  addNode(node: string): void {
    for (let i = 0; i < this.virtualNodes; i++) {
      this.ring.push({ point: this.hash(`${node}#${i}`), node });
    }
    this.ring.sort((a, b) => a.point - b.point);
  }

  removeNode(node: string): void {
    this.ring = this.ring.filter((e) => e.node !== node);
  }

  getNode(key: string): string | null {
    if (this.ring.length === 0) return null;
    const h = this.hash(key);
    let lo = 0, hi = this.ring.length;
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      if (this.ring[mid].point < h) lo = mid + 1; else hi = mid;
    }
    return this.ring[lo === this.ring.length ? 0 : lo].node;
  }
}
```

```go
package main

import (
	"hash/fnv"
	"sort"
	"strconv"
)

type ringEntry struct {
	point uint64
	node  string
}

type ConsistentHash struct {
	ring         []ringEntry
	virtualNodes int
}

func NewConsistentHash(virtualNodes int) *ConsistentHash {
	return &ConsistentHash{virtualNodes: virtualNodes}
}

func (ch *ConsistentHash) hash(key string) uint64 {
	h := fnv.New64a()
	h.Write([]byte(key))
	return h.Sum64()
}

func (ch *ConsistentHash) AddNode(node string) {
	for i := 0; i < ch.virtualNodes; i++ {
		ch.ring = append(ch.ring, ringEntry{
			point: ch.hash(node + "#" + strconv.Itoa(i)),
			node:  node,
		})
	}
	sort.Slice(ch.ring, func(a, b int) bool {
		return ch.ring[a].point < ch.ring[b].point
	})
}

func (ch *ConsistentHash) RemoveNode(node string) {
	out := ch.ring[:0]
	for _, e := range ch.ring {
		if e.node != node {
			out = append(out, e)
		}
	}
	ch.ring = out
}

func (ch *ConsistentHash) GetNode(key string) string {
	if len(ch.ring) == 0 {
		return ""
	}
	h := ch.hash(key)
	idx := sort.Search(len(ch.ring), func(i int) bool {
		return ch.ring[i].point >= h
	})
	if idx == len(ch.ring) {
		idx = 0
	}
	return ch.ring[idx].node
}
```

## Tradeoffs
| Property | Characteristic |
| --- | --- |
| Data locality | Range sharding enables efficient range scans; hash sharding destroys locality for uniform balance. |
| Hot spots | A single hot key still overloads its shard; virtual nodes smooth node-level imbalance, not key-level skew. |
| Rebalancing | Consistent hashing moves only ~1/N of keys on node changes; range shards may need large splits/migrations. |
| Cross-shard queries | Joins and secondary indexes spanning shards are expensive; scatter-gather adds latency. |
| Resharding cost | Data migration is slow and must be planned; rebalancing during live traffic risks inconsistency. |

## When to use
- Datasets too large for a single node, or write/read throughput exceeding one machine.
- Key-based access patterns (lookups by user ID, tenant ID) where per-shard locality is enough.
- Systems that must grow incrementally — consistent hashing minimizes disruption when adding/removing nodes.

## Alternatives
- Range sharding — ordered range scans within a shard, but risk uneven load and hot ranges.
- Directory-based sharding (a mapping service) — flexible placement and rebalancing, at the cost of a lookup hop.
- Replication without sharding — simpler and full-data reads, but every node still holds the whole dataset.

## Related
- [Replication](05-replication.md)
- [Distributed Query and Point-in-Time Recovery](07-distributed-query-pitr.md)
- [NoSQL Databases](02-nosql.md)
- [Storage Engines](03-storage-engines.md)
