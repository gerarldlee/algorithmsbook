---
title: "Hash Tables and Hash Sets"
weight: 4
toc: true
---

## What it is

A hash table (or hash map) maps keys to values using a hash function that turns a key into an index into an underlying array of buckets. A hash set is the same structure without values — it just answers "is this key present?". With a good hash function and a low load factor, both give O(1) average-case insert, lookup, and delete, degrading to O(n) in the worst case when many keys collide.

## How it works

Hash sets and hash tables are data structures built on top of a hash function.

- A **hash set** stores unique elements and answers the question "is this element present?"
- A **hash table** maps keys to values, giving O(1) average access, insert, and delete.

Both rely on a hash function that maps a key to an index in the underlying array.

The hash function spreads keys over the bucket array; collisions (two keys hashing to the same bucket) are resolved by separate chaining (a list per bucket) or open addressing (probing for the next free slot). Keeping the load factor (number of entries / number of buckets) low keeps the per-bucket chain short, preserving the average O(1) behavior:

```java
import java.util.LinkedList;

// Hash table with separate chaining
public class HashTable<K, V> {
    private static class Entry<K, V> {
        K key; V value;
        Entry(K key, V value) { this.key = key; this.value = value; }
    }

    private final LinkedList<Entry<K, V>>[] buckets;
    private int size;

    @SuppressWarnings("unchecked")
    public HashTable(int capacity) {
        buckets = new LinkedList[capacity];
        for (int i = 0; i < capacity; i++) buckets[i] = new LinkedList<>();
    }

    private int hash(K key) {
        return Math.floorMod(key.hashCode(), buckets.length);
    }

    public void put(K key, V value) {              // average O(1)
        int i = hash(key);
        for (Entry<K, V> e : buckets[i]) {
            if (e.key.equals(key)) { e.value = value; return; }
        }
        buckets[i].add(new Entry<>(key, value));
        size++;
    }

    public V get(K key) {                          // average O(1)
        int i = hash(key);
        for (Entry<K, V> e : buckets[i]) {
            if (e.key.equals(key)) return e.value;
        }
        return null;
    }

    public boolean contains(K key) { return get(key) != null; }
    public int size() { return size; }
}
```

```c
#include <stdlib.h>
#include <string.h>

typedef struct Entry {
    char *key;
    int value;
    struct Entry *next;
} Entry;

typedef struct {
    Entry **buckets;
    int capacity;
} HashTable;

unsigned long hash(const char *key, int capacity) {
    unsigned long h = 5381;
    int c;
    while ((c = *key++)) h = ((h << 5) + h) + c;  // djb2 hash
    return h % capacity;
}

void ht_put(HashTable *t, const char *key, int value) {  // average O(1)
    unsigned long i = hash(key, t->capacity);
    for (Entry *e = t->buckets[i]; e; e = e->next) {
        if (strcmp(e->key, key) == 0) { e->value = value; return; }
    }
    Entry *n = malloc(sizeof(Entry));
    n->key = strdup(key);
    n->value = value;
    n->next = t->buckets[i];
    t->buckets[i] = n;
}

int ht_get(HashTable *t, const char *key, int *found) {   // average O(1)
    unsigned long i = hash(key, t->capacity);
    for (Entry *e = t->buckets[i]; e; e = e->next) {
        if (strcmp(e->key, key) == 0) { *found = 1; return e->value; }
    }
    *found = 0;
    return 0;
}
```

```python
class HashTable:
    """Hash table with separate chaining."""
    def __init__(self, capacity=16):
        self.buckets = [[] for _ in range(capacity)]

    def _hash(self, key):
        return hash(key) % len(self.buckets)

    def put(self, key, value):        # average O(1)
        i = self._hash(key)
        for pair in self.buckets[i]:
            if pair[0] == key:
                pair[1] = value
                return
        self.buckets[i].append([key, value])

    def get(self, key):               # average O(1)
        i = self._hash(key)
        for k, v in self.buckets[i]:
            if k == key:
                return v
        return None

    def contains(self, key):
        return self.get(key) is not None
```

```rust
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};

pub struct HashTable<K, V> {
    buckets: Vec<Vec<(K, V)>>,
}

impl<K: Hash + Eq, V> HashTable<K, V> {
    pub fn new(capacity: usize) -> Self {
        let mut buckets = Vec::with_capacity(capacity);
        for _ in 0..capacity { buckets.push(Vec::new()); }
        HashTable { buckets }
    }

    fn hash(&self, key: &K) -> usize {
        let mut hasher = DefaultHasher::new();
        key.hash(&mut hasher);
        (hasher.finish() as usize) % self.buckets.len()
    }

    pub fn insert(&mut self, key: K, value: V) {    // average O(1)
        let i = self.hash(&key);
        for pair in self.buckets[i].iter_mut() {
            if pair.0 == key { pair.1 = value; return; }
        }
        self.buckets[i].push((key, value));
    }

    pub fn get(&self, key: &K) -> Option<&V> {      // average O(1)
        let i = self.hash(key);
        self.buckets[i].iter().find(|(k, _)| k == key).map(|(_, v)| v)
    }
}
```

```typescript
class HashTable<K, V> {
    private buckets: Array<Array<[K, V]>>;
    private size: number;

    constructor(capacity: number) {
        this.buckets = new Array(capacity).fill(null).map(() => []);
        this.size = 0;
    }

    private hash(key: K): number {
        let h = 0;
        const s = String(key);
        for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
        return h % this.buckets.length;
    }

    put(key: K, value: V): void {                    // average O(1)
        const i = this.hash(key);
        for (const pair of this.buckets[i]) {
            if (pair[0] === key) { pair[1] = value; return; }
        }
        this.buckets[i].push([key, value]);
        this.size++;
    }

    get(key: K): V | undefined {                    // average O(1)
        const i = this.hash(key);
        for (const [k, v] of this.buckets[i]) {
            if (k === key) return v;
        }
        return undefined;
    }

    contains(key: K): boolean { return this.get(key) !== undefined; }
}
```

```go
type entry struct {
	key   string
	value int
}

type HashTable struct {
	buckets [][]entry
}

func NewHashTable(capacity int) *HashTable {
	buckets := make([][]entry, capacity)
	return &HashTable{buckets: buckets}
}

func (t *HashTable) hash(key string) int {
	h := 0
	for i := 0; i < len(key); i++ {
		h = (h*31 + int(key[i])) & 0x7fffffff
	}
	return h % len(t.buckets)
}

func (t *HashTable) Put(key string, value int) {   // average O(1)
	i := t.hash(key)
	for j, e := range t.buckets[i] {
		if e.key == key { t.buckets[i][j].value = value; return }
	}
	t.buckets[i] = append(t.buckets[i], entry{key, value})
}

func (t *HashTable) Get(key string) (int, bool) {  // average O(1)
	i := t.hash(key)
	for _, e := range t.buckets[i] {
		if e.key == key { return e.value, true }
	}
	return 0, false
}
```

## Complexity

| Operation | Average time | Worst-case time | Space |
| --- | --- | --- | --- |
| Insert / put | O(1) | O(n) | O(n) |
| Lookup / get | O(1) | O(n) | O(n) |
| Delete | O(1) | O(n) | O(n) |
| Contains (hash set) | O(1) | O(n) | O(n) |

## When to use

- You need fast key-based lookup, insert, and delete (caches, dictionaries, symbol tables).
- Deduplicating elements (hash set) or counting frequencies (hash map).
- Building indexes and memoization tables where O(1) expected access matters more than ordering.

## Alternatives

- **Balanced binary search tree** — O(log n) guaranteed operations and ordered iteration, but slower constants and more complex.
- **Array / linear scan** — trivial and cache-friendly, but O(n) lookup for larger collections.
- **Bloom filter** — O(k) constant memory membership test with no false negatives, but allows false positives and cannot store values.

## Related

- [Dynamic Arrays, Memory Allocation, and Amortized Analysis](01-dynamic-arrays.md)
- [Bitwise Operations and Bloom Filters](05-bitwise-bloom-filters.md)
- [Binary Search Trees](../02-search-trees/01-binary-search-trees.md)
