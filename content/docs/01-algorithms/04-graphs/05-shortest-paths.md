---
title: "Shortest Path Algorithms: Single-Source (Dijkstra’s, Bellman-Ford) & All-Pairs (Floyd-Warshall, Johnson’s)"
weight: 5
toc: true
---

## What it is
**Single-source shortest-path algorithms** compute distances from one vertex, while **all-pairs shortest-path algorithms** compute a distance matrix; Dijkstra's, Bellman-Ford, Floyd-Warshall, and Johnson's algorithms cover non-negative, negative-edge, dense, and sparse cases.

## How it works
Dijkstra's algorithm finalizes the smallest tentative distance and relaxes outgoing edges. Bellman-Ford relaxes every edge \(V-1\) times, then performs one more pass to detect a reachable negative cycle. Floyd-Warshall considers each vertex as an intermediate vertex. Johnson's algorithm first computes a feasible potential with Bellman-Ford, reweights edges to be non-negative, and runs Dijkstra from every vertex.

```java
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;
import java.util.PriorityQueue;

public final class ShortestPaths {
    public record Edge(int from, int to, long weight) {}
    public record Result(long[] distances, boolean hasNegativeCycle) {}

    private static final long INF = Long.MAX_VALUE / 4;

    public static long[] dijkstra(List<List<Edge>> adjacency, int source) {
        int vertexCount = adjacency.size();
        long[] distance = new long[vertexCount];
        Arrays.fill(distance, INF);
        distance[source] = 0;
        PriorityQueue<long[]> queue = new PriorityQueue<>(Comparator.comparingLong(entry -> entry[1]));
        queue.add(new long[]{source, 0});
        while (!queue.isEmpty()) {
            long[] entry = queue.remove();
            int vertex = (int) entry[0];
            long currentDistance = entry[1];
            if (currentDistance > distance[vertex]) continue;
            for (Edge edge : adjacency.get(vertex)) {
                long candidate = currentDistance + edge.weight();
                if (candidate < distance[edge.to()]) {
                    distance[edge.to()] = candidate;
                    queue.add(new long[]{edge.to(), candidate});
                }
            }
        }
        return distance;
    }

    public static Result bellmanFord(int vertexCount, List<Edge> edges, int source) {
        long[] distance = new long[vertexCount];
        Arrays.fill(distance, INF);
        distance[source] = 0;
        for (int pass = 0; pass < vertexCount - 1; pass++) {
            for (Edge edge : edges) {
                if (distance[edge.from()] != INF && distance[edge.from()] + edge.weight() < distance[edge.to()]) {
                    distance[edge.to()] = distance[edge.from()] + edge.weight();
                }
            }
        }
        for (Edge edge : edges) {
            if (distance[edge.from()] != INF && distance[edge.from()] + edge.weight() < distance[edge.to()]) {
                return new Result(distance, true);
            }
        }
        return new Result(distance, false);
    }

    public static long[][] floydWarshall(long[][] graph) {
        int vertexCount = graph.length;
        long[][] distance = new long[vertexCount][];
        for (int vertex = 0; vertex < vertexCount; vertex++) distance[vertex] = graph[vertex].clone();
        for (int through = 0; through < vertexCount; through++) {
            for (int from = 0; from < vertexCount; from++) {
                if (distance[from][through] == INF) continue;
                for (int to = 0; to < vertexCount; to++) {
                    if (distance[through][to] == INF) continue;
                    long candidate = distance[from][through] + distance[through][to];
                    if (candidate < distance[from][to]) distance[from][to] = candidate;
                }
            }
        }
        return distance;
    }

    public static long[][] johnson(int vertexCount, List<Edge> edges) {
        List<Edge> arcs = new ArrayList<>(edges);
        for (int vertex = 0; vertex < vertexCount; vertex++) arcs.add(new Edge(vertex, 0, 0));
        long[] potential = bellmanFord(vertexCount, arcs, 0).distances();
        List<List<Edge>> weighted = new ArrayList<>();
        for (int vertex = 0; vertex < vertexCount; vertex++) weighted.add(new ArrayList<>());
        for (Edge edge : edges) {
            weighted.get(edge.from()).add(new Edge(edge.from(), edge.to(), edge.weight() + potential[edge.from()] - potential[edge.to()]));
        }
        long[][] distance = new long[vertexCount][vertexCount];
        for (int source = 0; source < vertexCount; source++) {
            long[] reduced = dijkstra(weighted, source);
            for (int target = 0; target < vertexCount; target++) {
                distance[source][target] = reduced[target] - potential[source] + potential[target];
            }
        }
        return distance;
    }
}
```

```c
#include <limits.h>
#include <stdbool.h>
#include <stdlib.h>

#define INF (LLONG_MAX / 4)

typedef struct {
    int from;
    int to;
    int weight;
} Edge;

typedef struct WeightedEdge {
    int to;
    long long weight;
    struct WeightedEdge* next;
} WeightedEdge;

typedef struct {
    int vertex;
    long long distance;
} HeapEntry;

static void shortest_paths_swap(HeapEntry* first, HeapEntry* second) {
    HeapEntry swap = *first;
    *first = *second;
    *second = swap;
}

static void shortest_paths_push(HeapEntry* heap, int* size, HeapEntry entry) {
    int index = (*size)++;
    heap[index] = entry;
    while (index > 0) {
        int parent = (index - 1) / 2;
        if (heap[parent].distance <= heap[index].distance) break;
        shortest_paths_swap(&heap[parent], &heap[index]);
        index = parent;
    }
}

static HeapEntry shortest_paths_pop(HeapEntry* heap, int* size) {
    HeapEntry result = heap[0];
    heap[0] = heap[--(*size)];
    int index = 0;
    while (1) {
        int left = index * 2 + 1;
        int right = left + 1;
        int smallest = index;
        if (left < *size && heap[left].distance < heap[smallest].distance) smallest = left;
        if (right < *size && heap[right].distance < heap[smallest].distance) smallest = right;
        if (smallest == index) break;
        shortest_paths_swap(&heap[index], &heap[smallest]);
        index = smallest;
    }
    return result;
}

void shortest_paths_dijkstra(WeightedEdge** adjacency, int vertex_count, int source, long long* distance) {
    for (int vertex = 0; vertex < vertex_count; vertex++) distance[vertex] = INF;
    distance[source] = 0;
    HeapEntry* queue = malloc((vertex_count * 2) * sizeof(HeapEntry));
    int queue_size = 0;
    shortest_paths_push(queue, &queue_size, (HeapEntry){source, 0});
    while (queue_size > 0) {
        HeapEntry entry = shortest_paths_pop(queue, &queue_size);
        int vertex = entry.vertex;
        if (entry.distance > distance[vertex]) continue;
        for (WeightedEdge* edge = adjacency[vertex]; edge; edge = edge->next) {
            long long candidate = distance[vertex] + edge->weight;
            if (candidate < distance[edge->to]) {
                distance[edge->to] = candidate;
                if (queue_size == vertex_count * 2) queue = realloc(queue, queue_size * 2 * sizeof(HeapEntry));
                shortest_paths_push(queue, &queue_size, (HeapEntry){edge->to, candidate});
            }
        }
    }
    free(queue);
}

bool shortest_paths_bellman_ford(int vertex_count, Edge* edges, int edge_count, int source, long long* distance) {
    for (int vertex = 0; vertex < vertex_count; vertex++) distance[vertex] = INF;
    distance[source] = 0;
    for (int pass = 0; pass < vertex_count - 1; pass++) {
        for (int index = 0; index < edge_count; index++) {
            Edge edge = edges[index];
            if (distance[edge.from] != INF && distance[edge.from] + edge.weight < distance[edge.to]) {
                distance[edge.to] = distance[edge.from] + edge.weight;
            }
        }
    }
    for (int index = 0; index < edge_count; index++) {
        Edge edge = edges[index];
        if (distance[edge.from] != INF && distance[edge.from] + edge.weight < distance[edge.to]) return true;
    }
    return false;
}

void shortest_paths_floyd_warshall(long long** graph, int vertex_count, long long** distance) {
    for (int from = 0; from < vertex_count; from++) {
        for (int to = 0; to < vertex_count; to++) distance[from][to] = graph[from][to];
    }
    for (int through = 0; through < vertex_count; through++) {
        for (int from = 0; from < vertex_count; from++) {
            for (int to = 0; to < vertex_count; to++) {
                if (distance[from][through] != INF && distance[through][to] != INF) {
                    long long candidate = distance[from][through] + distance[through][to];
                    if (candidate < distance[from][to]) distance[from][to] = candidate;
                }
            }
        }
    }
}

void shortest_paths_johnson(int vertex_count, Edge* edges, int edge_count, long long** distance) {
    Edge* arcs = malloc((edge_count + vertex_count) * sizeof(Edge));
    for (int index = 0; index < edge_count; index++) arcs[index] = edges[index];
    int arc_count = edge_count;
    for (int vertex = 0; vertex < vertex_count; vertex++) arcs[arc_count++] = (Edge){vertex, 0, 0};
    long long* potential = malloc(vertex_count * sizeof(long long));
    shortest_paths_bellman_ford(vertex_count, arcs, arc_count, 0, potential);
    WeightedEdge** adjacency = calloc(vertex_count, sizeof(WeightedEdge*));
    for (int index = 0; index < edge_count; index++) {
        Edge edge = edges[index];
        long long weight = edge.weight + potential[edge.from] - potential[edge.to];
        WeightedEdge* node = malloc(sizeof(WeightedEdge));
        node->to = edge.to;
        node->weight = weight;
        node->next = adjacency[edge.from];
        adjacency[edge.from] = node;
    }
    long long* reduced = malloc(vertex_count * sizeof(long long));
    for (int source = 0; source < vertex_count; source++) {
        shortest_paths_dijkstra(adjacency, vertex_count, source, reduced);
        for (int target = 0; target < vertex_count; target++) {
            distance[source][target] = reduced[target] - potential[source] + potential[target];
        }
    }
    for (int vertex = 0; vertex < vertex_count; vertex++) {
        WeightedEdge* edge = adjacency[vertex];
        while (edge) {
            WeightedEdge* next = edge->next;
            free(edge);
            edge = next;
        }
    }
    free(adjacency);
    free(reduced);
    free(potential);
    free(arcs);
}
```

```python
import heapq
from dataclasses import dataclass
from math import inf


@dataclass(frozen=True)
class Edge:
    from_vertex: int
    to_vertex: int
    weight: int


class ShortestPaths:
    @staticmethod
    def dijkstra(adjacency: list[list[Edge]], source: int) -> list[int]:
        distance = [inf] * len(adjacency)
        distance[source] = 0
        queue = [(0, source)]
        while queue:
            current_distance, vertex = heapq.heappop(queue)
            if current_distance > distance[vertex]:
                continue
            for edge in adjacency[vertex]:
                candidate = current_distance + edge.weight
                if candidate < distance[edge.to_vertex]:
                    distance[edge.to_vertex] = candidate
                    heapq.heappush(queue, (candidate, edge.to_vertex))
        return distance

    @staticmethod
    def bellman_ford(vertex_count: int, edges: list[Edge], source: int) -> tuple[list[int], bool]:
        distance = [inf] * vertex_count
        distance[source] = 0
        for _ in range(vertex_count - 1):
            for edge in edges:
                if distance[edge.from_vertex] != inf and distance[edge.from_vertex] + edge.weight < distance[edge.to_vertex]:
                    distance[edge.to_vertex] = distance[edge.from_vertex] + edge.weight
        negative_cycle = any(
            distance[edge.from_vertex] != inf and distance[edge.from_vertex] + edge.weight < distance[edge.to_vertex]
            for edge in edges
        )
        return distance, negative_cycle

    @staticmethod
    def floyd_warshall(graph: list[list[int]]) -> list[list[int]]:
        distance = [row.copy() for row in graph]
        for through in range(len(graph)):
            for from_vertex in range(len(graph)):
                for to_vertex in range(len(graph)):
                    candidate = distance[from_vertex][through] + distance[through][to_vertex]
                    if candidate < distance[from_vertex][to_vertex]:
                        distance[from_vertex][to_vertex] = candidate
        return distance

    @staticmethod
    def johnson(vertex_count: int, edges: list[Edge]) -> list[list[int]]:
        arcs = edges + [Edge(vertex, 0, 0) for vertex in range(vertex_count)]
        potential, _ = ShortestPaths.bellman_ford(vertex_count, arcs, 0)
        weighted: list[list[Edge]] = [[] for _ in range(vertex_count)]
        for edge in edges:
            weighted[edge.from_vertex].append(Edge(edge.from_vertex, edge.to_vertex, edge.weight + potential[edge.from_vertex] - potential[edge.to_vertex]))
        distance: list[list[int]] = []
        for source in range(vertex_count):
            reduced = ShortestPaths.dijkstra(weighted, source)
            distance.append([reduced[target] - potential[source] + potential[target] for target in range(vertex_count)])
        return distance
```

```rust
use std::cmp::Reverse;
use std::collections::BinaryHeap;

#[derive(Clone, Copy)]
pub struct Edge {
    pub from_vertex: usize,
    pub to_vertex: usize,
    pub weight: i64,
}

pub struct ShortestPaths;

impl ShortestPaths {
    const INF: i64 = i64::MAX / 4;

    pub fn dijkstra(adjacency: &[Vec<Edge>], source: usize) -> Vec<i64> {
        let mut distance = vec![Self::INF; adjacency.len()];
        distance[source] = 0;
        let mut queue = BinaryHeap::new();
        queue.push(Reverse((0, source)));
        while let Some(Reverse((current_distance, vertex))) = queue.pop() {
            if current_distance > distance[vertex] {
                continue;
            }
            for edge in &adjacency[vertex] {
                let candidate = current_distance + edge.weight;
                if candidate < distance[edge.to_vertex] {
                    distance[edge.to_vertex] = candidate;
                    queue.push(Reverse((candidate, edge.to_vertex)));
                }
            }
        }
        distance
    }

    pub fn bellman_ford(vertex_count: usize, edges: &[Edge], source: usize) -> (Vec<i64>, bool) {
        let mut distance = vec![Self::INF; vertex_count];
        distance[source] = 0;
        for _ in 0..vertex_count.saturating_sub(1) {
            for edge in edges {
                if distance[edge.from_vertex] != Self::INF && distance[edge.from_vertex] + edge.weight < distance[edge.to_vertex] {
                    distance[edge.to_vertex] = distance[edge.from_vertex] + edge.weight;
                }
            }
        }
        let has_negative_cycle = edges.iter().any(|edge| {
            distance[edge.from_vertex] != Self::INF && distance[edge.from_vertex] + edge.weight < distance[edge.to_vertex]
        });
        (distance, has_negative_cycle)
    }

    pub fn floyd_warshall(graph: &[Vec<i64>]) -> Vec<Vec<i64>> {
        let mut distance = graph.to_vec();
        for through in 0..graph.len() {
            for from_vertex in 0..graph.len() {
                for to_vertex in 0..graph.len() {
                    if distance[from_vertex][through] != Self::INF && distance[through][to_vertex] != Self::INF {
                        let candidate = distance[from_vertex][through] + distance[through][to_vertex];
                        if candidate < distance[from_vertex][to_vertex] {
                            distance[from_vertex][to_vertex] = candidate;
                        }
                    }
                }
            }
        }
        distance
    }

    pub fn johnson(vertex_count: usize, edges: &[Edge]) -> Vec<Vec<i64>> {
        let mut arcs = edges.to_vec();
        arcs.extend((0..vertex_count).map(|vertex| Edge { from_vertex: vertex, to_vertex: 0, weight: 0 }));
        let (potential, _) = Self::bellman_ford(vertex_count, &arcs, 0);
        let mut weighted = vec![Vec::new(); vertex_count];
        for edge in edges {
            weighted[edge.from_vertex].push(Edge {
                from_vertex: edge.from_vertex,
                to_vertex: edge.to_vertex,
                weight: edge.weight + potential[edge.from_vertex] - potential[edge.to_vertex],
            });
        }
        (0..vertex_count)
            .map(|source| {
                let reduced = Self::dijkstra(&weighted, source);
                (0..vertex_count)
                    .map(|target| reduced[target] - potential[source] + potential[target])
                    .collect()
            })
            .collect()
    }
}
```

```typescript
export interface Edge {
  fromVertex: number;
  toVertex: number;
  weight: number;
}

export class ShortestPaths {
  static readonly inf = Number.MAX_SAFE_INTEGER / 4;

  static dijkstra(adjacency: Edge[][], source: number): number[] {
    const distance = new Array<number>(adjacency.length).fill(ShortestPaths.inf);
    distance[source] = 0;
    const queue: [number, number][] = [[0, source]];
    while (queue.length > 0) {
      queue.sort((first, second) => first[0] - second[0]);
      const [currentDistance, vertex] = queue.shift()!;
      if (currentDistance > distance[vertex]) continue;
      for (const edge of adjacency[vertex]) {
        const candidate = currentDistance + edge.weight;
        if (candidate < distance[edge.toVertex]) {
          distance[edge.toVertex] = candidate;
          queue.push([candidate, edge.toVertex]);
        }
      }
    }
    return distance;
  }

  static bellmanFord(vertexCount: number, edges: Edge[], source: number): { distances: number[]; hasNegativeCycle: boolean } {
    const distance = new Array<number>(vertexCount).fill(ShortestPaths.inf);
    distance[source] = 0;
    for (let pass = 0; pass < vertexCount - 1; pass++) {
      for (const edge of edges) {
        if (distance[edge.fromVertex] !== ShortestPaths.inf && distance[edge.fromVertex] + edge.weight < distance[edge.toVertex]) {
          distance[edge.toVertex] = distance[edge.fromVertex] + edge.weight;
        }
      }
    }
    const hasNegativeCycle = edges.some(
      (edge) => distance[edge.fromVertex] !== ShortestPaths.inf && distance[edge.fromVertex] + edge.weight < distance[edge.toVertex],
    );
    return { distances: distance, hasNegativeCycle };
  }

  static floydWarshall(graph: number[][]): number[][] {
    const distance = graph.map((row) => row.slice());
    for (let through = 0; through < graph.length; through++) {
      for (let fromVertex = 0; fromVertex < graph.length; fromVertex++) {
        for (let toVertex = 0; toVertex < graph.length; toVertex++) {
          if (distance[fromVertex][through] === ShortestPaths.inf || distance[through][toVertex] === ShortestPaths.inf) continue;
          const candidate = distance[fromVertex][through] + distance[through][toVertex];
          if (candidate < distance[fromVertex][toVertex]) distance[fromVertex][toVertex] = candidate;
        }
      }
    }
    return distance;
  }

  static johnson(vertexCount: number, edges: Edge[]): number[][] {
    const arcs = edges.concat(Array.from({ length: vertexCount }, (_, vertex) => ({ fromVertex: vertex, toVertex: 0, weight: 0 })));
    const { distances: potential } = ShortestPaths.bellmanFord(vertexCount, arcs, 0);
    const weighted: Edge[][] = Array.from({ length: vertexCount }, () => []);
    for (const edge of edges) {
      weighted[edge.fromVertex].push({ fromVertex: edge.fromVertex, toVertex: edge.toVertex, weight: edge.weight + potential[edge.fromVertex] - potential[edge.toVertex] });
    }
    return Array.from({ length: vertexCount }, (_, source) => {
      const reduced = ShortestPaths.dijkstra(weighted, source);
      return reduced.map((value, target) => value - potential[source] + potential[target]);
    });
  }
}
```

```go
package graph

import (
	"container/heap"
	"math"
)

type Edge struct {
	From int
	To   int
	Weight int64
}

type distanceEntry struct {
	Vertex   int
	Distance int64
}

type distanceMinHeap []distanceEntry

func (queue distanceMinHeap) Len() int           { return len(queue) }
func (queue distanceMinHeap) Less(first, second int) bool {
	return queue[first].Distance < queue[second].Distance
}
func (queue distanceMinHeap) Swap(first, second int) {
	queue[first], queue[second] = queue[second], queue[first]
}
func (queue *distanceMinHeap) Push(value any) { *queue = append(*queue, value.(distanceEntry)) }
func (queue *distanceMinHeap) Pop() any {
	old := *queue
	last := len(old) - 1
	value := old[last]
	*queue = old[:last]
	return value
}

type ShortestPaths struct{}

const shortestPathInfinity = int64(math.MaxInt64 / 4)

func (ShortestPaths) Dijkstra(adjacency [][]Edge, source int) []int64 {
	distance := make([]int64, len(adjacency))
	for vertex := range distance {
		distance[vertex] = shortestPathInfinity
	}
	distance[source] = 0
	queue := &distanceMinHeap{{Vertex: source, Distance: 0}}
	heap.Init(queue)
	for queue.Len() > 0 {
		entry := heap.Pop(queue).(distanceEntry)
		if entry.Distance > distance[entry.Vertex] {
			continue
		}
		for _, edge := range adjacency[entry.Vertex] {
			candidate := entry.Distance + edge.Weight
			if candidate < distance[edge.To] {
				distance[edge.To] = candidate
				heap.Push(queue, distanceEntry{Vertex: edge.To, Distance: candidate})
			}
		}
	}
	return distance
}

func (ShortestPaths) BellmanFord(vertexCount int, edges []Edge, source int) ([]int64, bool) {
	distance := make([]int64, vertexCount)
	for vertex := range distance {
		distance[vertex] = shortestPathInfinity
	}
	distance[source] = 0
	for pass := 0; pass < vertexCount-1; pass++ {
		for _, edge := range edges {
			if distance[edge.From] != shortestPathInfinity && distance[edge.From]+edge.Weight < distance[edge.To] {
				distance[edge.To] = distance[edge.From] + edge.Weight
			}
		}
	}
	for _, edge := range edges {
		if distance[edge.From] != shortestPathInfinity && distance[edge.From]+edge.Weight < distance[edge.To] {
			return distance, true
		}
	}
	return distance, false
}

func (ShortestPaths) FloydWarshall(graph [][]int64) [][]int64 {
	distance := make([][]int64, len(graph))
	for vertex := range graph {
		distance[vertex] = append([]int64(nil), graph[vertex]...)
	}
	for through := range graph {
		for fromVertex := range graph {
			for toVertex := range graph {
				if distance[fromVertex][through] == shortestPathInfinity || distance[through][toVertex] == shortestPathInfinity {
					continue
				}
				candidate := distance[fromVertex][through] + distance[through][toVertex]
				if candidate < distance[fromVertex][toVertex] {
					distance[fromVertex][toVertex] = candidate
				}
			}
		}
	}
	return distance
}

func (ShortestPaths) Johnson(vertexCount int, edges []Edge) [][]int64 {
	arcs := append([]Edge(nil), edges...)
	for vertex := 0; vertex < vertexCount; vertex++ {
		arcs = append(arcs, Edge{From: vertex, To: 0})
	}
	potential, _ := ShortestPaths{}.BellmanFord(vertexCount, arcs, 0)
	weighted := make([][]Edge, vertexCount)
	for _, edge := range edges {
		weighted[edge.From] = append(weighted[edge.From], Edge{From: edge.From, To: edge.To, Weight: edge.Weight + potential[edge.From] - potential[edge.To]})
	}
	distance := make([][]int64, vertexCount)
	for source := 0; source < vertexCount; source++ {
		reduced := (ShortestPaths{}).Dijkstra(weighted, source)
		distance[source] = make([]int64, vertexCount)
		for target := 0; target < vertexCount; target++ {
			distance[source][target] = reduced[target] - potential[source] + potential[target]
		}
	}
	return distance
}
```

## Complexity
For \(V\) vertices and \(E\) edges:

| Algorithm | Scope and assumptions | Time | Extra space |
| --- | --- | --- | --- |
| Dijkstra with a binary heap | One source, non-negative weights | O((V+E) log V) | O(V+E) |
| Bellman-Ford | One source, negative edges allowed | O(VE) | O(V) |
| Floyd-Warshall | All pairs, dense representation | O(V³) | O(V²) |
| Johnson's algorithm | All pairs, sparse graph, no negative cycle | O(VE + V(V+E) log V) | O(V²+E) |

Dijkstra's implementation uses integer distances bounded well below its infinity sentinel; implementations without fixed-width integers must also guard against overflow during relaxation.

## When to use
- You need one-source routing with non-negative road or network costs.
- You need single-source results with negative edges or negative-cycle detection.
- You need all-pairs results for a small, dense graph.
- You need all-pairs results for a larger sparse graph that has no negative cycle.

## Alternatives
- **A*** — expands nodes likely to reach one target, but it requires a suitable heuristic and does not provide all-pairs results.
- **Contraction hierarchies** — precomputes shortcuts for road-network routing and is much faster in specialized map engines than general-purpose Dijkstra.
- **Bidirectional Dijkstra** — searches from source and target, but reverse weights and meeting logic complicate negative-edge support.

## Related
- [Graph Representations (Adjacency Matrix, Adjacency List, Edge List)](01-graph-representations.md)
- [Graph Traversals: Breadth-First Search (BFS) and Depth-First Search (DFS)](02-graph-traversals.md)
- [Minimum Spanning Trees (Kruskal's, Prim's Algorithms)](04-minimum-spanning-trees.md)
- [Network Flow & Matching (Ford-Fulkerson, Edmonds-Karp, Dinic’s, Hopcroft-Karp)](06-network-flow.md)
- [Heaps, Priority Queues, and Fibonacci Heaps](../02-search-trees/02-heaps-priority-queues.md)
- [Disjoint-Set Data Structures (Union-Find with Path Compression)](../02-search-trees/05-union-find.md)
- [Greedy Choice Paradigms & Interval Scheduling](../03-paradigms/02-greedy.md)
- [Dynamic Programming (Memoization, Tabulation, State Compression, Space Optimization)](../03-paradigms/03-dynamic-programming.md)
- [Topological Sorting & Strongly Connected Components (Tarjan’s, Kosaraju’s)](03-topological-sort-scc.md)
