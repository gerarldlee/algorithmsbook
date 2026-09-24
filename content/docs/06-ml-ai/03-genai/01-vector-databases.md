---
title: "Vector Databases"
weight: 1
toc: true
---

## What it is
A vector database stores **embeddings** — high-dimensional floating-point vectors produced by an embedding model — and answers *approximate nearest-neighbor* (ANN) queries: given a query vector, return the vectors most similar to it. Instead of a linear scan, it builds an index (graph, inverted list, or quantized tree) that trades a little recall for orders-of-magnitude faster search over billions of vectors.

## How it works
Embeddings map text, images, or audio into dense vectors where **similarity** is a distance: **cosine** (angle), **L2/Euclidean** (straight-line), or **inner product** (dot). The two dominant ANN indexes are **HNSW** (Hierarchical Navigable Small World) and **IVF-PQ**:

- **HNSW** builds a layered proximity graph. Each vector is a node with edges to a few nearby vectors; a greedy walk from an entry point hops across edges toward the query until it reaches a local minimum, and the collected candidates are returned. Higher layers are sparse "highways" that jump across the space, lower layers refine the result.
- **IVF-PQ** clusters vectors into `nlist` inverted-list cells via k-means, then **product quantization (PQ)** compresses each residual vector into a short code. Search probes only the few nearest cells and reconstructs distances from the codes, shrinking memory drastically.

The code below sketches HNSW-style graph construction and greedy search: `insert` walks greedily from the entry node to the nearest neighbor and links the new node to it, and `search` repeats that walk for a query.

```java
import java.util.ArrayList;
import java.util.List;

class HNSW {
    static class Node {
        double[] vec;
        List<Integer> neighbors = new ArrayList<>();
        Node(double[] vec) { this.vec = vec; }
    }

    private final List<Node> nodes = new ArrayList<>();

    double distance(double[] a, double[] b) {                 // L2 distance
        double s = 0;
        for (int i = 0; i < a.length; i++) {
            double d = a[i] - b[i];
            s += d * d;
        }
        return Math.sqrt(s);
    }

    int insert(double[] vec) {                                // graph construction
        int id = nodes.size();
        nodes.add(new Node(vec));
        if (id == 0) return id;
        int nearest = search(vec);                            // greedy walk from entry 0
        nodes.get(id).neighbors.add(nearest);
        nodes.get(nearest).neighbors.add(id);
        return id;
    }

    int search(double[] query) {                              // greedy search
        int cur = 0;                                          // entry node
        double best = distance(nodes.get(cur).vec, query);
        boolean improved = true;
        while (improved) {
            improved = false;
            for (int nb : nodes.get(cur).neighbors) {
                double d = distance(nodes.get(nb).vec, query);
                if (d < best) { best = d; cur = nb; improved = true; }
            }
        }
        return cur;
    }
}
```

```c
#include <stdlib.h>
#include <math.h>

#define MAX_NODES      1024
#define MAX_NEIGHBORS  32
#define DIM            128

typedef struct {
    double vec[DIM];
    int neighbors[MAX_NEIGHBORS];
    int n_neighbors;
} Node;

typedef struct {
    Node nodes[MAX_NODES];
    int count;
} HNSW;

double distance(const double *a, const double *b) {           /* L2 distance */
    double s = 0;
    for (int i = 0; i < DIM; i++) {
        double d = a[i] - b[i];
        s += d * d;
    }
    return sqrt(s);
}

int hnsw_search(HNSW *g, const double *query) {               /* greedy search */
    int cur = 0;                                              /* entry node */
    double best = distance(g->nodes[cur].vec, query);
    int improved = 1;
    while (improved) {
        improved = 0;
        Node *n = &g->nodes[cur];
        for (int i = 0; i < n->n_neighbors; i++) {
            int nb = n->neighbors[i];
            double d = distance(g->nodes[nb].vec, query);
            if (d < best) { best = d; cur = nb; improved = 1; }
        }
    }
    return cur;
}

int hnsw_insert(HNSW *g, const double *vec) {                 /* graph construction */
    int id = g->count++;
    for (int i = 0; i < DIM; i++) g->nodes[id].vec[i] = vec[i];
    g->nodes[id].n_neighbors = 0;
    if (id == 0) return id;
    int nearest = hnsw_search(g, vec);
    Node *a = &g->nodes[id];
    Node *b = &g->nodes[nearest];
    a->neighbors[a->n_neighbors++] = nearest;
    b->neighbors[b->n_neighbors++] = id;
    return id;
}
```

```python
import math

class Node:
    def __init__(self, vec):
        self.vec = vec
        self.neighbors = []

class HNSW:
    def __init__(self):
        self.nodes = []

    @staticmethod
    def distance(a, b):                        # L2 distance
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    def insert(self, vec):                     # graph construction
        node_id = len(self.nodes)
        self.nodes.append(Node(vec))
        if node_id == 0:
            return node_id
        nearest = self.search(vec)             # greedy walk from entry 0
        self.nodes[node_id].neighbors.append(nearest)
        self.nodes[nearest].neighbors.append(node_id)
        return node_id

    def search(self, query):                   # greedy search
        cur = 0                                # entry node
        best = self.distance(self.nodes[cur].vec, query)
        improved = True
        while improved:
            improved = False
            for nb in self.nodes[cur].neighbors:
                d = self.distance(self.nodes[nb].vec, query)
                if d < best:
                    best, cur, improved = d, nb, True
        return cur
```

```rust
struct Node {
    vec: Vec<f32>,
    neighbors: Vec<usize>,
}

struct Hnsw {
    nodes: Vec<Node>,
}

impl Hnsw {
    fn new() -> Self {
        Hnsw { nodes: Vec::new() }
    }

    fn distance(a: &[f32], b: &[f32]) -> f32 {         // L2 distance
        a.iter().zip(b).map(|(x, y)| (x - y).powi(2)).sum::<f32>().sqrt()
    }

    fn insert(&mut self, vec: Vec<f32>) -> usize {      // graph construction
        let id = self.nodes.len();
        self.nodes.push(Node { vec, neighbors: Vec::new() });
        if id == 0 {
            return id;
        }
        let nearest = self.search(&self.nodes[id].vec.clone()); // greedy walk
        self.nodes[id].neighbors.push(nearest);
        self.nodes[nearest].neighbors.push(id);
        id
    }

    fn search(&self, query: &[f32]) -> usize {          // greedy search
        let mut cur = 0;                                // entry node
        let mut best = Self::distance(&self.nodes[cur].vec, query);
        let mut improved = true;
        while improved {
            improved = false;
            for &nb in &self.nodes[cur].neighbors {
                let d = Self::distance(&self.nodes[nb].vec, query);
                if d < best {
                    best = d;
                    cur = nb;
                    improved = true;
                }
            }
        }
        cur
    }
}
```

```typescript
interface Node {
    vec: number[];
    neighbors: number[];
}

class HNSW {
    private nodes: Node[] = [];

    private distance(a: number[], b: number[]): number {  // L2 distance
        let s = 0;
        for (let i = 0; i < a.length; i++) {
            const d = a[i] - b[i];
            s += d * d;
        }
        return Math.sqrt(s);
    }

    insert(vec: number[]): number {                      // graph construction
        const id = this.nodes.length;
        this.nodes.push({ vec, neighbors: [] });
        if (id === 0) return id;
        const nearest = this.search(vec);                // greedy walk from entry 0
        this.nodes[id].neighbors.push(nearest);
        this.nodes[nearest].neighbors.push(id);
        return id;
    }

    search(query: number[]): number {                    // greedy search
        let cur = 0;                                     // entry node
        let best = this.distance(this.nodes[cur].vec, query);
        let improved = true;
        while (improved) {
            improved = false;
            for (const nb of this.nodes[cur].neighbors) {
                const d = this.distance(this.nodes[nb].vec, query);
                if (d < best) { best = d; cur = nb; improved = true; }
            }
        }
        return cur;
    }
}
```

```go
package main

import "math"

type Node struct {
	vec       []float64
	neighbors []int
}

type HNSW struct {
	nodes []*Node
}

func distance(a, b []float64) float64 { // L2 distance
	s := 0.0
	for i := range a {
		d := a[i] - b[i]
		s += d * d
	}
	return math.Sqrt(s)
}

func (h *HNSW) Insert(vec []float64) int { // graph construction
	id := len(h.nodes)
	h.nodes = append(h.nodes, &Node{vec: vec})
	if id == 0 {
		return id
	}
	nearest := h.Search(vec) // greedy walk from entry 0
	h.nodes[id].neighbors = append(h.nodes[id].neighbors, nearest)
	h.nodes[nearest].neighbors = append(h.nodes[nearest].neighbors, id)
	return id
}

func (h *HNSW) Search(query []float64) int { // greedy search
	cur := 0 // entry node
	best := distance(h.nodes[cur].vec, query)
	improved := true
	for improved {
		improved = false
		for _, nb := range h.nodes[cur].neighbors {
			d := distance(h.nodes[nb].vec, query)
			if d < best {
				best, cur, improved = d, nb, true
			}
		}
	}
	return cur
}
```

## Tradeoffs

| Aspect | Notes |
| --- | --- |
| Recall vs. latency | Approximate search trades a small recall loss for huge speed gains over exact k-NN |
| Index time | HNSW builds fast but graph construction is memory-heavy; IVF-PQ needs a clustering pass |
| Memory | HNSW stores full vectors plus graph; IVF-PQ compresses vectors to short codes (far less RAM) |
| Filtering | Metadata/boolean filters are hard to combine with ANN graphs without dropping recall |
| Freshness | New vectors require index maintenance; strong consistency adds write latency |

## When to use
- Semantic search and recommendation over embeddings where exact matches are not required.
- RAG pipelines that must fetch relevant passages quickly for an LLM.
- Image/audio similarity and deduplication at scale (hundreds of millions of vectors).

## Alternatives
- **Exact k-NN scan (numpy/FAISS flat)** — perfect recall, but O(n) per query and impractical at scale.
- **Locality-sensitive hashing (LSH)** — hashes similar vectors into the same buckets, but recall is noisier than HNSW.
- **Full-text search (BM25)** — keyword matching with no embeddings, but misses semantic similarity.

## Related
- [Retrieval-Augmented Generation (RAG)](02-rag.md)
- [LLM Serving](04-llm-serving.md)
- [Unsupervised Learning](../01-ml-foundations/02-unsupervised-learning.md)
- [Transformers](../01-ml-foundations/05-transformers.md)
