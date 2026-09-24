---
title: "Vector Databases (Pinecone, Qdrant, Milvus), Similarity Metrics (Cosine, L2, Dot Product), and Approximate Nearest Neighbors (HNSW, IVF-PQ)"
weight: 1
toc: true
tabs: {sync: true}
---

## What it is
A vector database stores numerical embeddings and returns nearest vectors under a declared distance or similarity metric. It adds ANN indexes, payload filters, durability, and distributed placement to the embedding workload that semantic search, recommendation, deduplication, and RAG systems run.

## How it works
An embedding model maps an object to a fixed-width vector. For two vectors `a` and `b`, common metrics define different neighborhoods:

| Metric | Definition | Favor when |
| --- | --- | --- |
| L2 distance | `sqrt(sum((a[i] - b[i])²))` | Magnitude matters, or vectors use a shared scale |
| Cosine similarity | `dot(a, b) / (norm(a) * norm(b))` | Direction matters more than magnitude |
| Dot product | `sum(a[i] * b[i])` | Magnitude is meaningful, as in a learned relevance score |

Cosine similarity is undefined when either vector has zero norm. The six implementations define cosine distance as `1.0` in that case so they can order every candidate without producing `NaN`.

The selected metric must match the embedding model and index. Pinecone provides a managed vector database, while Qdrant and Milvus can run self-hosted; Qdrant is designed around collection and payload configuration, and Milvus separates storage, index nodes, and query nodes in distributed deployments. These product features surround the shared ANN problem.

**HNSW** stores a multi-layer proximity graph. The highest layer starts at a small entry set, and each lower layer expands the search frontier. A best-first walk compares a candidate with its unvisited graph neighbors until the frontier cannot improve, then returns a maintained candidate set. Insertion searches from the top layer downward and connects the new vector in upper and lower layers, with a bidirectional-neighbor heuristic that preserves navigable shortcuts. The number of neighbors considered during search controls the recall and latency trade.

**IVF-PQ** first trains coarse centroids with k-means and assigns each vector to a nearest list, which is the inverted-file step. **Product quantization (PQ)** then splits a residual vector into subvectors, learns a codebook for each subspace, and replaces the residual with one code per subspace. Search probes a small number of nearby lists and estimates distances from compact codes. The index accepts reconstruction and ranking error in exchange for lower storage and bandwidth.

A portable collection manifest captures the decisions an operator must make before choosing a product-specific client configuration:

```yaml
collection: knowledge_chunks
vector:
  dimensions: 768
  distance: cosine
  normalization: model_specific
index:
  type: hnsw
  graph_degree: 32
  construction_candidates: 200
  search_candidates: 64
payload:
  tenant_id: keyword
  source_uri: keyword
  acl_groups: keyword_index
  updated_at: datetime_index
sharding:
  partitions: 16
  replication_factor: 3
consistency:
  write_visibility: acknowledged_primary
search:
  top_k: 20
  filter_before_search: true
  oversampling: 2
  return_payload: [source_uri, chunk_ordinal, acl_groups]
```

Payload and ACL filters are only one retrieval-security layer; they do not authorize a result. The application must bind `tenant_id` and policy context from its authenticated, trusted request rather than client-controlled filter input, filter before candidates leave retrieval, and recheck returned payloads. Missing, stale, or inconsistent tenant or policy state must fail closed before reranking, context assembly, or generation.

The six implementations below are **bounded/unlayered graph baselines**, not HNSW implementations. The shared `BoundedGraph` API uses exact linear L2 nearest-neighbor selection for insertion, prunes each node's neighbors by their L2 distance from that node's vector, maintains a degree bound, and performs an approximate bounded best-first traversal with cosine distance, L2 distance, or negated dot product as a lower-is-better rank. Thus, the example graph is L2-based during construction even when search uses cosine or dot-product ranking; it does not use one shared cosine or dot-product metric for both graph construction and search. The traversal can stop at `maxCandidates` and can omit nearer vectors that remain unreachable through the bounded graph. These implementations intentionally omit layered routing, concurrency, persistence, quantization, and product-specific payload filters so that the graph traversal remains visible. They are teaching baselines, not substitutes for Qdrant, Milvus, Pinecone, or an HNSW library in production.

{{< tabs >}}
{{< tab name="Java" >}}
```java
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.PriorityQueue;
import java.util.Set;

public final class BoundedGraph {
    public enum Metric { COSINE, L2, DOT }

    private static final class Node {
        final int id;
        final double[] vector;
        final List<Integer> neighbors = new ArrayList<>();

        Node(int id, double[] vector) {
            this.id = id;
            this.vector = vector;
        }
    }

    private static final class Candidate {
        final int id;
        final double distance;

        Candidate(int id, double distance) {
            this.id = id;
            this.distance = distance;
        }
    }

    private final int dimensions;
    private final int maxNeighbors;
    private final List<Node> nodes = new ArrayList<>();

    public BoundedGraph(int dimensions, int maxNeighbors) {
        if (dimensions < 1 || maxNeighbors < 1) {
            throw new IllegalArgumentException("dimensions and maxNeighbors must be positive");
        }
        this.dimensions = dimensions;
        this.maxNeighbors = maxNeighbors;
    }

    public void add(int id, double[] vector) {
        validate(vector);
        if (contains(id)) {
            throw new IllegalArgumentException("duplicate id");
        }
        Node node = new Node(id, vector.clone());
        if (nodes.isEmpty()) {
            nodes.add(node);
            return;
        }
        int nearest = nodes.get(0).id;
        double best = rank(vector, nodes.get(0).vector, Metric.L2);
        for (Node candidate : nodes) {
            double distance = rank(vector, candidate.vector, Metric.L2);
            if (distance < best || (distance == best && candidate.id < nearest)) {
                best = distance;
                nearest = candidate.id;
            }
        }
        nodes.add(node);
        connect(id, nearest, Metric.L2);
    }

    public List<Integer> search(double[] query, int k, int maxCandidates, Metric metric) {
        validate(query);
        if (nodes.isEmpty()) {
            return List.of();
        }
        if (k < 1 || maxCandidates < k) {
            throw new IllegalArgumentException("maxCandidates must be at least k and k must be positive");
        }
        PriorityQueue<Candidate> frontier = new PriorityQueue<>(
            Comparator.comparingDouble((Candidate candidate) -> candidate.distance)
                .thenComparingInt(candidate -> candidate.id)
        );
        Set<Integer> visited = new HashSet<>();
        List<Candidate> results = new ArrayList<>();
        int entry = nodes.get(0).id;
        visited.add(entry);
        frontier.add(new Candidate(entry, rank(query, find(entry).vector, metric)));
        while (!frontier.isEmpty()) {
            Candidate current = frontier.poll();
            results.add(current);
            for (int neighbor : find(current.id).neighbors) {
                if (visited.add(neighbor)) {
                    frontier.add(new Candidate(neighbor, rank(query, find(neighbor).vector, metric)));
                }
            }
            if (results.size() == maxCandidates) {
                break;
            }
        }
        results.sort(Comparator.comparingDouble((Candidate candidate) -> candidate.distance)
            .thenComparingInt(candidate -> candidate.id));
        return results.subList(0, Math.min(k, results.size())).stream().map(candidate -> candidate.id).toList();
    }

    private void connect(int left, int right, Metric metric) {
        Node a = find(left);
        Node b = find(right);
        if (!a.neighbors.contains(right)) {
            a.neighbors.add(right);
        }
        if (!b.neighbors.contains(left)) {
            b.neighbors.add(left);
        }
        prune(a, metric);
        prune(b, metric);
    }

    private void prune(Node node, Metric metric) {
        if (node.neighbors.size() <= maxNeighbors) {
            return;
        }
        node.neighbors.sort(Comparator.comparingDouble((Integer id) -> rank(node.vector, find(id).vector, metric))
            .thenComparingInt(id -> id));
        List<Integer> retained = new ArrayList<>(node.neighbors.subList(0, maxNeighbors));
        node.neighbors.clear();
        node.neighbors.addAll(retained);
    }

    private boolean contains(int id) {
        return nodes.stream().anyMatch(node -> node.id == id);
    }

    private Node find(int id) {
        return nodes.stream().filter(node -> node.id == id).findFirst().orElseThrow();
    }

    private void validate(double[] vector) {
        if (vector.length != dimensions) {
            throw new IllegalArgumentException("unexpected vector width");
        }
    }

    private double rank(double[] a, double[] b, Metric metric) {
        double dot = 0;
        double normA = 0;
        double normB = 0;
        for (int i = 0; i < dimensions; i++) {
            dot += a[i] * b[i];
            normA += a[i] * a[i];
            normB += b[i] * b[i];
        }
        return switch (metric) {
            case COSINE -> normA == 0.0 || normB == 0.0 ? 1.0 : 1.0 - dot / Math.sqrt(normA * normB);
            case L2 -> Math.sqrt(Math.max(0.0, normA + normB - 2 * dot));
            case DOT -> -dot;
        };
    }
}
```
{{< /tab >}}
{{< tab name="C" >}}
```c
#include <limits.h>
#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef enum {
    COSINE,
    L2,
    DOT
} Metric;

typedef struct {
    int id;
    double *vector;
    int *neighbors;
    int neighbor_count;
    int neighbor_capacity;
} Node;

typedef struct {
    int dimensions;
    int max_neighbors;
    int count;
    int node_capacity;
    Node *nodes;
} BoundedGraph;

typedef struct {
    int id;
    double distance;
} Candidate;

static double bounded_graph_rank(const double *a, const double *b, int dimensions, Metric metric) {
    double dot = 0;
    double norm_a = 0;
    double norm_b = 0;
    for (int i = 0; i < dimensions; i++) {
        dot += a[i] * b[i];
        norm_a += a[i] * a[i];
        norm_b += b[i] * b[i];
    }
    if (metric == COSINE) return norm_a == 0.0 || norm_b == 0.0 ? 1.0 : 1.0 - dot / sqrt(norm_a * norm_b);
    if (metric == L2) return sqrt(fmax(0.0, norm_a + norm_b - 2.0 * dot));
    return -dot;
}

static const Node *bounded_graph_find_const(const BoundedGraph *index, int id) {
    for (int i = 0; i < index->count; i++) {
        if (index->nodes[i].id == id) return &index->nodes[i];
    }
    return NULL;
}

static Node *bounded_graph_find(BoundedGraph *index, int id) {
    return (Node *)bounded_graph_find_const(index, id);
}

static bool bounded_graph_contains(BoundedGraph *index, int id) {
    return bounded_graph_find(index, id) != NULL;
}

static bool bounded_graph_reserve_node(BoundedGraph *index) {
    if (index->count < index->node_capacity) return true;
    size_t capacity = index->node_capacity == 0 ? 1 : (size_t)index->node_capacity * 2;
    if (capacity > (size_t)INT_MAX || capacity > SIZE_MAX / sizeof(Node)) return false;
    Node *nodes = realloc(index->nodes, capacity * sizeof(Node));
    if (nodes == NULL) return false;
    index->nodes = nodes;
    index->node_capacity = (int)capacity;
    return true;
}

static int bounded_graph_compare(const void *left, const void *right) {
    const Candidate *a = left;
    const Candidate *b = right;
    if (a->distance < b->distance) return -1;
    if (a->distance > b->distance) return 1;
    if (a->id < b->id) return -1;
    if (a->id > b->id) return 1;
    return 0;
}

static bool bounded_graph_before(const BoundedGraph *index, int left, int right, const double *vector, Metric metric) {
    const Node *left_node = bounded_graph_find_const(index, left);
    const Node *right_node = bounded_graph_find_const(index, right);
    double left_distance = bounded_graph_rank(vector, left_node->vector, index->dimensions, metric);
    double right_distance = bounded_graph_rank(vector, right_node->vector, index->dimensions, metric);
    return left_distance < right_distance || (left_distance == right_distance && left < right);
}

static bool bounded_graph_append_neighbor(Node *node, int neighbor_id) {
    for (int i = 0; i < node->neighbor_count; i++) {
        if (node->neighbors[i] == neighbor_id) return true;
    }
    if (node->neighbor_count == node->neighbor_capacity) {
        size_t capacity = node->neighbor_capacity == 0 ? 1 : (size_t)node->neighbor_capacity * 2;
        if (capacity > (size_t)INT_MAX || capacity > SIZE_MAX / sizeof(int)) return false;
        int *resized = realloc(node->neighbors, capacity * sizeof(int));
        if (resized == NULL) return false;
        node->neighbors = resized;
        node->neighbor_capacity = (int)capacity;
    }
    node->neighbors[node->neighbor_count++] = neighbor_id;
    return true;
}

static void bounded_graph_prune(BoundedGraph *index, Node *node, Metric metric) {
    for (int i = 1; i < node->neighbor_count; i++) {
        int current = node->neighbors[i];
        int position = i;
        while (position > 0 && bounded_graph_before(index, node->neighbors[position - 1], current, node->vector, metric)) {
            node->neighbors[position] = node->neighbors[position - 1];
            position--;
        }
        node->neighbors[position] = current;
    }
    if (node->neighbor_count > index->max_neighbors) {
        node->neighbor_count = index->max_neighbors;
    }
}

static bool bounded_graph_validate(const BoundedGraph *index, const double *vector, int width) {
    return index != NULL && index->dimensions > 0 && vector != NULL && width == index->dimensions;
}

static int bounded_graph_add(BoundedGraph *index, int id, const double *vector, int width) {
    if (index == NULL || !bounded_graph_validate(index, vector, width) || index->max_neighbors < 1) return 0;
    if ((size_t)width > SIZE_MAX / sizeof(double)) return 0;
    if (bounded_graph_contains(index, id)) return 0;
    if (!bounded_graph_reserve_node(index)) return 0;
    Node *node = &index->nodes[index->count];
    node->id = id;
    node->vector = malloc((size_t)width * sizeof(double));
    if (node->vector == NULL) return 0;
    memcpy(node->vector, vector, (size_t)width * sizeof(double));
    node->neighbors = NULL;
    node->neighbor_count = 0;
    node->neighbor_capacity = 0;
    int nearest = 0;
    double best = 0;
    if (index->count > 0) {
        Node *entry = &index->nodes[0];
        nearest = entry->id;
        best = bounded_graph_rank(vector, entry->vector, index->dimensions, L2);
        for (int i = 1; i < index->count; i++) {
            double distance = bounded_graph_rank(vector, index->nodes[i].vector, index->dimensions, L2);
            if (distance < best || (distance == best && index->nodes[i].id < nearest)) {
                best = distance;
                nearest = index->nodes[i].id;
            }
        }
    }
    index->count++;
    if (index->count == 1) return 1;
    Node *a = bounded_graph_find(index, id);
    Node *b = bounded_graph_find(index, nearest);
    if (!bounded_graph_append_neighbor(a, nearest) || !bounded_graph_append_neighbor(b, id)) {
        free(a->neighbors);
        free(a->vector);
        index->count--;
        return 0;
    }
    bounded_graph_prune(index, a, L2);
    bounded_graph_prune(index, b, L2);
    return 1;
}

static int bounded_graph_search(BoundedGraph *index, const double *query, int width, int k, int max_candidates, Metric metric, int *ids, int ids_capacity) {
    if (index == NULL || !bounded_graph_validate(index, query, width) || ids == NULL || index->count < 0) return -1;
    if (index->count == 0) return 0;
    if (k < 1 || max_candidates < k || ids_capacity < k) return -1;
    if ((size_t)index->count > SIZE_MAX / sizeof(bool) || (size_t)index->count > SIZE_MAX / sizeof(Candidate) || (size_t)max_candidates > SIZE_MAX / sizeof(Candidate)) return -1;
    bool *visited = calloc((size_t)index->count, sizeof(bool));
    Candidate *frontier = malloc((size_t)index->count * sizeof(Candidate));
    Candidate *results = malloc((size_t)max_candidates * sizeof(Candidate));
    if (visited == NULL || frontier == NULL || results == NULL) {
        free(visited);
        free(frontier);
        free(results);
        return -1;
    }
    int frontier_count = 1;
    int result_count = 0;
    int entry_index = 0;
    int entry_id = index->nodes[entry_index].id;
    visited[entry_index] = true;
    frontier[0].id = entry_id;
    frontier[0].distance = bounded_graph_rank(query, index->nodes[entry_index].vector, index->dimensions, metric);
    while (frontier_count > 0 && result_count < max_candidates) {
        int selected = 0;
        for (int i = 1; i < frontier_count; i++) {
            if (bounded_graph_compare(&frontier[i], &frontier[selected]) < 0) selected = i;
        }
        Candidate current = frontier[selected];
        for (int i = selected + 1; i < frontier_count; i++) frontier[i - 1] = frontier[i];
        frontier_count--;
        results[result_count++] = current;
        Node *node = bounded_graph_find(index, current.id);
        for (int i = 0; i < node->neighbor_count; i++) {
            int neighbor_id = node->neighbors[i];
            int neighbor_index = -1;
            for (int j = 0; j < index->count; j++) {
                if (index->nodes[j].id == neighbor_id) {
                    neighbor_index = j;
                    break;
                }
            }
            if (neighbor_index >= 0 && !visited[neighbor_index]) {
                visited[neighbor_index] = true;
                frontier[frontier_count].id = neighbor_id;
                frontier[frontier_count].distance = bounded_graph_rank(query, index->nodes[neighbor_index].vector, index->dimensions, metric);
                frontier_count++;
            }
        }
    }
    qsort(results, result_count, sizeof(Candidate), bounded_graph_compare);
    int count = result_count < k ? result_count : k;
    for (int i = 0; i < count; i++) ids[i] = results[i].id;
    free(visited);
    free(frontier);
    free(results);
    return count;
}
```
{{< /tab >}}
{{< tab name="Python" >}}
```python
import heapq
import math


class BoundedGraph:
    def __init__(self, dimensions, max_neighbors):
        if not isinstance(dimensions, int) or not isinstance(max_neighbors, int) or dimensions < 1 or max_neighbors < 1:
            raise ValueError("dimensions and max_neighbors must be positive integers")
        self.dimensions = dimensions
        self.max_neighbors = max_neighbors
        self.nodes = {}

    def _rank(self, left, right, metric):
        dot = sum(a * b for a, b in zip(left, right))
        left_norm = math.sqrt(sum(value * value for value in left))
        right_norm = math.sqrt(sum(value * value for value in right))
        if metric == "cosine":
            return 1.0 if left_norm == 0.0 or right_norm == 0.0 else 1.0 - dot / (left_norm * right_norm)
        if metric == "l2":
            return math.sqrt(max(0.0, left_norm * left_norm + right_norm * right_norm - 2.0 * dot))
        return -dot

    def _validate(self, vector):
        if len(vector) != self.dimensions:
            raise ValueError("unexpected vector width")

    def _prune(self, node_id):
        vector = self.nodes[node_id]["vector"]
        neighbors = self.nodes[node_id]["neighbors"]
        neighbors.sort(key=lambda neighbor: (self._rank(vector, self.nodes[neighbor]["vector"], "l2"), neighbor))
        del neighbors[self.max_neighbors:]

    def add(self, vector_id, vector):
        self._validate(vector)
        if vector_id in self.nodes:
            raise ValueError("duplicate id")
        if not self.nodes:
            self.nodes[vector_id] = {"vector": list(vector), "neighbors": []}
            return
        nearest = min(
            self.nodes,
            key=lambda node_id: (self._rank(vector, self.nodes[node_id]["vector"], "l2"), node_id),
        )
        self.nodes[vector_id] = {"vector": list(vector), "neighbors": [nearest]}
        self.nodes[nearest]["neighbors"].append(vector_id)
        self._prune(vector_id)
        self._prune(nearest)

    def search(self, query, k, max_candidates, metric):
        self._validate(query)
        if not self.nodes:
            return []
        if not isinstance(k, int) or not isinstance(max_candidates, int) or k < 1 or max_candidates < k:
            raise ValueError("max_candidates must be an integer at least k")
        entry = next(iter(self.nodes))
        frontier = [(self._rank(query, self.nodes[entry]["vector"], metric), entry)]
        visited = {entry}
        results = []
        while frontier and len(results) < max_candidates:
            _, current = heapq.heappop(frontier)
            results.append((self._rank(query, self.nodes[current]["vector"], metric), current))
            for neighbor in self.nodes[current]["neighbors"]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    heapq.heappush(frontier, (self._rank(query, self.nodes[neighbor]["vector"], metric), neighbor))
        results.sort()
        return [vector_id for _, vector_id in results[:k]]
```
{{< /tab >}}
{{< tab name="Rust" >}}
```rust
use std::cmp::Ordering;
use std::collections::{BinaryHeap, HashMap};

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum Metric {
    Cosine,
    L2,
    Dot,
}

#[derive(Clone)]
struct Node {
    vector: Vec<f64>,
    neighbors: Vec<i64>,
}

struct Candidate {
    id: i64,
    distance: f64,
}

impl PartialEq for Candidate {
    fn eq(&self, other: &Self) -> bool {
        self.distance.to_bits() == other.distance.to_bits() && self.id == other.id
    }
}

impl Eq for Candidate {}

impl PartialOrd for Candidate {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for Candidate {
    fn cmp(&self, other: &Self) -> Ordering {
        other
            .distance
            .total_cmp(&self.distance)
            .then_with(|| other.id.cmp(&self.id))
    }
}

pub struct BoundedGraph {
    dimensions: usize,
    max_neighbors: usize,
    order: Vec<i64>,
    nodes: HashMap<i64, Node>,
}

impl BoundedGraph {
    pub fn new(dimensions: usize, max_neighbors: usize) -> Self {
        assert!(dimensions > 0 && max_neighbors > 0);
        Self {
            dimensions,
            max_neighbors,
            order: Vec::new(),
            nodes: HashMap::new(),
        }
    }

    fn validate(&self, vector: &[f64]) {
        assert_eq!(vector.len(), self.dimensions);
    }

    fn rank(&self, left: &[f64], right: &[f64], metric: Metric) -> f64 {
        let dot: f64 = left.iter().zip(right).map(|(a, b)| a * b).sum();
        let left_norm = left.iter().map(|value| value * value).sum::<f64>().sqrt();
        let right_norm = right.iter().map(|value| value * value).sum::<f64>().sqrt();
        match metric {
            Metric::Cosine if left_norm == 0.0 || right_norm == 0.0 => 1.0,
            Metric::Cosine => 1.0 - dot / (left_norm * right_norm),
            Metric::L2 => (left_norm * left_norm + right_norm * right_norm - 2.0 * dot).max(0.0).sqrt(),
            Metric::Dot => -dot,
        }
    }

    fn prune(&mut self, node_id: i64) {
        let vector = &self.nodes[&node_id].vector;
        let mut neighbors = self.nodes[&node_id].neighbors.clone();
        neighbors.sort_by(|left, right| {
            let left_distance = self.rank(vector, &self.nodes[left].vector, Metric::L2);
            let right_distance = self.rank(vector, &self.nodes[right].vector, Metric::L2);
            left_distance.total_cmp(&right_distance).then_with(|| left.cmp(right))
        });
        neighbors.truncate(self.max_neighbors);
        self.nodes.get_mut(&node_id).unwrap().neighbors = neighbors;
    }

    pub fn add(&mut self, vector_id: i64, vector: Vec<f64>) {
        self.validate(&vector);
        assert!(!self.nodes.contains_key(&vector_id));
        if self.nodes.is_empty() {
            self.order.push(vector_id);
            self.nodes.insert(vector_id, Node { vector, neighbors: Vec::new() });
            return;
        }
        let nearest = self.order.iter().copied().min_by(|left, right| {
            let left_distance = self.rank(&vector, &self.nodes[left].vector, Metric::L2);
            let right_distance = self.rank(&vector, &self.nodes[right].vector, Metric::L2);
            left_distance.total_cmp(&right_distance).then_with(|| left.cmp(right))
        }).unwrap();
        self.order.push(vector_id);
        self.nodes.insert(vector_id, Node { vector: vector.clone(), neighbors: vec![nearest] });
        self.nodes.get_mut(&nearest).unwrap().neighbors.push(vector_id);
        self.prune(vector_id);
        self.prune(nearest);
    }

    pub fn search(&self, query: &[f64], k: usize, max_candidates: usize, metric: Metric) -> Vec<i64> {
        self.validate(query);
        assert!(k > 0 && max_candidates >= k);
        if self.nodes.is_empty() {
            return Vec::new();
        }
        let entry = self.order[0];
        let mut frontier = BinaryHeap::new();
        let mut visited = std::collections::HashSet::new();
        let mut results = Vec::new();
        frontier.push(Candidate {
            id: entry,
            distance: self.rank(query, &self.nodes[&entry].vector, metric),
        });
        visited.insert(entry);
        while let Some(candidate) = frontier.pop() {
            results.push(candidate.id);
            for neighbor in &self.nodes[&candidate.id].neighbors {
                if visited.insert(*neighbor) {
                    frontier.push(Candidate {
                        id: *neighbor,
                        distance: self.rank(query, &self.nodes[neighbor].vector, metric),
                    });
                }
            }
            if results.len() == max_candidates {
                break;
            }
        }
        results.sort_by(|left, right| {
            let left_distance = self.rank(query, &self.nodes[left].vector, metric);
            let right_distance = self.rank(query, &self.nodes[right].vector, metric);
            left_distance.total_cmp(&right_distance).then_with(|| left.cmp(right))
        });
        results.truncate(k);
        results
    }
}
```
{{< /tab >}}
{{< tab name="TypeScript" >}}
```typescript
export enum Metric {
  Cosine = "cosine",
  L2 = "l2",
  Dot = "dot",
}

export class BoundedGraph {
  private readonly dimensions: number;
  private readonly maxNeighbors: number;
  private readonly nodes = new Map<number, { vector: number[]; neighbors: number[] }>();
  private readonly order: number[] = [];

  constructor(dimensions: number, maxNeighbors: number) {
    if (!Number.isInteger(dimensions) || !Number.isInteger(maxNeighbors) || dimensions < 1 || maxNeighbors < 1) {
      throw new Error("dimensions and maxNeighbors must be positive");
    }
    this.dimensions = dimensions;
    this.maxNeighbors = maxNeighbors;
  }

  private rank(left: number[], right: number[], metric: Metric): number {
    let dot = 0;
    let leftNorm = 0;
    let rightNorm = 0;
    for (let index = 0; index < left.length; index++) {
      dot += left[index] * right[index];
      leftNorm += left[index] * left[index];
      rightNorm += right[index] * right[index];
    }
    if (metric === Metric.Cosine) return leftNorm === 0 || rightNorm === 0 ? 1 : 1 - dot / (Math.sqrt(leftNorm) * Math.sqrt(rightNorm));
    if (metric === Metric.L2) return Math.sqrt(Math.max(0, leftNorm + rightNorm - 2 * dot));
    return -dot;
  }

  private validate(vector: number[]): void {
    if (vector.length !== this.dimensions) {
      throw new Error("unexpected vector width");
    }
  }

  private prune(nodeId: number): void {
    const node = this.nodes.get(nodeId);
    if (!node) throw new Error("missing node");
    node.neighbors.sort((left, right) => {
      const leftNode = this.nodes.get(left);
      const rightNode = this.nodes.get(right);
      if (!leftNode || !rightNode) throw new Error("missing neighbor");
      const leftDistance = this.rank(node.vector, leftNode.vector, Metric.L2);
      const rightDistance = this.rank(node.vector, rightNode.vector, Metric.L2);
      return leftDistance - rightDistance || left - right;
    });
    node.neighbors.splice(this.maxNeighbors);
  }

  add(vectorId: number, vector: number[]): void {
    this.validate(vector);
    if (this.nodes.has(vectorId)) throw new Error("duplicate id");
    if (this.nodes.size === 0) {
      this.order.push(vectorId);
      this.nodes.set(vectorId, { vector: [...vector], neighbors: [] });
      return;
    }
    let nearest = this.order[0];
    let best = this.rank(vector, this.nodes.get(nearest)!.vector, Metric.L2);
    for (const nodeId of this.order) {
      const distance = this.rank(vector, this.nodes.get(nodeId)!.vector, Metric.L2);
      if (distance < best || (distance === best && nodeId < nearest)) {
        best = distance;
        nearest = nodeId;
      }
    }
    this.order.push(vectorId);
    this.nodes.set(vectorId, { vector: [...vector], neighbors: [nearest] });
    this.nodes.get(nearest)!.neighbors.push(vectorId);
    this.prune(vectorId);
    this.prune(nearest);
  }

  search(query: number[], k: number, maxCandidates: number, metric: Metric): number[] {
    this.validate(query);
    if (!Number.isInteger(k) || !Number.isInteger(maxCandidates) || k < 1 || maxCandidates < k) {
      throw new Error("maxCandidates must be an integer at least k");
    }
    if (this.nodes.size === 0) return [];
    const frontier: Array<{ id: number; distance: number }> = [];
    const visited = new Set<number>();
    const results: Array<{ id: number; distance: number }> = [];
    const entry = this.order[0];
    frontier.push({ id: entry, distance: this.rank(query, this.nodes.get(entry)!.vector, metric) });
    visited.add(entry);
    while (frontier.length > 0 && results.length < maxCandidates) {
      frontier.sort((left, right) => left.distance - right.distance || left.id - right.id);
      const current = frontier.shift()!;
      results.push(current);
      for (const neighbor of this.nodes.get(current.id)!.neighbors) {
        if (!visited.has(neighbor)) {
          visited.add(neighbor);
          frontier.push({ id: neighbor, distance: this.rank(query, this.nodes.get(neighbor)!.vector, metric) });
        }
      }
    }
    results.sort((left, right) => left.distance - right.distance || left.id - right.id);
    return results.slice(0, k).map(result => result.id);
  }
}
```
{{< /tab >}}
{{< tab name="Go" >}}
```go
package main

import "container/heap"
import "math"
import "sort"

type Metric string

const (
	Cosine Metric = "cosine"
	L2     Metric = "l2"
	Dot    Metric = "dot"
)

type Node struct {
	id        int
	vector    []float64
	neighbors []int
}

type BoundedGraph struct {
	dimensions   int
	maxNeighbors int
	order        []int
	nodes        map[int]*Node
}

type Candidate struct {
	id       int
	distance float64
}

type CandidateHeap []Candidate

func (candidates CandidateHeap) Len() int {
	return len(candidates)
}

func (candidates CandidateHeap) Less(left, right int) bool {
	return candidates[left].distance < candidates[right].distance ||
		candidates[left].distance == candidates[right].distance && candidates[left].id < candidates[right].id
}

func (candidates CandidateHeap) Swap(left, right int) {
	candidates[left], candidates[right] = candidates[right], candidates[left]
}

func (candidates *CandidateHeap) Push(value any) {
	*candidates = append(*candidates, value.(Candidate))
}

func (candidates *CandidateHeap) Pop() any {
	old := *candidates
	last := len(old) - 1
	value := old[last]
	*candidates = old[:last]
	return value
}

func NewBoundedGraph(dimensions, maxNeighbors int) *BoundedGraph {
	if dimensions < 1 || maxNeighbors < 1 {
		panic("dimensions and maxNeighbors must be positive")
	}
	return &BoundedGraph{
		dimensions:   dimensions,
		maxNeighbors: maxNeighbors,
		nodes:        make(map[int]*Node),
	}
}

func (index *BoundedGraph) rank(left, right []float64, metric Metric) float64 {
	var dot, leftNorm, rightNorm float64
	for position := range left {
		dot += left[position] * right[position]
		leftNorm += left[position] * left[position]
		rightNorm += right[position] * right[position]
	}
	switch metric {
	case Cosine:
		if leftNorm == 0 || rightNorm == 0 {
			return 1
		}
		return 1 - dot/(math.Sqrt(leftNorm)*math.Sqrt(rightNorm))
	case L2:
		return math.Sqrt(math.Max(0, leftNorm+rightNorm-2*dot))
	default:
		return -dot
	}
}

func (index *BoundedGraph) validate(vector []float64) {
	if len(vector) != index.dimensions {
		panic("unexpected vector width")
	}
}

func (index *BoundedGraph) prune(nodeID int) {
	node := index.nodes[nodeID]
	vector := node.vector
	neighbors := append([]int(nil), node.neighbors...)
	sort.Slice(neighbors, func(left, right int) bool {
		leftDistance := index.rank(vector, index.nodes[neighbors[left]].vector, L2)
		rightDistance := index.rank(vector, index.nodes[neighbors[right]].vector, L2)
		return leftDistance < rightDistance || leftDistance == rightDistance && neighbors[left] < neighbors[right]
	})
	if len(neighbors) > index.maxNeighbors {
		neighbors = neighbors[:index.maxNeighbors]
	}
	node.neighbors = neighbors
}

func (index *BoundedGraph) Add(vectorID int, vector []float64) {
	index.validate(vector)
	if _, exists := index.nodes[vectorID]; exists {
		panic("duplicate id")
	}
	if len(index.order) == 0 {
		index.order = append(index.order, vectorID)
		index.nodes[vectorID] = &Node{id: vectorID, vector: append([]float64(nil), vector...)}
		return
	}
	nearest := index.order[0]
	best := index.rank(vector, index.nodes[nearest].vector, L2)
	for _, nodeID := range index.order {
		distance := index.rank(vector, index.nodes[nodeID].vector, L2)
		if distance < best || distance == best && nodeID < nearest {
			best = distance
			nearest = nodeID
		}
	}
	index.order = append(index.order, vectorID)
	index.nodes[vectorID] = &Node{
		id:        vectorID,
		vector:    append([]float64(nil), vector...),
		neighbors: []int{nearest},
	}
	index.nodes[nearest].neighbors = append(index.nodes[nearest].neighbors, vectorID)
	index.prune(vectorID)
	index.prune(nearest)
}

func (index *BoundedGraph) Search(query []float64, k, maxCandidates int, metric Metric) []int {
	index.validate(query)
	if k < 1 || maxCandidates < k {
		panic("maxCandidates must be at least k")
	}
	if len(index.order) == 0 {
		return nil
	}
	entry := index.order[0]
	visited := make(map[int]bool)
	frontier := &CandidateHeap{{id: entry, distance: index.rank(query, index.nodes[entry].vector, metric)}}
	heap.Init(frontier)
	visited[entry] = true
	results := make([]Candidate, 0, maxCandidates)
	for frontier.Len() > 0 && len(results) < maxCandidates {
		current := heap.Pop(frontier).(Candidate)
		results = append(results, current)
		for _, neighbor := range index.nodes[current.id].neighbors {
			if !visited[neighbor] {
				visited[neighbor] = true
				heap.Push(frontier, Candidate{
					id:       neighbor,
					distance: index.rank(query, index.nodes[neighbor].vector, metric),
				})
			}
		}
	}
	sort.Slice(results, func(left, right int) bool {
		return results[left].distance < results[right].distance ||
			results[left].distance == results[right].distance && results[left].id < results[right].id
	})
	if len(results) > k {
		results = results[:k]
	}
	ids := make([]int, len(results))
	for position, result := range results {
		ids[position] = result.id
	}
	return ids
}
```
{{< /tab >}}
{{< /tabs >}}

## Complexity

Let `N` be the number of vectors, `d` their dimension, and `k` the result count. Every distance or similarity comparison in these examples costs O(d). For the unlayered examples, let `M` be the graph degree bound, `C = min(N, maxCandidates)` the number of candidates expanded, and `B = min(N, CM)` the number of distinct candidates that can be discovered. The `maxCandidates` argument bounds expanded candidates, but expanding a candidate can still examine its neighbors. For HNSW, let `e` be the search breadth per layer and `e_build` the insertion candidate breadth. For IVF, let `nlist` be the number of coarse centroids and IVF lists, `nprobe` the number of nearest lists selected for inspection per query, and `C_ivf` the number of candidates retained from those probed lists. Let `I` be the number of k-means iterations and `p` the number of PQ subspaces.

| Operation or index | Time | Space |
| --- | --- | --- |
| Cosine, L2, or dot product | O(d) | O(1) auxiliary |
| Exact top-k scan | O(Nd + N log k) with heap selection | O(k) auxiliary for a bounded heap |
| Unlayered graph insertion with hash-indexed nodes | O(Nd + dM log M) per insertion in Python, Rust, TypeScript, and Go, with expected O(1) node lookup | O(Nd + NM) total |
| Unlayered graph insertion in Java | O(Nd + (N + d)M log M) per insertion because every sort comparison performs a linear neighbor lookup and an O(d) distance calculation | O(Nd + NM) total |
| Unlayered graph insertion in C | O(Nd + (N + d)M²) per insertion: insertion sorting performs O(NM²) linear lookup work and O(dM²) distance-comparison work | O(Nd + NM) total |
| Unlayered graph search with heap-backed frontiers and hash-indexed nodes | O(CM + Bd + B log B + C log C) in Python and Go; O(CM + B d log B + C log C) in Rust because the final comparator recomputes the metric; TypeScript's sorted-array frontier is O(CB log B + Bd) worst case | O(N + B) query space; O(N + maxCandidates) when the result buffer is preallocated |
| Unlayered graph search in Java | O(CMN + Bd + B log B + C log C) because each graph-node lookup is linear | O(N + B) query space |
| Unlayered graph search in C | O(CMN + CB + Bd) because node lookup is linear and frontier selection is a scan | O(N + B) query space; O(N + maxCandidates) because the result buffer is preallocated |
| HNSW search in a layered library | Typically O(e M d log N + k log k) for layered search, neighbor expansion, and result selection | O(Nd + NM) persistent for vectors and graph, plus O(e M log N + k) query space |
| HNSW insertion in a layered library | Typically O(e_build M d log N + e_build M log M) for layered search, neighbor selection, and degree maintenance | O(Nd + NM) persistent, plus O(e_build M log N + M) construction state |
| IVF training with `nlist` centroids | O(I N d nlist) for `I` k-means iterations | O(Nd + nlist d) |
| IVF coarse search and list selection | O(nlist d) to score all centroids plus O(nlist log nprobe) for bounded-heap selection of the closest lists | O(nprobe) auxiliary query space; O(nlist d) persistent centroid storage |
| IVF-PQ search after coarse search | O(C_ivf p + C_ivf log k) with heap selection over `C_ivf` compact candidates; use O(C_ivf d + C_ivf log k) for full-vector candidates | O(nprobe + C_ivf) query space; centroid and codebook storage is persistent index space |

The unlayered examples are not exact nearest-neighbor search: bounded traversal can miss vectors that are reachable only through discarded candidates. HNSW rows describe a layered library implementation, not the examples above. Larger `e`, `nprobe`, or candidate bounds usually increase work and can improve recall, but the response is implementation- and workload-dependent. Product quantization reduces stored vector width, while HNSW and IVF need their own metadata; measured memory and latency must include payloads, replication, and graph or codebook overhead.

## When to use
- You need semantic nearest-neighbor retrieval rather than exact keyword matching.
- An exact scan cannot meet the query-latency objective for the current vector count.
- You can choose a metric appropriate to the embedding model and validate recall against exact results.
- Payloads must support tenant, document, or policy filters without exhausting memory.
- The application can tolerate the index's build time, update behavior, and recall target.

## Alternatives
- **Exact k-NN scan (NumPy or FAISS flat indexes)** — wins when the dataset is small or perfect recall is mandatory, but query cost grows linearly with vector count.
- **Locality-sensitive hashing (LSH)** — wins when a simple probabilistic index and predictable bucket filtering fit the workload, but recall and query cost need careful tuning.
- **Full-text search (BM25 or a relational index)** — wins for exact terms, filters, and lexical explainability, but it does not capture paraphrase similarity.
- **Relational B-tree or inverted indexes** — win for structured predicates and exact lookups, but they are not substitutes for vector-neighborhood search.
- **Model-native long-context retrieval** — wins when the source set fits the context and a model can attend over it, but recurring token cost and context limits make it weaker for large corpora.

## Related
- [Retrieval-Augmented Generation (RAG): Chunking Frameworks, Hybrid Search, Dense/Sparse Embeddings, and Re-ranking](02-rag.md)
- [High-Throughput LLM Serving Frameworks: vLLM, PagedAttention, KV Caching, Continuous Batching, and Speculative Decoding](04-llm-serving.md)
- [Unsupervised Learning: K-Means, Hierarchical Clustering, Principal Component Analysis (PCA)](../01-ml-foundations/02-unsupervised-learning.md)
- [AI Agent Systems: Tool-Calling Mechanics, Long/Short-Term Memory Stores, Reasoning Frameworks (ReAct), and Multi-Agent Orchestration](05-ai-agents.md)
