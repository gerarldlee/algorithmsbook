---
title: "Graph Representations"
weight: 1
toc: true
---

## What it is
A graph is a set of vertices (nodes) connected by edges. It can be directed or undirected, weighted or unweighted, and is the foundation for modeling networks, dependencies, and relationships.

## How it works
A graph is a data structure that's composed of edges (lines connecting one vertex to another) and vertices (nodes).  We could say that an array and a linked list is a graph.

The two canonical representations are the **adjacency matrix** (a V×V grid where cell `[u][v]` holds the edge weight or a boolean) and the **adjacency list** (an array of lists, one per vertex, holding its neighbors). Matrix lookups are O(1) but consume O(V²) space regardless of sparsity; lists use O(V+E) space and iterate neighbors fast, making them the default choice for sparse graphs.

```java
import java.util.*;

public class GraphRepr {
    // Adjacency list
    List<List<Integer>> adj;
    int V;

    public GraphRepr(int v) {
        this.V = v;
        this.adj = new ArrayList<>();
        for (int i = 0; i < v; i++) adj.add(new ArrayList<>());
    }

    public void addEdge(int u, int v, boolean undirected) {
        adj.get(u).add(v);
        if (undirected) adj.get(v).add(u);
    }

    // Adjacency matrix
    int[][] matrix;

    public void buildMatrix(int v) {
        matrix = new int[v][v];
    }

    public void addMatrixEdge(int u, int v, int w) {
        matrix[u][v] = w;
    }
}
```

```c
#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int vertex;
    struct Node* next;
} Node;

typedef struct {
    int V;
    Node** adj; // adjacency list
    int** matrix; // adjacency matrix
} Graph;

Graph* createGraph(int V) {
    Graph* g = malloc(sizeof(Graph));
    g->V = V;
    g->adj = calloc(V, sizeof(Node*));
    g->matrix = calloc(V, sizeof(int*));
    for (int i = 0; i < V; i++) g->matrix[i] = calloc(V, sizeof(int));
    return g;
}

void addEdgeList(Graph* g, int u, int v) {
    Node* n = malloc(sizeof(Node));
    n->vertex = v;
    n->next = g->adj[u];
    g->adj[u] = n;
}

void addEdgeMatrix(Graph* g, int u, int v, int w) {
    g->matrix[u][v] = w;
}

void freeGraph(Graph* g) {
    for (int i = 0; i < g->V; i++) {
        Node* cur = g->adj[i];
        while (cur) { Node* t = cur; cur = cur->next; free(t); }
        free(g->matrix[i]);
    }
    free(g->adj);
    free(g->matrix);
    free(g);
}
```

```python
from collections import defaultdict


class GraphRepr:
    def __init__(self, v: int):
        self.v = v
        # adjacency list
        self.adj = defaultdict(list)
        # adjacency matrix
        self.matrix = [[0] * v for _ in range(v)]

    def add_edge_list(self, u: int, v: int, undirected: bool = False) -> None:
        self.adj[u].append(v)
        if undirected:
            self.adj[v].append(u)

    def add_edge_matrix(self, u: int, v: int, w: int = 1) -> None:
        self.matrix[u][v] = w
```

```rust
use std::collections::HashMap;

#[derive(Default)]
pub struct GraphRepr {
    pub v: usize,
    pub adj: HashMap<usize, Vec<usize>>,
    pub matrix: Vec<Vec<i32>>,
}

impl GraphRepr {
    pub fn new(v: usize) -> Self {
        GraphRepr {
            v,
            adj: HashMap::new(),
            matrix: vec![vec![0; v]; v],
        }
    }

    pub fn add_edge_list(&mut self, u: usize, v: usize, undirected: bool) {
        self.adj.entry(u).or_default().push(v);
        if undirected {
            self.adj.entry(v).or_default().push(u);
        }
    }

    pub fn add_edge_matrix(&mut self, u: usize, v: usize, w: i32) {
        self.matrix[u][v] = w;
    }
}
```

```typescript
export class GraphRepr {
  readonly v: number;
  adj: number[][];
  matrix: number[][];

  constructor(v: number) {
    this.v = v;
    this.adj = Array.from({ length: v }, () => []);
    this.matrix = Array.from({ length: v }, () => Array(v).fill(0));
  }

  addEdgeList(u: number, v: number, undirected = false): void {
    this.adj[u].push(v);
    if (undirected) this.adj[v].push(u);
  }

  addEdgeMatrix(u: number, v: number, w = 1): void {
    this.matrix[u][v] = w;
  }
}
```

```go
package main

type GraphRepr struct {
	V      int
	Adj    [][]int
	Matrix [][]int
}

func NewGraphRepr(v int) *GraphRepr {
	adj := make([][]int, v)
	matrix := make([][]int, v)
	for i := 0; i < v; i++ {
		adj[i] = []int{}
		matrix[i] = make([]int, v)
	}
	return &GraphRepr{V: v, Adj: adj, Matrix: matrix}
}

func (g *GraphRepr) AddEdgeList(u, v int, undirected bool) {
	g.Adj[u] = append(g.Adj[u], v)
	if undirected {
		g.Adj[v] = append(g.Adj[v], u)
	}
}

func (g *GraphRepr) AddEdgeMatrix(u, v, w int) {
	g.Matrix[u][v] = w
}
```

## Complexity
| Representation | Operation | Time | Space |
| --- | --- | --- | --- |
| Adjacency list | add edge | O(1) | O(V+E) |
| Adjacency list | check edge (u,v) | O(deg(u)) | O(V+E) |
| Adjacency list | iterate neighbors | O(deg(u)) | O(V+E) |
| Adjacency matrix | add edge | O(1) | O(V²) |
| Adjacency matrix | check edge (u,v) | O(1) | O(V²) |
| Adjacency matrix | iterate neighbors | O(V) | O(V²) |

## When to use
- Use an adjacency list for sparse graphs (most real-world graphs) to save space and iterate neighbors efficiently.
- Use an adjacency matrix for dense graphs or when constant-time edge-existence checks are needed (e.g., Floyd–Warshall).
- Model relationships like social networks, road maps, dependency graphs, or state machines.

## Alternatives
- Edge list (array of `(u, v, w)` tuples) — most compact, ideal input for Kruskal's algorithm, but slow for neighbor iteration.
- Incidence matrix — generalizes to hypergraphs and multigraphs, but wastes space with mostly-zero cells.
- Compressed sparse row (CSR) — cache-friendly read-only adjacency for static graphs, but expensive to mutate.

## Related
- [Graph Traversals (BFS and DFS)](02-graph-traversals.md)
- [Topological Sort and Strongly Connected Components](03-topological-sort-scc.md)
- [Minimum Spanning Trees](04-minimum-spanning-trees.md)
