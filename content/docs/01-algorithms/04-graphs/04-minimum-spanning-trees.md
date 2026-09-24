---
title: "Minimum Spanning Trees"
weight: 4
toc: true
---

## What it is
A minimum spanning tree (MST) of a weighted, connected, undirected graph is a subset of edges that connects all vertices with no cycles and minimum total weight. Kruskal's and Prim's algorithms are the two classic ways to build it.

## How it works
Kruskal's algorithm sorts all edges by weight and greedily adds each edge that does not form a cycle, tracked with a union-find (disjoint-set) structure. Prim's algorithm grows a single tree from an arbitrary start vertex, repeatedly adding the cheapest edge crossing the cut from the tree to the rest of the graph, maintained in a priority queue.

```java
import java.util.*;

public class MST {
    static int[] parent, rank;

    static int find(int x) {
        if (parent[x] != x) parent[x] = find(parent[x]);
        return parent[x];
    }

    static boolean union(int a, int b) {
        int ra = find(a), rb = find(b);
        if (ra == rb) return false;
        if (rank[ra] < rank[rb]) { int t = ra; ra = rb; rb = t; }
        parent[rb] = ra;
        if (rank[ra] == rank[rb]) rank[ra]++;
        return true;
    }

    // Kruskal: edges as int[]{u, v, w}
    public static int kruskal(int n, List<int[]> edges) {
        parent = new int[n]; rank = new int[n];
        for (int i = 0; i < n; i++) parent[i] = i;
        edges.sort(Comparator.comparingInt(e -> e[2]));
        int total = 0, count = 0;
        for (int[] e : edges) {
            if (union(e[0], e[1])) {
                total += e[2];
                if (++count == n - 1) break;
            }
        }
        return total;
    }

    // Prim: adjacency list of int[]{v, w}
    public static int prim(List<List<int[]>> adj) {
        int n = adj.size();
        boolean[] inTree = new boolean[n];
        PriorityQueue<int[]> pq = new PriorityQueue<>(Comparator.comparingInt(e -> e[1]));
        pq.add(new int[]{0, 0});
        int total = 0, count = 0;
        while (!pq.isEmpty() && count < n) {
            int[] e = pq.poll();
            int u = e[0];
            if (inTree[u]) continue;
            inTree[u] = true;
            total += e[1];
            count++;
            for (int[] nb : adj.get(u)) {
                if (!inTree[nb[0]]) pq.add(new int[]{nb[0], nb[1]});
            }
        }
        return total;
    }
}
```

```c
#include <stdio.h>
#include <stdlib.h>

typedef struct Edge { int u, v, w; } Edge;

static int* parent; static int* rank;

static int find(int x) {
    if (parent[x] != x) parent[x] = find(parent[x]);
    return parent[x];
}

static int unionSets(int a, int b) {
    int ra = find(a), rb = find(b);
    if (ra == rb) return 0;
    if (rank[ra] < rank[rb]) { int t = ra; ra = rb; rb = t; }
    parent[rb] = ra;
    if (rank[ra] == rank[rb]) rank[ra]++;
    return 1;
}

static int cmpEdge(const void* a, const void* b) {
    return ((Edge*)a)->w - ((Edge*)b)->w;
}

int kruskal(int n, Edge* edges, int m) {
    parent = malloc(n * sizeof(int));
    rank = calloc(n, sizeof(int));
    for (int i = 0; i < n; i++) parent[i] = i;
    qsort(edges, m, sizeof(Edge), cmpEdge);
    int total = 0, count = 0;
    for (int i = 0; i < m && count < n - 1; i++) {
        if (unionSets(edges[i].u, edges[i].v)) {
            total += edges[i].w;
            count++;
        }
    }
    free(parent); free(rank);
    return total;
}
```

```python
from typing import List, Tuple


class DSU:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def kruskal(n: int, edges: List[Tuple[int, int, int]]) -> int:
    dsu = DSU(n)
    edges.sort(key=lambda e: e[2])
    total = 0
    count = 0
    for u, v, w in edges:
        if dsu.union(u, v):
            total += w
            count += 1
            if count == n - 1:
                break
    return total


def prim(adj: List[List[Tuple[int, int]]]) -> int:
    import heapq
    n = len(adj)
    in_tree = [False] * n
    pq = [(0, 0)]
    total = 0
    count = 0
    while pq and count < n:
        w, u = heapq.heappop(pq)
        if in_tree[u]:
            continue
        in_tree[u] = True
        total += w
        count += 1
        for v, vw in adj[u]:
            if not in_tree[v]:
                heapq.heappush(pq, (vw, v))
    return total
```

```rust
use std::cmp::Reverse;
use std::collections::BinaryHeap;

struct DSU {
    parent: Vec<usize>,
    rank: Vec<usize>,
}

impl DSU {
    fn new(n: usize) -> Self {
        DSU { parent: (0..n).collect(), rank: vec![0; n] }
    }
    fn find(&mut self, x: usize) -> usize {
        if self.parent[x] != x {
            let p = self.find(self.parent[x]);
            self.parent[x] = p;
        }
        self.parent[x]
    }
    fn union(&mut self, a: usize, b: usize) -> bool {
        let (mut ra, mut rb) = (self.find(a), self.find(b));
        if ra == rb {
            return false;
        }
        if self.rank[ra] < self.rank[rb] {
            std::mem::swap(&mut ra, &mut rb);
        }
        self.parent[rb] = ra;
        if self.rank[ra] == self.rank[rb] {
            self.rank[ra] += 1;
        }
        true
    }
}

pub fn kruskal(n: usize, edges: &mut [(usize, usize, i32)]) -> i32 {
    edges.sort_by_key(|e| e.2);
    let mut dsu = DSU::new(n);
    let mut total = 0;
    let mut count = 0;
    for &(u, v, w) in edges.iter() {
        if dsu.union(u, v) {
            total += w;
            count += 1;
            if count == n - 1 {
                break;
            }
        }
    }
    total
}

pub fn prim(adj: &[Vec<(usize, i32)>]) -> i32 {
    let n = adj.len();
    let mut in_tree = vec![false; n];
    let mut pq: BinaryHeap<Reverse<(i32, usize)>> = BinaryHeap::new();
    pq.push(Reverse((0, 0)));
    let mut total = 0;
    let mut count = 0;
    while let Some(Reverse((w, u))) = pq.pop() {
        if in_tree[u] {
            continue;
        }
        in_tree[u] = true;
        total += w;
        count += 1;
        if count == n {
            break;
        }
        for &(v, vw) in &adj[u] {
            if !in_tree[v] {
                pq.push(Reverse((vw, v)));
            }
        }
    }
    total
}
```

```typescript
export function kruskal(n: number, edges: [number, number, number][]): number {
  const parent = Array.from({ length: n }, (_, i) => i);
  const rank = new Array(n).fill(0);

  const find = (x: number): number => {
    if (parent[x] !== x) parent[x] = find(parent[x]);
    return parent[x];
  };

  const union = (a: number, b: number): boolean => {
    let ra = find(a);
    let rb = find(b);
    if (ra === rb) return false;
    if (rank[ra] < rank[rb]) [ra, rb] = [rb, ra];
    parent[rb] = ra;
    if (rank[ra] === rank[rb]) rank[ra]++;
    return true;
  };

  edges.sort((a, b) => a[2] - b[2]);
  let total = 0;
  let count = 0;
  for (const [u, v, w] of edges) {
    if (union(u, v)) {
      total += w;
      if (++count === n - 1) break;
    }
  }
  return total;
}

export function prim(adj: [number, number][][]): number {
  const n = adj.length;
  const inTree = new Array(n).fill(false);
  const pq: [number, number][] = [[0, 0]]; // [weight, vertex]
  let total = 0;
  let count = 0;
  while (pq.length > 0 && count < n) {
    pq.sort((a, b) => a[0] - b[0]);
    const [w, u] = pq.shift()!;
    if (inTree[u]) continue;
    inTree[u] = true;
    total += w;
    count++;
    for (const [v, vw] of adj[u]) {
      if (!inTree[v]) pq.push([vw, v]);
    }
  }
  return total;
}
```

```go
package main

import "sort"

type Edge struct{ u, v, w int }

func kruskal(n int, edges []Edge) int {
	parent := make([]int, n)
	rank := make([]int, n)
	for i := range parent {
		parent[i] = i
	}
	var find func(x int) int
	find = func(x int) int {
		if parent[x] != x {
			parent[x] = find(parent[x])
		}
		return parent[x]
	}
	union := func(a, b int) bool {
		ra, rb := find(a), find(b)
		if ra == rb {
			return false
		}
		if rank[ra] < rank[rb] {
			ra, rb = rb, ra
		}
		parent[rb] = ra
		if rank[ra] == rank[rb] {
			rank[ra]++
		}
		return true
	}

	sort.Slice(edges, func(i, j int) bool { return edges[i].w < edges[j].w })
	total, count := 0, 0
	for _, e := range edges {
		if union(e.u, e.v) {
			total += e.w
			count++
			if count == n-1 {
				break
			}
		}
	}
	return total
}
```

## Complexity
| Algorithm | Time | Space |
| --- | --- | --- |
| Kruskal (sort + union-find) | O(E log E) | O(V+E) |
| Prim (binary heap) | O(E log V) | O(V+E) |
| Prim (Fibonacci heap) | O(E + V log V) | O(V+E) |

## When to use
- Use Kruskal when edges can be sorted globally or the graph is sparse; it is simple to implement with union-find.
- Use Prim when the graph is dense or given as an adjacency list; it grows a single connected tree.
- Apply MST to network design (minimum cable/road layout), clustering (single-linkage), and approximation for problems like the traveling salesperson.

## Alternatives
- Borůvka's algorithm — adds many cheapest crossing edges in parallel each round; useful for parallel/distributed MST, but less common in practice.
- Reverse-delete algorithm — starts with the full graph and removes heaviest cycle edges; simpler proof but rarely more efficient.
- Minimum bottleneck spanning tree — minimizes the maximum edge weight rather than total weight, relevant for latency-sensitive networks.

## Related
- [Graph Representations](01-graph-representations.md)
- [Graph Traversals (BFS and DFS)](02-graph-traversals.md)
- [Shortest Paths](05-shortest-paths.md)
- [Union-Find](../02-search-trees/05-union-find.md)
