---
title: "Graph Traversals: Breadth-First Search (BFS) and Depth-First Search (DFS)"
weight: 2
toc: true
---

## What it is
**Breadth-first search (BFS)** visits a graph in distance layers from a source, while **depth-first search (DFS)** follows each path as far as possible before backtracking.

## How it works
BFS marks the source, enqueues it, and repeatedly removes the oldest vertex before marking and enqueueing its undiscovered neighbors. DFS marks each vertex when it is removed from an explicit stack, then adds its undiscovered neighbors. The examples use the same explicit-stack DFS across languages; adjacency order can change the traversal order without changing its reachability or cycle-detection semantics.

```java
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

public final class GraphTraversals {
    private GraphTraversals() {}

    public static List<Integer> bfs(List<List<Integer>> adjacency, int start) {
        List<Integer> order = new ArrayList<>();
        boolean[] visited = new boolean[adjacency.size()];
        Deque<Integer> queue = new ArrayDeque<>();
        visited[start] = true;
        queue.add(start);
        while (!queue.isEmpty()) {
            int vertex = queue.removeFirst();
            order.add(vertex);
            for (int neighbor : adjacency.get(vertex)) {
                if (!visited[neighbor]) {
                    visited[neighbor] = true;
                    queue.addLast(neighbor);
                }
            }
        }
        return order;
    }

    public static List<Integer> dfs(List<List<Integer>> adjacency, int start) {
        List<Integer> order = new ArrayList<>();
        boolean[] visited = new boolean[adjacency.size()];
        Deque<Integer> stack = new ArrayDeque<>();
        stack.push(start);
        while (!stack.isEmpty()) {
            int vertex = stack.pop();
            if (visited[vertex]) continue;
            visited[vertex] = true;
            order.add(vertex);
            for (int neighbor : adjacency.get(vertex)) {
                if (!visited[neighbor]) stack.push(neighbor);
            }
        }
        return order;
    }
}
```

```c
#include <stdbool.h>
#include <stdlib.h>

typedef struct Node {
    int vertex;
    struct Node* next;
} Node;

int graph_traversals_bfs(Node** adjacency, int vertex_count, int start, int* order) {
    bool* visited = calloc(vertex_count, sizeof(bool));
    int* queue = malloc(vertex_count * sizeof(int));
    int head = 0;
    int tail = 0;
    int count = 0;
    visited[start] = true;
    queue[tail++] = start;
    while (head < tail) {
        int vertex = queue[head++];
        order[count++] = vertex;
        for (Node* node = adjacency[vertex]; node; node = node->next) {
            if (!visited[node->vertex]) {
                visited[node->vertex] = true;
                queue[tail++] = node->vertex;
            }
        }
    }
    free(visited);
    free(queue);
    return count;
}

int graph_traversals_dfs(Node** adjacency, int vertex_count, int start, int* order) {
    bool* visited = calloc(vertex_count, sizeof(bool));
    int* stack = malloc(vertex_count * sizeof(int));
    int size = 0;
    int capacity = vertex_count;
    int count = 0;
    stack[size++] = start;
    while (size > 0) {
        int vertex = stack[--size];
        if (visited[vertex]) continue;
        visited[vertex] = true;
        order[count++] = vertex;
        for (Node* node = adjacency[vertex]; node; node = node->next) {
            if (!visited[node->vertex]) {
                if (size == capacity) {
                    capacity *= 2;
                    stack = realloc(stack, capacity * sizeof(int));
                }
                stack[size++] = node->vertex;
            }
        }
    }
    free(visited);
    free(stack);
    return count;
}
```

```python
from collections import deque


class GraphTraversals:
    @staticmethod
    def bfs(adjacency: list[list[int]], start: int) -> list[int]:
        order: list[int] = []
        visited = [False] * len(adjacency)
        queue = deque([start])
        visited[start] = True
        while queue:
            vertex = queue.popleft()
            order.append(vertex)
            for neighbor in adjacency[vertex]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    queue.append(neighbor)
        return order

    @staticmethod
    def dfs(adjacency: list[list[int]], start: int) -> list[int]:
        order: list[int] = []
        visited = [False] * len(adjacency)
        stack = [start]
        while stack:
            vertex = stack.pop()
            if visited[vertex]:
                continue
            visited[vertex] = True
            order.append(vertex)
            for neighbor in adjacency[vertex]:
                if not visited[neighbor]:
                    stack.append(neighbor)
        return order
```

```rust
use std::collections::VecDeque;

pub struct GraphTraversals;

impl GraphTraversals {
    pub fn bfs(adjacency: &[Vec<usize>], start: usize) -> Vec<usize> {
        let mut order = Vec::new();
        let mut visited = vec![false; adjacency.len()];
        let mut queue = VecDeque::new();
        visited[start] = true;
        queue.push_back(start);
        while let Some(vertex) = queue.pop_front() {
            order.push(vertex);
            for &neighbor in &adjacency[vertex] {
                if !visited[neighbor] {
                    visited[neighbor] = true;
                    queue.push_back(neighbor);
                }
            }
        }
        order
    }

    pub fn dfs(adjacency: &[Vec<usize>], start: usize) -> Vec<usize> {
        let mut order = Vec::new();
        let mut visited = vec![false; adjacency.len()];
        let mut stack = vec![start];
        while let Some(vertex) = stack.pop() {
            if visited[vertex] {
                continue;
            }
            visited[vertex] = true;
            order.push(vertex);
            for &neighbor in &adjacency[vertex] {
                if !visited[neighbor] {
                    stack.push(neighbor);
                }
            }
        }
        order
    }
}
```

```typescript
export class GraphTraversals {
  static bfs(adjacency: number[][], start: number): number[] {
    const order: number[] = [];
    const visited = new Array<boolean>(adjacency.length).fill(false);
    const queue: number[] = [start];
    visited[start] = true;
    while (queue.length > 0) {
      const vertex = queue.shift()!;
      order.push(vertex);
      for (const neighbor of adjacency[vertex]) {
        if (!visited[neighbor]) {
          visited[neighbor] = true;
          queue.push(neighbor);
        }
      }
    }
    return order;
  }

  static dfs(adjacency: number[][], start: number): number[] {
    const order: number[] = [];
    const visited = new Array<boolean>(adjacency.length).fill(false);
    const stack: number[] = [start];
    while (stack.length > 0) {
      const vertex = stack.pop()!;
      if (visited[vertex]) continue;
      visited[vertex] = true;
      order.push(vertex);
      for (const neighbor of adjacency[vertex]) {
        if (!visited[neighbor]) stack.push(neighbor);
      }
    }
    return order;
  }
}
```

```go
package graph

type GraphTraversals struct{}

func (GraphTraversals) BFS(adjacency [][]int, start int) []int {
	order := []int{}
	visited := make([]bool, len(adjacency))
	queue := []int{start}
	visited[start] = true
	for len(queue) > 0 {
		vertex := queue[0]
		queue = queue[1:]
		order = append(order, vertex)
		for _, neighbor := range adjacency[vertex] {
			if !visited[neighbor] {
				visited[neighbor] = true
				queue = append(queue, neighbor)
			}
		}
	}
	return order
}

func (GraphTraversals) DFS(adjacency [][]int, start int) []int {
    order := []int{}
    visited := make([]bool, len(adjacency))
    stack := []int{start}
    for len(stack) > 0 {
        vertex := stack[len(stack)-1]
        stack = stack[:len(stack)-1]
        if visited[vertex] {
            continue
        }
        visited[vertex] = true
        order = append(order, vertex)
        for _, neighbor := range adjacency[vertex] {
            if !visited[neighbor] {
                stack = append(stack, neighbor)
            }
        }
    }
    return order
}
```

## Complexity
For \(V\) vertices and \(E\) edges:

| Algorithm and representation | Time | Extra space |
| --- | --- | --- |
| BFS with adjacency lists | O(V+E) | O(V) |
| DFS with adjacency lists and an explicit stack | O(V+E) | O(V+E) worst case |
| BFS with an adjacency matrix | O(V²) | O(V) |
| DFS with an adjacency matrix | O(V²) | O(V+E) worst case |

## When to use
- You need shortest paths in an unweighted graph or level-by-level exploration.
- You need reachability, connected components, or bipartite checks.
- You need cycle detection, finish times, or backtracking state.
- You need to traverse a large implicit graph without storing every edge.

## Alternatives
- **A*** — expands promising states toward a known goal, but requires an admissible heuristic for shortest-path guarantees.
- **Bidirectional BFS** — searches from both endpoints, which is useful for one known target but not arbitrary reachability.
- **Iterative-deepening DFS** — explores increasing depth limits with linear working memory, but repeats work and costs more time.

## Related
- [Graph Representations (Adjacency Matrix, Adjacency List, Edge List)](01-graph-representations.md)
- [Topological Sorting & Strongly Connected Components (Tarjan’s, Kosaraju’s)](03-topological-sort-scc.md)
- [Minimum Spanning Trees (Kruskal’s, Prim’s Algorithms)](04-minimum-spanning-trees.md)
- [Computational Complexity Theory: P vs NP, NP-Completeness, NP-Hardness, and Polynomial-Time Reductions](../04a-computational-theory/01-complexity-theory.md)
- [Shortest Path Algorithms: Single-Source (Dijkstra’s, Bellman-Ford) & All-Pairs (Floyd-Warshall, Johnson’s)](05-shortest-paths.md)
- [Network Flow & Matching (Ford-Fulkerson, Edmonds-Karp, Dinic’s, Hopcroft-Karp)](06-network-flow.md)
