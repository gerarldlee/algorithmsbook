---
title: "Range Query Trees (Segment Trees and Fenwick Trees)"
weight: 4
toc: true
---

## What it is
Range query trees answer aggregate queries (sum, min, max, gcd) over contiguous array ranges with updates in logarithmic time. A segment tree stores aggregates for a complete binary tree over the array; a Fenwick tree (binary indexed tree) stores partial prefix sums in an array indexed by low-order bits, answering prefix sums and point updates in O(log n).

## How it works
A segment tree recursively splits the array in half, each internal node holding the aggregate of its two children, so a range query combines O(log n) nodes and a point update walks one root-to-leaf path. A Fenwick tree instead maps each index `i` to the range ending at `i` of length equal to `i & -i` (the lowest set bit); updating position `i` advances upward by `i += i & -i`, while a prefix query walks downward by `i -= i & -i`. Both support point updates and range-sum queries in O(log n); the segment tree also supports lazy propagation for range updates.

```java
public class FenwickTree {
    private final int[] tree;
    private final int n;

    public FenwickTree(int[] values) {
        n = values.length;
        tree = new int[n + 1];
        for (int i = 0; i < n; i++) add(i, values[i]);
    }

    public void add(int index, int delta) {
        for (int i = index + 1; i <= n; i += i & -i) tree[i] += delta;
    }

    public int prefixSum(int index) { // sum of [0..index]
        int sum = 0;
        for (int i = index + 1; i > 0; i -= i & -i) sum += tree[i];
        return sum;
    }

    public int rangeSum(int left, int right) {
        return prefixSum(right) - prefixSum(left - 1);
    }
}
```

```c
#include <stdlib.h>

typedef struct {
    int *tree;
    int n;
} FenwickTree;

void fenwick_init(FenwickTree *ft, int *values, int n) {
    ft->n = n;
    ft->tree = calloc(n + 1, sizeof(int));
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j <= n; j += j & -j)
            ft->tree[j] += values[i];
    }
}

void fenwick_add(FenwickTree *ft, int index, int delta) {
    for (int i = index + 1; i <= ft->n; i += i & -i)
        ft->tree[i] += delta;
}

int fenwick_prefix_sum(FenwickTree *ft, int index) {
    int sum = 0;
    for (int i = index + 1; i > 0; i -= i & -i)
        sum += ft->tree[i];
    return sum;
}

int fenwick_range_sum(FenwickTree *ft, int left, int right) {
    return fenwick_prefix_sum(ft, right) - fenwick_prefix_sum(ft, left - 1);
}
```

```python
class FenwickTree:
    def __init__(self, values):
        self.n = len(values)
        self.tree = [0] * (self.n + 1)
        for i, v in enumerate(values):
            self.add(i, v)

    def add(self, index, delta):
        i = index + 1
        while i <= self.n:
            self.tree[i] += delta
            i += i & -i

    def prefix_sum(self, index):
        total = 0
        i = index + 1
        while i > 0:
            total += self.tree[i]
            i -= i & -i
        return total

    def range_sum(self, left, right):
        return self.prefix_sum(right) - self.prefix_sum(left - 1)
```

```rust
pub struct FenwickTree {
    tree: Vec<i64>,
}

impl FenwickTree {
    pub fn new(values: &[i64]) -> Self {
        let n = values.len();
        let mut ft = FenwickTree { tree: vec![0; n + 1] };
        for (i, &v) in values.iter().enumerate() {
            ft.add(i, v);
        }
        ft
    }

    pub fn add(&mut self, mut index: usize, delta: i64) {
        index += 1;
        while index < self.tree.len() {
            self.tree[index] += delta;
            index += index & index.wrapping_neg();
        }
    }

    pub fn prefix_sum(&self, mut index: usize) -> i64 {
        let mut sum = 0;
        index += 1;
        while index > 0 {
            sum += self.tree[index];
            index -= index & index.wrapping_neg();
        }
        sum
    }

    pub fn range_sum(&self, left: usize, right: usize) -> i64 {
        self.prefix_sum(right) - if left == 0 { 0 } else { self.prefix_sum(left - 1) }
    }
}
```

```typescript
export class FenwickTree {
    private tree: number[];
    private n: number;

    constructor(values: number[]) {
        this.n = values.length;
        this.tree = new Array(this.n + 1).fill(0);
        for (let i = 0; i < this.n; i++) this.add(i, values[i]);
    }

    add(index: number, delta: number): void {
        for (let i = index + 1; i <= this.n; i += i & -i) this.tree[i] += delta;
    }

    prefixSum(index: number): number {
        let sum = 0;
        for (let i = index + 1; i > 0; i -= i & -i) sum += this.tree[i];
        return sum;
    }

    rangeSum(left: number, right: number): number {
        return this.prefixSum(right) - this.prefixSum(left - 1);
    }
}
```

```go
package fenwick

type FenwickTree struct {
	tree []int
}

func New(values []int) *FenwickTree {
	ft := &FenwickTree{tree: make([]int, len(values)+1)}
	for i, v := range values {
		ft.Add(i, v)
	}
	return ft
}

func (ft *FenwickTree) Add(index, delta int) {
	for i := index + 1; i < len(ft.tree); i += i & -i {
		ft.tree[i] += delta
	}
}

func (ft *FenwickTree) PrefixSum(index int) int {
	sum := 0
	for i := index + 1; i > 0; i -= i & -i {
		sum += ft.tree[i]
	}
	return sum
}

func (ft *FenwickTree) RangeSum(left, right int) int {
	return ft.PrefixSum(right) - ft.PrefixSum(left-1)
}
```

## Complexity
| Structure / operation | Time | Space |
| --- | --- | --- |
| Segment tree build | O(n) | O(n) |
| Segment tree point update | O(log n) | O(1) |
| Segment tree range query | O(log n) | O(1) |
| Segment tree range update (lazy) | O(log n) | O(1) |
| Fenwick tree build | O(n) | O(n) |
| Fenwick tree point update | O(log n) | O(1) |
| Fenwick tree prefix/range query | O(log n) | O(1) |

Fenwick trees use a constant factor less memory than segment trees (n+1 vs up to 4n) and are simpler, but they only support invertible aggregates (sum, xor) and point updates; segment trees support non-invertible aggregates (min, max, gcd) and lazy range updates.

## When to use
- When you need frequent range-sum/min/max queries interleaved with point updates on a mutable array.
- Competitive programming range queries, prefix-frequency statistics, and counting inversions.
- Segment tree when the aggregate is non-invertible (min/max/gcd) or you need range updates; Fenwick tree when you only need prefix sums with point updates and want minimal memory.

## Alternatives
- Prefix sum array — O(1) range queries but O(n) per update, so only good for static arrays.
- Balanced BST — supports dynamic ranges but O(log n) per element with heavier constants and no implicit array indexing.
- Sqrt decomposition — O(√n) per query/update, simpler than a segment tree but slower asymptotically.

## Related
- [Binary Search Trees](01-binary-search-trees.md)
- [Union-Find (Disjoint Set Union)](05-union-find.md)
