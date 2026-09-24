---
title: "Graph Traversals (BFS and DFS)"
weight: 2
toc: true
---

## What it is
Breadth-first search (BFS) and depth-first search (DFS) are the two fundamental strategies for visiting every vertex reachable from a source in a graph. BFS explores level by level using a queue, while DFS plunges as deep as possible using recursion or an explicit stack.

## How it works
BFS starts at a source vertex, marks it visited, and enqueues it; it repeatedly dequeues a vertex, enqueues its unvisited neighbors, and marks them. This produces shortest paths in unweighted graphs. DFS marks a vertex, then recursively visits one unvisited neighbor at a time, backtracking when stuck; a stack-based version mirrors the recursion. Both run in O(V+E) time on an adjacency-list graph.

```java
import java.util.*;

public class Traversals {
    public static List<Integer> bfs(List<List<Integer>> adj, int start) {
        List<Integer> order = new ArrayList<>();
        boolean[] visited = new boolean[adj.size()];
        Deque<Integer> queue = new ArrayDeque<>();
        visited[start] = true;
        queue.add(start);
        while (!queue.isEmpty()) {
            int u = queue.poll();
            order.add(u);
            for (int v : adj.get(u)) {
                if (!visited[v]) {
                    visited[v] = true;
                    queue.add(v);
                }
            }
        }
        return order;
    }

    public static List<Integer> dfs(List<List<Integer>> adj, int start) {
        List<Integer> order = new ArrayList<>();
        boolean[] visited = new boolean[adj.size()];
        Deque<Integer> stack = new ArrayDeque<>();
        stack.push(start);
        while (!stack.isEmpty()) {
            int u = stack.pop();
            if (visited[u]) continue;
            visited[u] = true;
            order.add(u);
            for (int v : adj.get(u)) {
                if (!visited[v]) stack.push(v);
            }
        }
        return order;
    }
}
```

```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct Node { int vertex; struct Node* next; } Node;

void addEdge(Node** adj, int u, int v) {
    Node* n = malloc(sizeof(Node));
    n->vertex = v;
    n->next = adj[u];
    adj[u] = n;
}

void bfs(Node** adj, int n, int start, int* order, int* count) {
    bool* visited = calloc(n, sizeof(bool));
    int* queue = malloc(n * sizeof(int));
    int head = 0, tail = 0;
    visited[start] = true;
    queue[tail++] = start;
    while (head < tail) {
        int u = queue[head++];
        order[(*count)++] = u;
        for (Node* cur = adj[u]; cur; cur = cur->next) {
            if (!visited[cur->vertex]) {
                visited[cur->vertex] = true;
                queue[tail++] = cur->vertex;
            }
        }
    }
    free(visited);
    free(queue);
}

void dfsRec(Node** adj, int u, bool* visited, int* order, int* count) {
    visited[u] = true;
    order[(*count)++] = u;
    for (Node* cur = adj[u]; cur; cur = cur->next) {
        if (!visited[cur->vertex]) dfsRec(adj, cur->vertex, visited, order, count);
    }
}

void dfs(Node** adj, int n, int start, int* order, int* count) {
    bool* visited = calloc(n, sizeof(bool));
    dfsRec(adj, start, visited, order, count);
    free(visited);
}
```

```python
from collections import deque
from typing import List


def bfs(adj: List[List[int]], start: int) -> List[int]:
    order: List[int] = []
    visited = [False] * len(adj)
    queue: deque[int] = deque([start])
    visited[start] = True
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                queue.append(v)
    return order


def dfs(adj: List[List[int]], start: int) -> List[int]:
    order: List[int] = []
    visited = [False] * len(adj)
    stack = [start]
    while stack:
        u = stack.pop()
        if visited[u]:
            continue
        visited[u] = True
        order.append(u)
        for v in adj[u]:
            if not visited[v]:
                stack.append(v)
    return order
```

```rust
use std::collections::VecDeque;

pub fn bfs(adj: &[Vec<usize>], start: usize) -> Vec<usize> {
    let mut order = Vec::new();
    let mut visited = vec![false; adj.len()];
    let mut queue = VecDeque::new();
    visited[start] = true;
    queue.push_back(start);
    while let Some(u) = queue.pop_front() {
        order.push(u);
        for &v in &adj[u] {
            if !visited[v] {
                visited[v] = true;
                queue.push_back(v);
            }
        }
    }
    order
}

pub fn dfs(adj: &[Vec<usize>], start: usize) -> Vec<usize> {
    let mut order = Vec::new();
    let mut visited = vec![false; adj.len()];
    let mut stack = vec![start];
    while let Some(u) = stack.pop() {
        if visited[u] {
            continue;
        }
        visited[u] = true;
        order.push(u);
        for &v in &adj[u] {
            if !visited[v] {
                stack.push(v);
            }
        }
    }
    order
}
```

```typescript
export function bfs(adj: number[][], start: number): number[] {
  const order: number[] = [];
  const visited: boolean[] = new Array(adj.length).fill(false);
  const queue: number[] = [start];
  visited[start] = true;
  while (queue.length > 0) {
    const u = queue.shift()!;
    order.push(u);
    for (const v of adj[u]) {
      if (!visited[v]) {
        visited[v] = true;
        queue.push(v);
      }
    }
  }
  return order;
}

export function dfs(adj: number[][], start: number): number[] {
  const order: number[] = [];
  const visited: boolean[] = new Array(adj.length).fill(false);
  const stack: number[] = [start];
  while (stack.length > 0) {
    const u = stack.pop()!;
    if (visited[u]) continue;
    visited[u] = true;
    order.push(u);
    for (const v of adj[u]) {
      if (!visited[v]) stack.push(v);
    }
  }
  return order;
}
```

```go
package main

func BFS(adj [][]int, start int) []int {
	var order []int
	visited := make([]bool, len(adj))
	queue := []int{start}
	visited[start] = true
	for len(queue) > 0 {
		u := queue[0]
		queue = queue[1:]
		order = append(order, u)
		for _, v := range adj[u] {
			if !visited[v] {
				visited[v] = true
				queue = append(queue, v)
			}
		}
	}
	return order
}

func DFS(adj [][]int, start int) []int {
	var order []int
	visited := make([]bool, len(adj))
	stack := []int{start}
	for len(stack) > 0 {
		u := stack[len(stack)-1]
		stack = stack[:len(stack)-1]
		if visited[u] {
			continue
		}
		visited[u] = true
		order = append(order, u)
		for _, v := range adj[u] {
			if !visited[v] {
				stack = append(stack, v)
			}
		}
	}
	return order
}
```

## Complexity
| Algorithm | Time | Space |
| --- | --- | --- |
| BFS (adjacency list) | O(V+E) | O(V) |
| DFS (adjacency list) | O(V+E) | O(V) |
| BFS (adjacency matrix) | O(V²) | O(V) |
| DFS (adjacency matrix) | O(V²) | O(V) |

## When to use
- Use BFS to find shortest paths in unweighted graphs and to explore level by level (e.g., web crawling, nearest-neighbor search).
- Use DFS to detect cycles, compute connected components, and drive topological sort or backtracking searches.
- Use either to check reachability, bipartiteness (BFS coloring), or enumerate components of a graph.

## Alternatives
- Iterative deepening DFS — depth-limited DFS that preserves DFS's memory advantage while finding shallowest goals, at the cost of revisiting nodes.
- Bidirectional BFS — halves the search radius for shortest paths by meeting in the middle, but needs a defined target.
- A* — a heuristic-driven best-first search that reaches a goal faster than BFS, but requires an admissible heuristic.

## Related
- [Graph Representations](01-graph-representations.md)
- [Topological Sort and Strongly Connected Components](03-topological-sort-scc.md)
- [Minimum Spanning Trees](04-minimum-spanning-trees.md)
- [Memory Works (Templates)](../../00-essentials/06-memory-works-templates.md)
