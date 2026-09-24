---
title: "Bitwise Operations and Bloom Filters"
weight: 5
toc: true
---

## What it is

Bitwise operations (`AND`, `OR`, `XOR`, `NOT`, and shifts) manipulate the individual bits of an integer and run in a single machine instruction, making them the fastest primitives available for masking, flag packing, and arithmetic tricks. A Bloom filter is a space-efficient probabilistic set built on a bit array and `k` hash functions: it tells you an element is *definitely not* in the set or *possibly* in the set, trading a controllable false-positive rate for dramatic memory savings over a hash set.

## How it works

A Bloom filter holds an array of `m` bits, initially all 0. To add an element, it runs `k` independent hash functions and sets the resulting `k` bit positions to 1. To query, it hashes the element and checks whether *all* `k` positions are set: if any is 0, the element is definitely absent; if all are 1, it is *possibly* present. False positives happen when unrelated insertions happen to set all `k` bits. Bitwise `AND`/`OR`/`XOR`/`NOT` and shifts map directly to CPU instructions and are O(1); the Bloom filter's `add` and `query` are O(k), independent of the number of stored elements:

```java
import java.util.BitSet;

public class BloomFilter {
    private final BitSet bits;
    private final int size;
    private final int hashCount;

    public BloomFilter(int size, int hashCount) {
        this.bits = new BitSet(size);
        this.size = size;
        this.hashCount = hashCount;
    }

    private int hash(String value, int seed) {
        int h = 0;
        for (int i = 0; i < value.length(); i++) {
            h = (h * seed) ^ value.charAt(i);
        }
        return Math.floorMod(h, size);
    }

    public void add(String value) {                  // O(k)
        for (int i = 0; i < hashCount; i++) {
            bits.set(hash(value, 31 + i));
        }
    }

    public boolean mightContain(String value) {      // O(k), no false negatives
        for (int i = 0; i < hashCount; i++) {
            if (!bits.get(hash(value, 31 + i))) return false;
        }
        return true;
    }
}
```

```c
#include <stdlib.h>

typedef struct {
    unsigned char *bits;  // bit array
    int size;             // number of bits
    int hash_count;
} BloomFilter;

void bf_set(BloomFilter *bf, int index) {
    bf->bits[index / 8] |= (1u << (index % 8));
}

int bf_get(BloomFilter *bf, int index) {
    return (bf->bits[index / 8] >> (index % 8)) & 1u;
}

int bf_hash(const char *value, int seed, int size) {
    unsigned long h = 5381;
    int c;
    while ((c = *value++)) h = ((h << 5) + h) ^ (c + seed);
    return (int)(h % size);
}

void bf_add(BloomFilter *bf, const char *value) {    // O(k)
    for (int i = 0; i < bf->hash_count; i++) {
        bf_set(bf, bf_hash(value, 31 + i, bf->size));
    }
}

int bf_might_contain(BloomFilter *bf, const char *value) { // O(k)
    for (int i = 0; i < bf->hash_count; i++) {
        if (!bf_get(bf, bf_hash(value, 31 + i, bf->size))) return 0;
    }
    return 1;
}
```

```python
class BloomFilter:
    def __init__(self, size, hash_count):
        self.bits = bytearray((size + 7) // 8)
        self.size = size
        self.hash_count = hash_count

    def _hash(self, value, seed):
        h = 0
        for ch in value:
            h = (h * seed) ^ ord(ch)
        return h % self.size

    def add(self, value):                             # O(k)
        for i in range(self.hash_count):
            index = self._hash(value, 31 + i)
            self.bits[index // 8] |= (1 << (index % 8))

    def might_contain(self, value):                   # O(k), no false negatives
        for i in range(self.hash_count):
            index = self._hash(value, 31 + i)
            if not (self.bits[index // 8] >> (index % 8)) & 1:
                return False
        return True
```

```rust
pub struct BloomFilter {
    bits: Vec<u8>,
    size: usize,
    hash_count: usize,
}

impl BloomFilter {
    pub fn new(size: usize, hash_count: usize) -> Self {
        BloomFilter {
            bits: vec![0; (size + 7) / 8],
            size,
            hash_count,
        }
    }

    fn hash(&self, value: &str, seed: usize) -> usize {
        let mut h: usize = 0;
        for c in value.bytes() {
            h = h.wrapping_mul(seed) ^ (c as usize);
        }
        h % self.size
    }

    pub fn add(&mut self, value: &str) {              // O(k)
        for i in 0..self.hash_count {
            let index = self.hash(value, 31 + i);
            self.bits[index / 8] |= 1 << (index % 8);
        }
    }

    pub fn might_contain(&self, value: &str) -> bool { // O(k)
        for i in 0..self.hash_count {
            let index = self.hash(value, 31 + i);
            if (self.bits[index / 8] >> (index % 8)) & 1 == 0 {
                return false;
            }
        }
        true
    }
}
```

```typescript
class BloomFilter {
    private bits: Uint8Array;
    private size: number;
    private hashCount: number;

    constructor(size: number, hashCount: number) {
        this.bits = new Uint8Array(Math.ceil(size / 8));
        this.size = size;
        this.hashCount = hashCount;
    }

    private hash(value: string, seed: number): number {
        let h = 0;
        for (let i = 0; i < value.length; i++) {
            h = (h * seed) ^ value.charCodeAt(i);
        }
        return ((h % this.size) + this.size) % this.size;
    }

    add(value: string): void {                        // O(k)
        for (let i = 0; i < this.hashCount; i++) {
            const index = this.hash(value, 31 + i);
            this.bits[index >> 3] |= (1 << (index & 7));
        }
    }

    mightContain(value: string): boolean {            // O(k), no false negatives
        for (let i = 0; i < this.hashCount; i++) {
            const index = this.hash(value, 31 + i);
            if (((this.bits[index >> 3] >> (index & 7)) & 1) === 0) return false;
        }
        return true;
    }
}
```

```go
type BloomFilter struct {
	bits      []byte
	size      int
	hashCount int
}

func NewBloomFilter(size, hashCount int) *BloomFilter {
	return &BloomFilter{
		bits:      make([]byte, (size+7)/8),
		size:      size,
		hashCount: hashCount,
	}
}

func (f *BloomFilter) hash(value string, seed int) int {
	h := 0
	for i := 0; i < len(value); i++ {
		h = (h * seed) ^ int(value[i])
	}
	return (h%f.size + f.size) % f.size
}

func (f *BloomFilter) Add(value string) {            // O(k)
	for i := 0; i < f.hashCount; i++ {
		index := f.hash(value, 31+i)
		f.bits[index/8] |= 1 << (index % 8)
	}
}

func (f *BloomFilter) MightContain(value string) bool { // O(k)
	for i := 0; i < f.hashCount; i++ {
		index := f.hash(value, 31+i)
		if (f.bits[index/8]>>(index%8))&1 == 0 {
			return false
		}
	}
	return true
}
```

## Complexity

| Operation | Time | Space |
| --- | --- | --- |
| Bitwise AND / OR / XOR / NOT | O(1) | O(1) |
| Bit shift (left/right) | O(1) | O(1) |
| Bloom filter add | O(k) | O(m) bits |
| Bloom filter query | O(k) | O(1) |
| False-positive probability | ≈ (1 − e^(−kn/m))^k | — |

`k` is the number of hash functions, `m` the bit-array size, `n` the number of inserted elements.

## When to use

- Bitwise ops: flag packing, permissions masks, parity/`x & (x-1)` tricks, fast multiply/divide by powers of two, low-level protocol parsing.
- Bloom filter: "definitely absent" membership checks before an expensive lookup (e.g. cache/database/disk), spam/URL filtering, spell-check dictionaries where occasional false positives are acceptable.

## Alternatives

- **Hash set / hash table** — exact membership with no false positives and stores values, but uses far more memory per element.
- **Counting Bloom filter** — supports deletes by storing counts per bit, at the cost of more memory.
- **Cuckoo filter** — supports deletes and better space efficiency for low false-positive rates, but more complex to implement.

## Related

- [Hash Tables and Hash Sets](04-hash-tables.md)
- [Dynamic Arrays, Memory Allocation, and Amortized Analysis](01-dynamic-arrays.md)
- [In-Memory Caching](../../02-system-design/02-caching/01-in-memory-caching.md)
