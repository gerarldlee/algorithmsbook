---
title: "Shortest Paths"
weight: 5
toc: true
---

## What it is
Shortest-path algorithms find the minimum-weight path between vertices in a weighted graph. Dijkstra's algorithm handles non-negative weights, Bellman–Ford tolerates negative edges and detects negative cycles, and Floyd–Warshall computes all-pairs shortest paths.

## How it works
Dijkstra's algorithm greedily relaxes edges from a priority queue of the nearest unvisited vertex, correct when weights are non-negative. Bellman–Ford relaxes every edge V−1 times, settling shortest paths and detecting a negative cycle if a further relaxation succeeds. Floyd–Warshall is a dynamic-programming triple loop over all pairs using intermediate vertices.

```java
import java.util.*;

public class ShortestPaths {
    static final int INF = Integer.MAX_VALUE / 2;

    // Dijkstra on adjacency list of int[]{v, w}
    public static int[] dijkstra(List<List<int[]>> adj, int src) {
        int n = adj.size();
        int[] dist = new int[n];
        Arrays.fill(dist, INF);
        dist[src] = 0;
        PriorityQueue<int[]> pq = new PriorityQueue<>(Comparator.comparingInt(e -> e[1]));
        pq.add(new int[]{src, 0});
        while (!pq.isEmpty()) {
            int[] e = pq.poll();
            int u = e[0], d = e[1];
            if (d > dist[u]) continue;
            for (int[] nb : adj.get(u)) {
                int v = nb[0], w = nb[1];
                if (dist[u] + w < dist[v]) {
                    dist[v] = dist[u] + w;
                    pq.add(new int[]{v, dist[v]});
                }
            }
        }
        return dist;
    }

    // Bellman-Ford: edges as int[]{u, v, w}
    public static int[] bellmanFord(int n, List<int[]> edges, int src) {
        int[] dist = new int[n];
        Arrays.fill(dist, INF);
        dist[src] = 0;
        for (int i = 0; i < n - 1; i++) {
            for (int[] e : edges) {
                if (dist[e[0]] + e[2] < dist[e[1]]) {
                    dist[e[1]] = dist[e[0]] + e[2];
                }
            }
        }
        return dist;
    }

    // Floyd-Warshall: matrix of int[][]
    public static int[][] floydWarshall(int[][] g) {
        int n = g.length;
        int[][] dist = new int[n][];
        for (int i = 0; i < n; i++) dist[i] = g[i].clone();
        for (int k = 0; k < n; k++)
            for (int i = 0; i < n; i++)
                for (int j = 0; j < n; j++)
                    if (dist[i][k] + dist[k][j] < dist[i][j])
                        dist[i][j] = dist[i][k] + dist[k][j];
        return dist;
    }
}
```

```c
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

#define INF (INT_MAX / 2)

typedef struct Edge { int u, v, w; } Edge;

// Bellman-Ford
void bellmanFord(int n, Edge* edges, int m, int src, int* dist) {
    for (int i = 0; i < n; i++) dist[i] = INF;
    dist[src] = 0;
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < m; j++) {
            int u = edges[j].u, v = edges[j].v, w = edges[j].w;
            if (dist[u] + w < dist[v]) dist[v] = dist[u] + w;
        }
    }
}

// Floyd-Warshall
void floydWarshall(int n, int** g, int** dist) {
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            dist[i][j] = g[i][j];
    for (int k = 0; k < n; k++)
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++)
                if (dist[i][k] + dist[k][j] < dist[i][j])
                    dist[i][j] = dist[i][k] + dist[k][j];
}
```

```python
import heapq
from typing import List, Tuple


def dijkstra(adj: List[List[Tuple[int, int]]], src: int) -> List[int]:
    n = len(adj)
    dist = [float("inf")] * n
    dist[src] = 0
    pq: List[Tuple[int, int]] = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))
    return dist


def bellman_ford(n: int, edges: List[Tuple[int, int, int]], src: int) -> List[int]:
    dist = [float("inf")] * n
    dist[src] = 0
    for _ in range(n - 1):
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    return dist


def floyd_warshall(g: List[List[int]]) -> List[List[int]]:
    n = len(g)
    dist = [row[:] for row in g]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist
```

```rust
use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn dijkstra(adj: &[Vec<(usize, i32)>], src: usize) -> Vec<i32> {
    let n = adj.len();
    let mut dist = vec![i32::MAX / 2; n];
    dist[src] = 0;
    let mut pq = BinaryHeap::new();
    pq.push(Reverse((0, src)));
    while let Some(Reverse((d, u))) = pq.pop() {
        if d > dist[u] {
            continue;
        }
        for &(v, w) in &adj[u] {
            if dist[u] + w < dist[v] {
                dist[v] = dist[u] + w;
                pq.push(Reverse((dist[v], v)));
            }
        }
    }
    dist
}

pub fn bellman_ford(n: usize, edges: &[(usize, usize, i32)], src: usize) -> Vec<i32> {
    let mut dist = vec![i32::MAX / 2; n];
    dist[src] = 0;
    for _ in 0..n - 1 {
        for &(u, v, w) in edges {
            if dist[u] + w < dist[v] {
                dist[v] = dist[u] + w;
            }
        }
    }
    dist
}

pub fn floyd_warshall(g: &[Vec<i32>]) -> Vec<Vec<i32>> {
    let n = g.len();
    let mut dist = g.to_vec();
    for k in 0..n {
        for i in 0..n {
            for j in 0..n {
                if dist[i][k] + dist[k][j] < dist[i][j] {
                    dist[i][j] = dist[i][k] + dist[k][j];
                }
            }
        }
    }
    dist
}
```

```typescript
export function dijkstra(adj: [number, number][][], src: number): number[] {
  const n = adj.length;
  const dist = new Array(n).fill(Number.MAX_SAFE_INTEGER);
  dist[src] = 0;
  const pq: [number, number][] = [[0, src]];
  while (pq.length > 0) {
    pq.sort((a, b) => a[0] - b[0]);
    const [d, u] = pq.shift()!;
    if (d > dist[u]) continue;
    for (const [v, w] of adj[u]) {
      if (dist[u] + w < dist[v]) {
        dist[v] = dist[u] + w;
        pq.push([dist[v], v]);
      }
    }
  }
  return dist;
}

export function bellmanFord(n: number, edges: [number, number, number][], src: number): number[] {
  const dist = new Array(n).fill(Number.MAX_SAFE_INTEGER);
  dist[src] = 0;
  for (let i = 0; i < n - 1; i++) {
    for (const [u, v, w] of edges) {
      if (dist[u] + w < dist[v]) dist[v] = dist[u] + w;
    }
  }
  return dist;
}

export function floydWarshall(g: number[][]): number[][] {
  const n = g.length;
  const dist = g.map((row) => [...row]);
  for (let k = 0; k < n; k++) {
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        if (dist[i][k] + dist[k][j] < dist[i][j]) {
          dist[i][j] = dist[i][k] + dist[k][j];
        }
      }
    }
  }
  return dist;
}
```

```go
package main

import "container/heap"

type Item struct{ d, v int }
type MinHeap []Item

func (h MinHeap) Len() int            { return len(h) }
func (h MinHeap) Less(i, j int) bool  { return h[i].d < h[j].d }
func (h MinHeap) Swap(i, j int)       { h[i], h[j] = h[j], h[i] }
func (h *MinHeap) Push(x any)         { *h = append(*h, x.(Item)) }
func (h *MinHeap) Pop() any {
	old := *h
	n := len(old)
	it := old[n-1]
	*h = old[:n-1]
	return it
}

func dijkstra(adj [][][2]int, src int) []int {
	n := len(adj)
	const INF = int(^uint(0) >> 1) / 2
	dist := make([]int, n)
	for i := range dist {
		dist[i] = INF
	}
	dist[src] = 0
	h := &MinHeap{{0, src}}
	heap.Init(h)
	for h.Len() > 0 {
		it := heap.Pop(h).(Item)
		u, d := it.v, it.d
		if d > dist[u] {
			continue
		}
		for _, nb := range adj[u] {
			v, w := nb[0], nb[1]
			if dist[u]+w < dist[v] {
				dist[v] = dist[u] + w
				heap.Push(h, Item{dist[v], v})
			}
		}
	}
	return dist
}

func bellmanFord(n int, edges [][3]int, src int) []int {
	const INF = int(^uint(0) >> 1) / 2
	dist := make([]int, n)
	for i := range dist {
		dist[i] = INF
	}
	dist[src] = 0
	for i := 0; i < n-1; i++ {
		for _, e := range edges {
			u, v, w := e[0], e[1], e[2]
			if dist[u]+w < dist[v] {
				dist[v] = dist[u] + w
			}
		}
	}
	return dist
}

func floydWarshall(g [][]int) [][]int {
	n := len(g)
	dist := make([][]int, n)
	for i := range g {
		dist[i] = append([]int(nil), g[i]...)
	}
	for k := 0; k < n; k++ {
		for i := 0; i < n; i++ {
			for j := 0; j < n; j++ {
				if dist[i][k]+dist[k][j] < dist[i][j] {
					dist[i][j] = dist[i][k] + dist[k][j]
				}
			}
		}
	}
	return dist
}
```

## Complexity
| Algorithm | Time | Space |
| --- | --- | --- |
| Dijkstra (binary heap) | O((V+E) log V) | O(V) |
| Bellman-Ford | O(V·E) | O(V) |
| Floyd-Warshall | O(V³) | O(V²) |

## When to use
- Use Dijkstra for single-source shortest paths with non-negative weights (road networks, routing protocols like OSPF).
- Use Bellman-Ford when edges may be negative or when negative-cycle detection is required (currency arbitrage).
- Use Floyd-Warshall for dense graphs needing all-pairs shortest paths, or for transitive closure.

## Alternatives
- A* search — Dijkstra guided by a heuristic to reach a single target faster, but needs an admissible heuristic.
- Johnson's algorithm — all-pairs shortest paths via Bellman-Ford reweighting plus Dijkstra; better than Floyd-Warshall on sparse graphs.
- BFS (unweighted) — gives shortest paths in O(V+E) when all edge weights are 1, but cannot handle weights.

## Related
- [Graph Representations](01-graph-representations.md)
- [Graph Traversals (BFS and DFS)](02-graph-traversals.md)
- [Minimum Spanning Trees](04-minimum-spanning-trees.md)
- [Network Flow](06-network-flow.md)
