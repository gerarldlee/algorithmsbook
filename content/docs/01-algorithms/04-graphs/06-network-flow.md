---
title: "Network Flow"
weight: 6
toc: true
---

## What it is
Network flow models the movement of a commodity through a directed graph with capacity-constrained edges, from a source to a sink, to maximize total throughput. The maximum flow equals the minimum cut, as stated by the max-flow min-cut theorem.

## How it works
The Edmonds–Karp algorithm repeatedly finds a shortest augmenting path from source to sink using BFS on the residual graph, pushes as much flow as the path's bottleneck capacity allows, and updates residual capacities until no augmenting path remains. This is a specialization of the Ford–Fulkerson method with polynomial guarantees.

```java
import java.util.*;

public class NetworkFlow {
    // Edmonds-Karp: capacity matrix, source s, sink t
    public static int maxFlow(int[][] cap, int s, int t) {
        int n = cap.length;
        int[][] res = new int[n][];
        for (int i = 0; i < n; i++) res[i] = cap[i].clone();
        int[] parent = new int[n];
        int flow = 0;
        while (true) {
            Arrays.fill(parent, -1);
            Deque<Integer> queue = new ArrayDeque<>();
            queue.add(s);
            parent[s] = s;
            while (!queue.isEmpty() && parent[t] == -1) {
                int u = queue.poll();
                for (int v = 0; v < n; v++) {
                    if (parent[v] == -1 && res[u][v] > 0) {
                        parent[v] = u;
                        queue.add(v);
                    }
                }
            }
            if (parent[t] == -1) break;
            int pathFlow = Integer.MAX_VALUE;
            for (int v = t; v != s; v = parent[v]) {
                pathFlow = Math.min(pathFlow, res[parent[v]][v]);
            }
            for (int v = t; v != s; v = parent[v]) {
                res[parent[v]][v] -= pathFlow;
                res[v][parent[v]] += pathFlow;
            }
            flow += pathFlow;
        }
        return flow;
    }
}
```

```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <limits.h>

int maxFlow(int** cap, int n, int s, int t) {
    int** res = malloc(n * sizeof(int*));
    for (int i = 0; i < n; i++) {
        res[i] = malloc(n * sizeof(int));
        for (int j = 0; j < n; j++) res[i][j] = cap[i][j];
    }
    int* parent = malloc(n * sizeof(int));
    int flow = 0;
    while (true) {
        for (int i = 0; i < n; i++) parent[i] = -1;
        int* queue = malloc(n * sizeof(int));
        int head = 0, tail = 0;
        queue[tail++] = s;
        parent[s] = s;
        while (head < tail && parent[t] == -1) {
            int u = queue[head++];
            for (int v = 0; v < n; v++) {
                if (parent[v] == -1 && res[u][v] > 0) {
                    parent[v] = u;
                    queue[tail++] = v;
                }
            }
        }
        free(queue);
        if (parent[t] == -1) break;
        int pathFlow = INT_MAX;
        for (int v = t; v != s; v = parent[v]) {
            int c = res[parent[v]][v];
            if (c < pathFlow) pathFlow = c;
        }
        for (int v = t; v != s; v = parent[v]) {
            res[parent[v]][v] -= pathFlow;
            res[v][parent[v]] += pathFlow;
        }
        flow += pathFlow;
    }
    free(parent);
    for (int i = 0; i < n; i++) free(res[i]);
    free(res);
    return flow;
}
```

```python
from collections import deque
from typing import List


def max_flow(cap: List[List[int]], s: int, t: int) -> int:
    n = len(cap)
    res = [row[:] for row in cap]
    flow = 0
    while True:
        parent = [-1] * n
        queue: deque[int] = deque([s])
        parent[s] = s
        while queue and parent[t] == -1:
            u = queue.popleft()
            for v in range(n):
                if parent[v] == -1 and res[u][v] > 0:
                    parent[v] = u
                    queue.append(v)
        if parent[t] == -1:
            break
        path_flow = float("inf")
        v = t
        while v != s:
            path_flow = min(path_flow, res[parent[v]][v])
            v = parent[v]
        v = t
        while v != s:
            res[parent[v]][v] -= path_flow
            res[v][parent[v]] += path_flow
            v = parent[v]
        flow += path_flow
    return flow
```

```rust
use std::collections::VecDeque;

pub fn max_flow(cap: &[Vec<i32>], s: usize, t: usize) -> i32 {
    let n = cap.len();
    let mut res = cap.to_vec();
    let mut flow = 0;
    loop {
        let mut parent = vec![usize::MAX; n];
        let mut queue = VecDeque::new();
        queue.push_back(s);
        parent[s] = s;
        while let Some(u) = queue.pop_front() {
            if parent[t] != usize::MAX {
                break;
            }
            for v in 0..n {
                if parent[v] == usize::MAX && res[u][v] > 0 {
                    parent[v] = u;
                    queue.push_back(v);
                }
            }
        }
        if parent[t] == usize::MAX {
            break;
        }
        let mut path_flow = i32::MAX;
        let mut v = t;
        while v != s {
            path_flow = path_flow.min(res[parent[v]][v]);
            v = parent[v];
        }
        v = t;
        while v != s {
            res[parent[v]][v] -= path_flow;
            res[v][parent[v]] += path_flow;
            v = parent[v];
        }
        flow += path_flow;
    }
    flow
}
```

```typescript
export function maxFlow(cap: number[][], s: number, t: number): number {
  const n = cap.length;
  const res = cap.map((row) => [...row]);
  let flow = 0;
  while (true) {
    const parent = new Array(n).fill(-1);
    const queue: number[] = [s];
    parent[s] = s;
    while (queue.length > 0 && parent[t] === -1) {
      const u = queue.shift()!;
      for (let v = 0; v < n; v++) {
        if (parent[v] === -1 && res[u][v] > 0) {
          parent[v] = u;
          queue.push(v);
        }
      }
    }
    if (parent[t] === -1) break;
    let pathFlow = Number.MAX_SAFE_INTEGER;
    for (let v = t; v !== s; v = parent[v]) {
      pathFlow = Math.min(pathFlow, res[parent[v]][v]);
    }
    for (let v = t; v !== s; v = parent[v]) {
      res[parent[v]][v] -= pathFlow;
      res[v][parent[v]] += pathFlow;
    }
    flow += pathFlow;
  }
  return flow;
}
```

```go
package main

func maxFlow(cap [][]int, s, t int) int {
	n := len(cap)
	res := make([][]int, n)
	for i := range cap {
		res[i] = append([]int(nil), cap[i]...)
	}
	flow := 0
	for {
		parent := make([]int, n)
		for i := range parent {
			parent[i] = -1
		}
		queue := []int{s}
		parent[s] = s
		for len(queue) > 0 && parent[t] == -1 {
			u := queue[0]
			queue = queue[1:]
			for v := 0; v < n; v++ {
				if parent[v] == -1 && res[u][v] > 0 {
					parent[v] = u
					queue = append(queue, v)
				}
			}
		}
		if parent[t] == -1 {
			break
		}
		pathFlow := int(^uint(0) >> 1)
		for v := t; v != s; v = parent[v] {
			if res[parent[v]][v] < pathFlow {
				pathFlow = res[parent[v]][v]
			}
		}
		for v := t; v != s; v = parent[v] {
			res[parent[v]][v] -= pathFlow
			res[v][parent[v]] += pathFlow
		}
		flow += pathFlow
	}
	return flow
}
```

## Complexity
| Algorithm | Time | Space |
| --- | --- | --- |
| Edmonds-Karp (max flow) | O(V·E²) | O(V+E) |
| Ford-Fulkerson (generic) | O(E·f*) (pseudo-polynomial) | O(V+E) |
| Dinic's algorithm | O(V²·E) | O(V+E) |

## When to use
- Use max flow for bipartite matching (e.g., assigning jobs to workers), where each worker-job edge has unit capacity.
- Model resource allocation, transportation/evacuation planning, and network throughput problems as flow networks.
- Use the min-cut result to find bottlenecks, image segmentation, or reliability of a network.

## Alternatives
- Dinic's algorithm — faster layered blocking-flow approach (O(V²·E)); preferred over Edmonds–Karp for large graphs.
- Push-relabel — maintains preflows and heights for near O(V³) practical performance, but more complex to implement.
- Bipartite matching via Hopcroft–Karp — specialized O(E√V) matching, faster than generic flow for that specific problem.

## Related
- [Graph Representations](01-graph-representations.md)
- [Graph Traversals (BFS and DFS)](02-graph-traversals.md)
- [Shortest Paths](05-shortest-paths.md)
