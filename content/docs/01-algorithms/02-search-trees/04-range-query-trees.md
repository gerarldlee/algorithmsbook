---
title: "Range Queries: Segment Trees, Fenwick Trees (Binary Indexed Trees), and Interval Trees"
weight: 4
toc: true
---

## What it is
Range-query structures maintain aggregates over an indexed collection while values change. A segment tree stores summaries for aligned intervals, a Fenwick tree stores overlapping prefix blocks, and an interval tree groups intervals by endpoint so a query can avoid scanning every record.

## How it works
A segment tree divides an array or coordinate domain in half at each level. A point update recomputes one root-to-leaf path. A range query descends only into children that overlap the requested interval and combines at most O(log n) stored aggregates. A **lazy segment tree** also stores pending transformations or assignments on internal nodes and pushes them downward before descending, which supports range updates without touching every element.

A **Fenwick tree**, or binary indexed tree, stores the aggregate for the block ending at each one-based index `i`; that block has length `i & -i`, the value of its lowest set bit. A point update advances through `i += i & -i`. A prefix query runs backward through `i -= i & -i`. Subtracting two prefix answers gives an inclusive range sum. Fenwick trees support invertible operations such as addition and XOR, but not ordinary min or max.

An **interval tree** is usually an augmented balanced search tree ordered by an interval's lower endpoint. Each node stores the greatest upper endpoint in its subtree. An overlap query first finds intervals whose lower endpoint does not exceed the query's upper endpoint, then uses the stored maxima to skip subtrees that cannot contain a match. The examples below implement the same Fenwick `add`, `prefix_sum`, and `range_sum` operations in all six languages.

```java
public class FenwickTree {
    private final int[] tree;

    public FenwickTree(int[] values) {
        tree = new int[values.length + 1];
        for (int index = 0; index < values.length; index++) add(index, values[index]);
    }

    public void add(int index, int delta) {
        for (int position = index + 1; position < tree.length; position += position & -position) {
            tree[position] += delta;
        }
    }

    public int prefixSum(int index) {
        int sum = 0;
        for (int position = index + 1; position > 0; position -= position & -position) {
            sum += tree[position];
        }
        return sum;
    }

    public int rangeSum(int left, int right) {
        int beforeLeft = left == 0 ? 0 : prefixSum(left - 1);
        return prefixSum(right) - beforeLeft;
    }
}
```

```c
#include <stdlib.h>

typedef struct {
    int *tree;
    int size;
} FenwickTree;

void fenwick_add(FenwickTree *fenwick, int index, int delta);

void fenwick_init(FenwickTree *fenwick, const int *values, int size) {
    fenwick->size = size;
    fenwick->tree = calloc((size_t)size + 1, sizeof(int));
    for (int index = 0; index < size; index++) {
        fenwick_add(fenwick, index, values[index]);
    }
}

void fenwick_destroy(FenwickTree *fenwick) {
    free(fenwick->tree);
    fenwick->tree = NULL;
    fenwick->size = 0;
}

void fenwick_add(FenwickTree *fenwick, int index, int delta) {
    for (int position = index + 1; position <= fenwick->size; position += position & -position) {
        fenwick->tree[position] += delta;
    }
}

int fenwick_prefix_sum(const FenwickTree *fenwick, int index) {
    int sum = 0;
    for (int position = index + 1; position > 0; position -= position & -position) {
        sum += fenwick->tree[position];
    }
    return sum;
}

int fenwick_range_sum(const FenwickTree *fenwick, int left, int right) {
    int beforeLeft = left == 0 ? 0 : fenwick_prefix_sum(fenwick, left - 1);
    return fenwick_prefix_sum(fenwick, right) - beforeLeft;
}
```

```python
class FenwickTree:
    def __init__(self, values):
        self.tree = [0] * (len(values) + 1)
        for index, value in enumerate(values):
            self.add(index, value)

    def add(self, index, delta):
        position = index + 1
        while position < len(self.tree):
            self.tree[position] += delta
            position += position & -position

    def prefix_sum(self, index):
        total = 0
        position = index + 1
        while position > 0:
            total += self.tree[position]
            position -= position & -position
        return total

    def range_sum(self, left, right):
        before_left = 0 if left == 0 else self.prefix_sum(left - 1)
        return self.prefix_sum(right) - before_left
```

```rust
pub struct FenwickTree {
    tree: Vec<i64>,
}

impl FenwickTree {
    pub fn new(values: &[i64]) -> Self {
        let mut fenwick = FenwickTree { tree: vec![0; values.len() + 1] };
        for (index, value) in values.iter().enumerate() {
            fenwick.add(index, *value);
        }
        fenwick
    }

    pub fn add(&mut self, index: usize, delta: i64) {
        let mut position = index + 1;
        while position < self.tree.len() {
            self.tree[position] += delta;
            position += position & position.wrapping_neg();
        }
    }

    pub fn prefix_sum(&self, index: usize) -> i64 {
        let mut sum = 0;
        let mut position = index + 1;
        while position > 0 {
            sum += self.tree[position];
            position -= position & position.wrapping_neg();
        }
        sum
    }

    pub fn range_sum(&self, left: usize, right: usize) -> i64 {
        let before_left = if left == 0 { 0 } else { self.prefix_sum(left - 1) };
        self.prefix_sum(right) - before_left
    }
}
```

```typescript
export class FenwickTree {
    private tree: number[];

    constructor(values: number[]) {
        this.tree = new Array<number>(values.length + 1).fill(0);
        for (let index = 0; index < values.length; index++) this.add(index, values[index]);
    }

    add(index: number, delta: number): void {
        for (let position = index + 1; position < this.tree.length; position += position & -position) {
            this.tree[position] += delta;
        }
    }

    prefixSum(index: number): number {
        let sum = 0;
        for (let position = index + 1; position > 0; position -= position & -position) {
            sum += this.tree[position];
        }
        return sum;
    }

    rangeSum(left: number, right: number): number {
        const beforeLeft = left === 0 ? 0 : this.prefixSum(left - 1);
        return this.prefixSum(right) - beforeLeft;
    }
}
```

```go
package fenwick

type FenwickTree struct {
	tree []int
}

func New(values []int) *FenwickTree {
	fenwick := &FenwickTree{tree: make([]int, len(values)+1)}
	for index, value := range values {
		fenwick.Add(index, value)
	}
	return fenwick
}

func (fenwick *FenwickTree) Add(index, delta int) {
	for position := index + 1; position < len(fenwick.tree); position += position & -position {
		fenwick.tree[position] += delta
	}
}

func (fenwick *FenwickTree) PrefixSum(index int) int {
	sum := 0
	for position := index + 1; position > 0; position -= position & -position {
		sum += fenwick.tree[position]
	}
	return sum
}

func (fenwick *FenwickTree) RangeSum(left, right int) int {
	beforeLeft := 0
	if left > 0 {
		beforeLeft = fenwick.PrefixSum(left - 1)
	}
	return fenwick.PrefixSum(right) - beforeLeft
}
```

## Complexity
| Structure and operation | Time | Extra space |
| --- | --- | --- |
| Segment tree build | O(n) | O(n) |
| Segment tree point update or range query | O(log n) | O(log n) with recursion |
| Segment tree range update or range query with lazy propagation | O(log n) | O(log n) with recursion |
| Fenwick tree build | O(n log n) when populated one value at a time, or O(n) with a linear build | O(n) |
| Fenwick point update | O(log n) | O(1) |
| Fenwick prefix or inclusive range sum | O(log n) | O(1) |
| Interval tree insert or search | O(log n) | O(log n) with recursion |
| Interval overlap or stabbing query returning `k` intervals | O(log n + k) | O(log n) with recursion |

A Fenwick tree uses one additional cell for `n` input values, while a conventional fixed segment-tree array uses O(n) cells and often roughly twice the input count. Fenwick trees are smaller for prefix sums and XOR, while segment trees support associative aggregates such as min, max, and GCD plus range transformations.

## When to use
- You need prefix or range sums with frequent point updates over a mutable array.
- You need min, max, GCD, or range assignments that a Fenwick tree cannot represent directly.
- You need dynamic interval overlap or stabbing queries and can maintain balanced-tree metadata.
- Coordinate compression is acceptable when values are large but the number of distinct values is modest.

## Alternatives
- **Prefix-sum array** — gives O(1) range queries for static data, but each point update can require O(n) work.
- **Balanced search tree** — handles dynamic ordered keys and can return `k` range items in O(log n + k), with larger constants than an array index.
- **Square-root decomposition** — gives O(√n) updates and queries with simpler code, but does not match the logarithmic bound.
- **Interval tree** — wins for overlap and stabbing queries, but requires interval endpoints rather than fixed array positions.

## Related
- [Binary Search Trees](01-binary-search-trees.md)
- [Union-Find (Disjoint Set Union)](05-union-find.md)
- [Storage Engine Trees (B-Trees and LSM-Trees)](03-storage-engine-trees.md)
- [Spatial Indexing & Geospatial Data Structures](07-spatial-indexing.md)
