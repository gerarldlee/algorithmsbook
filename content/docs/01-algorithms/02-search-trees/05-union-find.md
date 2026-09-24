---
title: "Disjoint-Set Data Structures (Union-Find with Path Compression)"
weight: 5
toc: true
---

## What it is
Union-find, also called disjoint-set union, maintains a partition of elements into disjoint sets. `find(x)` returns the representative of `x`, `union(x, y)` merges the sets containing `x` and `y`, and `connected(x, y)` reports whether both elements share a representative. Union by rank or size plus path compression makes these operations O(α(n)) amortized time.

## How it works
Every element stores a parent index. A root is its own parent and represents one set. `find` follows parent pointers to a root, then points each visited node directly to that root with **path compression**. `union` finds both roots and attaches the lower-rank or smaller tree below the higher-rank or larger one with **union by rank** or **union by size**. The root choice bounds tree height, while compression shortens future traversals.

The implementations below expose the same `find`, `union`, and `connected` operations in all six languages. Applications use them for connected components, Kruskal's minimum spanning tree algorithm, image region grouping, and equivalence relations.

```java
public class UnionFind {
    private final int[] parent;
    private final int[] rank;

    public UnionFind(int size) {
        parent = new int[size];
        rank = new int[size];
        for (int index = 0; index < size; index++) parent[index] = index;
    }

    public int find(int element) {
        int root = element;
        while (parent[root] != root) root = parent[root];
        while (parent[element] != element) {
            int next = parent[element];
            parent[element] = root;
            element = next;
        }
        return root;
    }

    public boolean union(int left, int right) {
        int leftRoot = find(left);
        int rightRoot = find(right);
        if (leftRoot == rightRoot) return false;
        if (rank[leftRoot] < rank[rightRoot]) {
            int swap = leftRoot;
            leftRoot = rightRoot;
            rightRoot = swap;
        }
        parent[rightRoot] = leftRoot;
        if (rank[leftRoot] == rank[rightRoot]) rank[leftRoot]++;
        return true;
    }

    public boolean connected(int left, int right) {
        return find(left) == find(right);
    }
}
```

```c
#include <stdbool.h>
#include <stdlib.h>

typedef struct {
    int *parent;
    int *rank;
    int size;
} UnionFind;

void union_find_init(UnionFind *union_find, int size) {
    union_find->parent = malloc((size_t)size * sizeof(int));
    union_find->rank = calloc((size_t)size, sizeof(int));
    union_find->size = size;
    for (int index = 0; index < size; index++) union_find->parent[index] = index;
}

void union_find_destroy(UnionFind *union_find) {
    free(union_find->parent);
    free(union_find->rank);
}

int union_find_find(UnionFind *union_find, int element) {
    int root = element;
    while (union_find->parent[root] != root) root = union_find->parent[root];
    while (union_find->parent[element] != element) {
        int next = union_find->parent[element];
        union_find->parent[element] = root;
        element = next;
    }
    return root;
}

bool union_find_union(UnionFind *union_find, int left, int right) {
    int left_root = union_find_find(union_find, left);
    int right_root = union_find_find(union_find, right);
    if (left_root == right_root) return false;
    if (union_find->rank[left_root] < union_find->rank[right_root]) {
        int swap = left_root;
        left_root = right_root;
        right_root = swap;
    }
    union_find->parent[right_root] = left_root;
    if (union_find->rank[left_root] == union_find->rank[right_root]) {
        union_find->rank[left_root]++;
    }
    return true;
}

bool union_find_connected(UnionFind *union_find, int left, int right) {
    return union_find_find(union_find, left) == union_find_find(union_find, right);
}
```

```python
class UnionFind:
    def __init__(self, size):
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, element):
        root = element
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[element] != element:
            next_element = self.parent[element]
            self.parent[element] = root
            element = next_element
        return root

    def union(self, left, right):
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            return False
        if self.rank[left_root] < self.rank[right_root]:
            left_root, right_root = right_root, left_root
        self.parent[right_root] = left_root
        if self.rank[left_root] == self.rank[right_root]:
            self.rank[left_root] += 1
        return True

    def connected(self, left, right):
        return self.find(left) == self.find(right)
```

```rust
pub struct UnionFind {
    parent: Vec<usize>,
    rank: Vec<usize>,
}

impl UnionFind {
    pub fn new(size: usize) -> Self {
        UnionFind {
            parent: (0..size).collect(),
            rank: vec![0; size],
        }
    }

    pub fn find(&mut self, element: usize) -> usize {
        let mut root = element;
        while self.parent[root] != root {
            root = self.parent[root];
        }
        let mut current = element;
        while self.parent[current] != current {
            let next = self.parent[current];
            self.parent[current] = root;
            current = next;
        }
        root
    }

    pub fn union(&mut self, left: usize, right: usize) -> bool {
        let mut left_root = self.find(left);
        let mut right_root = self.find(right);
        if left_root == right_root {
            return false;
        }
        if self.rank[left_root] < self.rank[right_root] {
            std::mem::swap(&mut left_root, &mut right_root);
        }
        self.parent[right_root] = left_root;
        if self.rank[left_root] == self.rank[right_root] {
            self.rank[left_root] += 1;
        }
        true
    }

    pub fn connected(&mut self, left: usize, right: usize) -> bool {
        self.find(left) == self.find(right)
    }
}
```

```typescript
export class UnionFind {
    private parent: number[];
    private rank: number[];

    constructor(size: number) {
        this.parent = Array.from({ length: size }, (_, index) => index);
        this.rank = new Array<number>(size).fill(0);
    }

    find(element: number): number {
        let root = element;
        while (this.parent[root] !== root) root = this.parent[root];
        let current = element;
        while (this.parent[current] !== current) {
            const next = this.parent[current];
            this.parent[current] = root;
            current = next;
        }
        return root;
    }

    union(left: number, right: number): boolean {
        let leftRoot = this.find(left);
        let rightRoot = this.find(right);
        if (leftRoot === rightRoot) return false;
        if (this.rank[leftRoot] < this.rank[rightRoot]) [leftRoot, rightRoot] = [rightRoot, leftRoot];
        this.parent[rightRoot] = leftRoot;
        if (this.rank[leftRoot] === this.rank[rightRoot]) this.rank[leftRoot]++;
        return true;
    }

    connected(left: number, right: number): boolean {
        return this.find(left) === this.find(right);
    }
}
```

```go
package unionfind

type UnionFind struct {
	parent []int
	rank   []int
}

func New(size int) *UnionFind {
	parent := make([]int, size)
	for index := range parent {
		parent[index] = index
	}
	return &UnionFind{parent: parent, rank: make([]int, size)}
}

func (unionFind *UnionFind) Find(element int) int {
	root := element
	for unionFind.parent[root] != root {
		root = unionFind.parent[root]
	}
	current := element
	for unionFind.parent[current] != current {
		next := unionFind.parent[current]
		unionFind.parent[current] = root
		current = next
	}
	return root
}

func (unionFind *UnionFind) Union(left, right int) bool {
	leftRoot := unionFind.Find(left)
	rightRoot := unionFind.Find(right)
	if leftRoot == rightRoot {
		return false
	}
	if unionFind.rank[leftRoot] < unionFind.rank[rightRoot] {
		leftRoot, rightRoot = rightRoot, leftRoot
	}
	unionFind.parent[rightRoot] = leftRoot
	if unionFind.rank[leftRoot] == unionFind.rank[rightRoot] {
		unionFind.rank[leftRoot]++
	}
	return true
}

func (unionFind *UnionFind) Connected(left, right int) bool {
	return unionFind.Find(left) == unionFind.Find(right)
}
```

## Complexity
| Operation | Time | Extra space | Stored state |
| --- | --- | --- | --- |
| `find` | O(α(n)) amortized | O(1) | O(n) total |
| `union` | O(α(n)) amortized | O(1) | O(n) total |
| `connected` | O(α(n)) amortized | O(1) | O(n) total |

α(n) is the inverse Ackermann function and remains below 5 for practical input sizes. Union by rank keeps individual tree height O(log n) even without compression. Path compression alone can still follow a chain of n elements, while combining both techniques makes the full operation sequence nearly constant amortized time.

## When to use
- You process graph edges and only need to merge components without deleting connections.
- You build a minimum spanning tree with Kruskal's algorithm and reject cycle-forming edges.
- You repeatedly merge named or numeric objects into equivalence classes.
- The operations dominate, while inspecting all edges or running a fresh graph traversal would be wasteful.

## Alternatives
- **DFS or BFS** — gives O(V + E) component discovery, which wins for a small number of static-graph queries.
- **Transitive closure** — gives O(1) constant-time membership after O(V³) preprocessing with matrix methods, which is costly for large graphs.
- **Linked-list sets** — makes merging simple but can require O(n) time to find a representative.
- **Dynamic connectivity algorithms** — handle vertex or edge deletions, but need more structure than a basic union-find.

## Related
- [Range Query Trees (Segment Trees and Fenwick Trees)](04-range-query-trees.md)
- [Minimum Spanning Trees](../04-graphs/04-minimum-spanning-trees.md)
- [Shortest Paths](../04-graphs/05-shortest-paths.md)
- [Amortized Analysis Techniques (Aggregate, Accounting, and Potential Methods)](../03-paradigms/05-amortized-analysis.md)
