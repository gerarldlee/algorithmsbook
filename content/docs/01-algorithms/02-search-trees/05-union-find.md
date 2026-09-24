---
title: "Union-Find (Disjoint Set Union)"
weight: 5
toc: true
---

## What it is
Union-find (disjoint-set union) maintains a collection of disjoint sets supporting two operations: `find(x)` returns the representative of the set containing `x`, and `union(x, y)` merges the two sets containing `x` and `y`. With union by rank/size and path compression, both operations run in nearly-constant amortized time.

## How it works
Each element points to a parent, with a root node whose parent is itself acting as the set representative. `find` follows parent pointers to the root and, via path compression, re-links every visited node directly to the root. `union` attaches the root of the smaller (by rank or size) set under the root of the larger one, keeping trees shallow. Together these yield an amortized time of O(α(n)), where α is the inverse Ackermann function — effectively constant for any practical n.

```java
public class UnionFind {
    private final int[] parent;
    private final int[] rank;

    public UnionFind(int n) {
        parent = new int[n];
        rank = new int[n];
        for (int i = 0; i < n; i++) parent[i] = i;
    }

    public int find(int x) {
        if (parent[x] != x) parent[x] = find(parent[x]); // path compression
        return parent[x];
    }

    public boolean union(int x, int y) {
        int rx = find(x), ry = find(y);
        if (rx == ry) return false;
        if (rank[rx] < rank[ry]) { int t = rx; rx = ry; ry = t; }
        parent[ry] = rx;
        if (rank[rx] == rank[ry]) rank[rx]++;
        return true;
    }

    public boolean connected(int x, int y) {
        return find(x) == find(y);
    }
}
```

```c
#include <stdbool.h>

typedef struct {
    int *parent;
    int *rank;
    int n;
} UnionFind;

void uf_init(UnionFind *uf, int n) {
    uf->n = n;
    uf->parent = malloc(n * sizeof(int));
    uf->rank = calloc(n, sizeof(int));
    for (int i = 0; i < n; i++) uf->parent[i] = i;
}

int uf_find(UnionFind *uf, int x) {
    if (uf->parent[x] != x)
        uf->parent[x] = uf_find(uf, uf->parent[x]); /* path compression */
    return uf->parent[x];
}

bool uf_union(UnionFind *uf, int x, int y) {
    int rx = uf_find(uf, x), ry = uf_find(uf, y);
    if (rx == ry) return false;
    if (uf->rank[rx] < uf->rank[ry]) { int t = rx; rx = ry; ry = t; }
    uf->parent[ry] = rx;
    if (uf->rank[rx] == uf->rank[ry]) uf->rank[rx]++;
    return true;
}
```

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True

    def connected(self, x, y):
        return self.find(x) == self.find(y)
```

```rust
pub struct UnionFind {
    parent: Vec<usize>,
    rank: Vec<usize>,
}

impl UnionFind {
    pub fn new(n: usize) -> Self {
        UnionFind {
            parent: (0..n).collect(),
            rank: vec![0; n],
        }
    }

    pub fn find(&mut self, x: usize) -> usize {
        if self.parent[x] != x {
            let root = self.find(self.parent[x]);
            self.parent[x] = root; // path compression
        }
        self.parent[x]
    }

    pub fn union(&mut self, x: usize, y: usize) -> bool {
        let mut rx = self.find(x);
        let mut ry = self.find(y);
        if rx == ry {
            return false;
        }
        if self.rank[rx] < self.rank[ry] {
            std::mem::swap(&mut rx, &mut ry);
        }
        self.parent[ry] = rx;
        if self.rank[rx] == self.rank[ry] {
            self.rank[rx] += 1;
        }
        true
    }
}
```

```typescript
export class UnionFind {
    private parent: number[];
    private rank: number[];

    constructor(n: number) {
        this.parent = Array.from({ length: n }, (_, i) => i);
        this.rank = new Array(n).fill(0);
    }

    find(x: number): number {
        if (this.parent[x] !== x) {
            this.parent[x] = this.find(this.parent[x]); // path compression
        }
        return this.parent[x];
    }

    union(x: number, y: number): boolean {
        let rx = this.find(x), ry = this.find(y);
        if (rx === ry) return false;
        if (this.rank[rx] < this.rank[ry]) [rx, ry] = [ry, rx];
        this.parent[ry] = rx;
        if (this.rank[rx] === this.rank[ry]) this.rank[rx]++;
        return true;
    }
}
```

```go
package unionfind

type UnionFind struct {
	parent []int
	rank   []int
}

func New(n int) *UnionFind {
	parent := make([]int, n)
	for i := range parent {
		parent[i] = i
	}
	return &UnionFind{parent: parent, rank: make([]int, n)}
}

func (uf *UnionFind) Find(x int) int {
	if uf.parent[x] != x {
		uf.parent[x] = uf.Find(uf.parent[x]) // path compression
	}
	return uf.parent[x]
}

func (uf *UnionFind) Union(x, y int) bool {
	rx, ry := uf.Find(x), uf.Find(y)
	if rx == ry {
		return false
	}
	if uf.rank[rx] < uf.rank[ry] {
		rx, ry = ry, rx
	}
	uf.parent[ry] = rx
	if uf.rank[rx] == uf.rank[ry] {
		uf.rank[rx]++
	}
	return true
}
```

## Complexity
| Operation | Time (amortized) | Space |
| --- | --- | --- |
| find (with path compression) | O(α(n)) | O(n) |
| union (with union by rank/size) | O(α(n)) | O(n) |
| connected | O(α(n)) | O(n) |

α(n) is the inverse Ackermann function, which grows so slowly it is below 5 for any n representable in the universe. Without both optimizations, find can degrade to O(n) and union to O(n) per operation in the worst case.

## When to use
- Detecting connected components in an undirected graph (e.g. Kruskal's MST algorithm).
- Tracking connectivity in dynamic graph problems and percolation simulations.
- Grouping elements into equivalence classes, such as accounts that share an email or network hosts that share a connection.

## Alternatives
- DFS/BFS per query — O(V + E) to answer connectivity but recomputed from scratch each time; better when the graph is static and queried once.
- Adjacency matrix with transitive closure — O(1) queries after O(V³) preprocessing, only viable for tiny static graphs.
- Linked-list representation of sets — simpler union but O(n) find.

## Related
- [Range Query Trees (Segment Trees and Fenwick Trees)](04-range-query-trees.md)
- [Memory Works (Templates)](../../00-essentials/06-memory-works-templates.md)
