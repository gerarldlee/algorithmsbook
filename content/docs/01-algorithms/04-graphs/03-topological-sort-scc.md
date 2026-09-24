---
title: "Topological Sort and Strongly Connected Components"
weight: 3
toc: true
---

## What it is
Topological sort orders the vertices of a directed acyclic graph (DAG) so that every edge points from an earlier to a later vertex. Strongly connected components (SCCs) are maximal subgraphs in which every vertex is reachable from every other vertex, computable via Tarjan's or Kosaraju's algorithm.

## How it works
Topological sort runs DFS and pushes each vertex onto a stack after all its descendants are finished; popping the stack yields a valid order (or Kahn's algorithm peels off vertices with in-degree zero). SCCs use DFS finishing times (Kosaraju) or a low-link value maintained during a single DFS (Tarjan) to group mutually reachable vertices. Both run in O(V+E).

```java
import java.util.*;

public class TopoSCC {
    // Kahn's algorithm for topological sort
    public static List<Integer> topoSort(List<List<Integer>> adj) {
        int n = adj.size();
        int[] indegree = new int[n];
        for (List<Integer> edges : adj)
            for (int v : edges) indegree[v]++;
        Deque<Integer> queue = new ArrayDeque<>();
        for (int i = 0; i < n; i++)
            if (indegree[i] == 0) queue.add(i);
        List<Integer> order = new ArrayList<>();
        while (!queue.isEmpty()) {
            int u = queue.poll();
            order.add(u);
            for (int v : adj.get(u))
                if (--indegree[v] == 0) queue.add(v);
        }
        return order.size() == n ? order : Collections.emptyList(); // cycle if shorter
    }

    // Tarjan's SCC
    static int index = 0;
    static int[] disc, low;
    static boolean[] onStack;
    static Deque<Integer> stack;
    static List<List<Integer>> sccs;

    public static List<List<Integer>> tarjan(List<List<Integer>> adj) {
        int n = adj.size();
        disc = new int[n]; low = new int[n];
        Arrays.fill(disc, -1);
        onStack = new boolean[n];
        stack = new ArrayDeque<>();
        sccs = new ArrayList<>();
        index = 0;
        for (int i = 0; i < n; i++)
            if (disc[i] == -1) strongConnect(adj, i);
        return sccs;
    }

    private static void strongConnect(List<List<Integer>> adj, int u) {
        disc[u] = low[u] = index++;
        stack.push(u);
        onStack[u] = true;
        for (int v : adj.get(u)) {
            if (disc[v] == -1) {
                strongConnect(adj, v);
                low[u] = Math.min(low[u], low[v]);
            } else if (onStack[v]) {
                low[u] = Math.min(low[u], disc[v]);
            }
        }
        if (low[u] == disc[u]) {
            List<Integer> comp = new ArrayList<>();
            int w;
            do {
                w = stack.pop();
                onStack[w] = false;
                comp.add(w);
            } while (w != u);
            sccs.add(comp);
        }
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
    n->vertex = v; n->next = adj[u]; adj[u] = n;
}

// Kahn's algorithm for topological sort
int topoSort(Node** adj, int n, int* order) {
    int* indegree = calloc(n, sizeof(int));
    for (int u = 0; u < n; u++)
        for (Node* cur = adj[u]; cur; cur = cur->next) indegree[cur->vertex]++;
    int* queue = malloc(n * sizeof(int));
    int head = 0, tail = 0, count = 0;
    for (int i = 0; i < n; i++)
        if (indegree[i] == 0) queue[tail++] = i;
    while (head < tail) {
        int u = queue[head++];
        order[count++] = u;
        for (Node* cur = adj[u]; cur; cur = cur->next)
            if (--indegree[cur->vertex] == 0) queue[tail++] = cur->vertex;
    }
    free(indegree); free(queue);
    return count == n; // 0 means cycle
}

// Tarjan's SCC
static int idx;
static int* disc; static int* low; static bool* onStack;
static int* stack; static int top;
static int* compOf;

static void strongConnect(Node** adj, int u) {
    disc[u] = low[u] = idx++;
    stack[top++] = u; onStack[u] = true;
    for (Node* cur = adj[u]; cur; cur = cur->next) {
        int v = cur->vertex;
        if (disc[v] == -1) {
            strongConnect(adj, v);
            if (low[v] < low[u]) low[u] = low[v];
        } else if (onStack[v] && disc[v] < low[u]) {
            low[u] = disc[v];
        }
    }
    if (low[u] == disc[u]) {
        while (1) {
            int w = stack[--top];
            onStack[w] = false;
            compOf[w] = u;
            if (w == u) break;
        }
    }
}

int tarjan(Node** adj, int n, int* comp) {
    idx = 0;
    disc = calloc(n, sizeof(int));
    low = calloc(n, sizeof(int));
    onStack = calloc(n, sizeof(bool));
    stack = malloc(n * sizeof(int));
    compOf = comp;
    top = 0;
    for (int i = 0; i < n; i++) disc[i] = -1;
    for (int i = 0; i < n; i++)
        if (disc[i] == -1) strongConnect(adj, i);
    free(disc); free(low); free(onStack); free(stack);
    return idx;
}
```

```python
from collections import deque
from typing import List


def topo_sort(adj: List[List[int]]) -> List[int]:
    n = len(adj)
    indegree = [0] * n
    for edges in adj:
        for v in edges:
            indegree[v] += 1
    queue: deque[int] = deque(i for i in range(n) if indegree[i] == 0)
    order: List[int] = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in adj[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                queue.append(v)
    return order if len(order) == n else []


def tarjan(adj: List[List[int]]) -> List[List[int]]:
    n = len(adj)
    disc = [-1] * n
    low = [0] * n
    on_stack = [False] * n
    stack: List[int] = []
    sccs: List[List[int]] = []
    idx = 0

    def strong_connect(u: int) -> None:
        nonlocal idx
        disc[u] = low[u] = idx
        idx += 1
        stack.append(u)
        on_stack[u] = True
        for v in adj[u]:
            if disc[v] == -1:
                strong_connect(v)
                low[u] = min(low[u], low[v])
            elif on_stack[v]:
                low[u] = min(low[u], disc[v])
        if low[u] == disc[u]:
            comp: List[int] = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                comp.append(w)
                if w == u:
                    break
            sccs.append(comp)

    for i in range(n):
        if disc[i] == -1:
            strong_connect(i)
    return sccs
```

```rust
use std::collections::VecDeque;

pub fn topo_sort(adj: &[Vec<usize>]) -> Vec<usize> {
    let n = adj.len();
    let mut indegree = vec![0usize; n];
    for edges in adj {
        for &v in edges {
            indegree[v] += 1;
        }
    }
    let mut queue: VecDeque<usize> = (0..n).filter(|&i| indegree[i] == 0).collect();
    let mut order = Vec::new();
    while let Some(u) = queue.pop_front() {
        order.push(u);
        for &v in &adj[u] {
            indegree[v] -= 1;
            if indegree[v] == 0 {
                queue.push_back(v);
            }
        }
    }
    if order.len() == n {
        order
    } else {
        Vec::new()
    }
}

pub fn tarjan(adj: &[Vec<usize>]) -> Vec<Vec<usize>> {
    let n = adj.len();
    let mut disc = vec![-1i32; n];
    let mut low = vec![0i32; n];
    let mut on_stack = vec![false; n];
    let mut stack = Vec::new();
    let mut sccs = Vec::new();
    let mut idx = 0i32;

    fn strong_connect(
        u: usize, adj: &[Vec<usize>], disc: &mut Vec<i32>, low: &mut Vec<i32>,
        on_stack: &mut Vec<bool>, stack: &mut Vec<usize>, sccs: &mut Vec<Vec<usize>>, idx: &mut i32,
    ) {
        disc[u] = *idx;
        low[u] = *idx;
        *idx += 1;
        stack.push(u);
        on_stack[u] = true;
        for &v in &adj[u] {
            if disc[v] == -1 {
                strong_connect(v, adj, disc, low, on_stack, stack, sccs, idx);
                low[u] = low[u].min(low[v]);
            } else if on_stack[v] {
                low[u] = low[u].min(disc[v]);
            }
        }
        if low[u] == disc[u] {
            let mut comp = Vec::new();
            loop {
                let w = stack.pop().unwrap();
                on_stack[w] = false;
                comp.push(w);
                if w == u {
                    break;
                }
            }
            sccs.push(comp);
        }
    }

    for i in 0..n {
        if disc[i] == -1 {
            strong_connect(i, adj, &mut disc, &mut low, &mut on_stack, &mut stack, &mut sccs, &mut idx);
        }
    }
    sccs
}
```

```typescript
export function topoSort(adj: number[][]): number[] {
  const n = adj.length;
  const indegree = new Array(n).fill(0);
  for (const edges of adj) {
    for (const v of edges) indegree[v]++;
  }
  const queue: number[] = [];
  for (let i = 0; i < n; i++) if (indegree[i] === 0) queue.push(i);
  const order: number[] = [];
  while (queue.length > 0) {
    const u = queue.shift()!;
    order.push(u);
    for (const v of adj[u]) {
      if (--indegree[v] === 0) queue.push(v);
    }
  }
  return order.length === n ? order : [];
}

export function tarjan(adj: number[][]): number[][] {
  const n = adj.length;
  const disc = new Array(n).fill(-1);
  const low = new Array(n).fill(0);
  const onStack = new Array(n).fill(false);
  const stack: number[] = [];
  const sccs: number[][] = [];
  let idx = 0;

  const strongConnect = (u: number): void => {
    disc[u] = low[u] = idx++;
    stack.push(u);
    onStack[u] = true;
    for (const v of adj[u]) {
      if (disc[v] === -1) {
        strongConnect(v);
        low[u] = Math.min(low[u], low[v]);
      } else if (onStack[v]) {
        low[u] = Math.min(low[u], disc[v]);
      }
    }
    if (low[u] === disc[u]) {
      const comp: number[] = [];
      while (true) {
        const w = stack.pop()!;
        onStack[w] = false;
        comp.push(w);
        if (w === u) break;
      }
      sccs.push(comp);
    }
  };

  for (let i = 0; i < n; i++) {
    if (disc[i] === -1) strongConnect(i);
  }
  return sccs;
}
```

```go
package main

func TopoSort(adj [][]int) []int {
	n := len(adj)
	indegree := make([]int, n)
	for _, edges := range adj {
		for _, v := range edges {
			indegree[v]++
		}
	}
	var queue []int
	for i := 0; i < n; i++ {
		if indegree[i] == 0 {
			queue = append(queue, i)
		}
	}
	var order []int
	for len(queue) > 0 {
		u := queue[0]
		queue = queue[1:]
		order = append(order, u)
		for _, v := range adj[u] {
			indegree[v]--
			if indegree[v] == 0 {
				queue = append(queue, v)
			}
		}
	}
	if len(order) == n {
		return order
	}
	return nil
}

func Tarjan(adj [][]int) [][]int {
	n := len(adj)
	disc := make([]int, n)
	low := make([]int, n)
	onStack := make([]bool, n)
	for i := range disc {
		disc[i] = -1
	}
	var stack []int
	var sccs [][]int
	idx := 0

	var strongConnect func(u int)
	strongConnect = func(u int) {
		disc[u] = idx
		low[u] = idx
		idx++
		stack = append(stack, u)
		onStack[u] = true
		for _, v := range adj[u] {
			if disc[v] == -1 {
				strongConnect(v)
				if low[v] < low[u] {
					low[u] = low[v]
				}
			} else if onStack[v] && disc[v] < low[u] {
				low[u] = disc[v]
			}
		}
		if low[u] == disc[u] {
			var comp []int
			for {
				w := stack[len(stack)-1]
				stack = stack[:len(stack)-1]
				onStack[w] = false
				comp = append(comp, w)
				if w == u {
					break
				}
			}
			sccs = append(sccs, comp)
		}
	}

	for i := 0; i < n; i++ {
		if disc[i] == -1 {
			strongConnect(i)
		}
	}
	return sccs
}
```

## Complexity
| Algorithm | Time | Space |
| --- | --- | --- |
| Topological sort (Kahn / DFS) | O(V+E) | O(V) |
| SCC (Tarjan) | O(V+E) | O(V) |
| SCC (Kosaraju) | O(V+E) | O(V) |

## When to use
- Use topological sort to schedule tasks with dependencies, resolve build order, or detect cycles in a DAG (e.g., course prerequisites, package managers).
- Use SCC to condense a directed graph into a DAG of components, find 2-SAT satisfiability, or analyze mutually reachable groups in a web graph.
- Use Tarjan when you want SCCs in a single DFS; Kosaraju when simplicity matters more than a second pass.

## Alternatives
- Kosaraju's algorithm — two-pass DFS on the graph and its transpose; simpler to implement than Tarjan but needs the reversed graph.
- Kahn's algorithm — iterative in-degree-based topological sort that also detects cycles, versus the DFS post-order approach.
- Condensation graph — compress SCCs into a DAG to run further algorithms, at the cost of an extra condensation pass.

## Related
- [Graph Representations](01-graph-representations.md)
- [Graph Traversals (BFS and DFS)](02-graph-traversals.md)
- [Shortest Paths](05-shortest-paths.md)
- [Memory Works (Templates)](../../00-essentials/06-memory-works-templates.md)
