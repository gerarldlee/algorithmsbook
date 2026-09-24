---
title: "Computational Complexity Theory: P vs NP, NP-Completeness, NP-Hardness, and Polynomial-Time Reductions"
weight: 1
toc: true
tabs: {sync: true}
---

## What it is
**Computational complexity theory** classifies problems by the resources needed to solve them, especially time. It compares efficiently verifiable problems in **P** with problems whose proposed solutions can be checked quickly in **NP**, and uses **polynomial-time reductions** to transfer difficulty between problems.

## How it works
A problem is in P when a correct algorithm runs in time bounded by a polynomial in the input length. SAT asks whether a Boolean formula can be made true, and it belongs to NP because a proposed assignment can be checked in polynomial time. A problem \(K\) is NP-complete when it belongs to NP and every problem in NP has a polynomial-time reduction to \(K\). NP-hardness is weaker and broader; a problem can be NP-hard without belonging to NP.

A reduction \(A \le_p B\) means that a solver for \(B\) can solve \(A\) after a polynomial-time transformation. The direction matters. If a graph has a \(k\)-clique exactly when its complement has an independent set of size \(k\), transforming an undirected graph into its complement is polynomial. An independent-set solver applied to that complement therefore solves the original clique instance. Building all complement edges takes \(O(V^2)\) time and space with adjacency matrices, independent of whether a clique actually exists.

The implementation below performs that reduction and represents the result as an adjacency matrix. Its `reduces` operation checks whether a candidate has every required edge in that complement, where a candidate is independent in the complement exactly when it is a clique in the original graph. All six APIs take the same vertex count and edge list for the reduction, then the complement matrix and candidate for verification. SAT-to-3-SAT, set-cover reductions, and Cook-Levin constructions establish other hardness results; none turns NP-completeness into a proof that every NP problem is intractable.

{{< tabs >}}
{{< tab name="Java" >}}
```java
import java.util.List;

public final class ComputationalTheory {
    public static int[][] complementGraph(int vertexCount, List<int[]> edges) {
        boolean[][] connected = new boolean[vertexCount][vertexCount];
        for (int[] edge : edges) {
            connected[edge[0]][edge[1]] = true;
            connected[edge[1]][edge[0]] = true;
        }
        int[][] complement = new int[vertexCount][vertexCount];
        for (int left = 0; left < vertexCount; left++) {
            for (int right = 0; right < vertexCount; right++) {
                complement[left][right] = left == right || !connected[left][right] ? 1 : 0;
            }
        }
        return complement;
    }

    public static int[][] reduceCliqueToIndependentSet(int vertexCount, List<int[]> edges) {
        return complementGraph(vertexCount, edges);
    }

    public static boolean reduces(int[][] complement, int[] candidate) {
        for (int left = 0; left < candidate.length; left++) {
            for (int right = left + 1; right < candidate.length; right++) {
                int first = candidate[left];
                int second = candidate[right];
                if (complement[first][second] == 0) return false;
            }
        }
        return true;
    }
}
```

{{< /tab >}}
{{< tab name="C" >}}
```c
#include <stdbool.h>
#include <stdlib.h>

typedef struct {
    int first;
    int second;
} Edge;

int** computational_theory_complement_graph(int vertex_count, Edge* edges, int edge_count) {
    bool** connected = calloc(vertex_count, sizeof(bool*));
    int** complement = malloc(vertex_count * sizeof(int*));
    for (int vertex = 0; vertex < vertex_count; vertex++) {
        connected[vertex] = calloc(vertex_count, sizeof(bool));
        complement[vertex] = malloc(vertex_count * sizeof(int));
    }
    for (int edge = 0; edge < edge_count; edge++) {
        connected[edges[edge].first][edges[edge].second] = true;
        connected[edges[edge].second][edges[edge].first] = true;
    }
    for (int left = 0; left < vertex_count; left++) {
        for (int right = 0; right < vertex_count; right++) {
            complement[left][right] = left == right || !connected[left][right];
        }
    }
    for (int vertex = 0; vertex < vertex_count; vertex++) free(connected[vertex]);
    free(connected);
    return complement;
}

int** computational_theory_reduce_clique_to_independent_set(int vertex_count, Edge* edges, int edge_count) {
    return computational_theory_complement_graph(vertex_count, edges, edge_count);
}

bool computational_theory_reduces(int** complement, int* candidate, int candidate_count) {
    for (int left = 0; left < candidate_count; left++) {
        for (int right = left + 1; right < candidate_count; right++) {
            if (!complement[candidate[left]][candidate[right]]) return false;
        }
    }
    return true;
}
```

{{< /tab >}}
{{< tab name="Python" >}}
```python
class ComputationalTheory:
    @staticmethod
    def complement_graph(vertex_count: int, edges: list[tuple[int, int]]) -> list[list[int]]:
        connected = [[False] * vertex_count for _ in range(vertex_count)]
        for first, second in edges:
            connected[first][second] = True
            connected[second][first] = True
        return [[int(left == right or not connected[left][right]) for right in range(vertex_count)] for left in range(vertex_count)]

    @staticmethod
    def reduce_clique_to_independent_set(vertex_count: int, edges: list[tuple[int, int]]) -> list[list[int]]:
        return ComputationalTheory.complement_graph(vertex_count, edges)

    @staticmethod
    def reduces(complement: list[list[int]], candidate: list[int]) -> bool:
        return all(complement[candidate[left]][candidate[right]] == 1 for left in range(len(candidate)) for right in range(left + 1, len(candidate)))
```

{{< /tab >}}
{{< tab name="Rust" >}}
```rust
pub struct ComputationalTheory;

impl ComputationalTheory {
    pub fn complement_graph(vertex_count: usize, edges: &[(usize, usize)]) -> Vec<Vec<u8>> {
        let mut connected = vec![vec![false; vertex_count]; vertex_count];
        for &(first, second) in edges {
            connected[first][second] = true;
            connected[second][first] = true;
        }
        let mut complement = vec![vec![0u8; vertex_count]; vertex_count];
        for left in 0..vertex_count {
            for right in 0..vertex_count {
                complement[left][right] = u8::from(left == right || !connected[left][right]);
            }
        }
        complement
    }

    pub fn reduce_clique_to_independent_set(vertex_count: usize, edges: &[(usize, usize)]) -> Vec<Vec<u8>> {
        Self::complement_graph(vertex_count, edges)
    }

    pub fn reduces(complement: &[Vec<u8>], candidate: &[usize]) -> bool {
        candidate.iter().enumerate().all(|(left, &first)| {
            candidate[left + 1..]
                .iter()
                .all(|&second| complement[first][second] == 1)
        })
    }
}
```

{{< /tab >}}
{{< tab name="TypeScript" >}}
```typescript
export class ComputationalTheory {
  static complementGraph(vertexCount: number, edges: [number, number][]): number[][] {
    const connected = Array.from({ length: vertexCount }, () => new Array<boolean>(vertexCount).fill(false));
    for (const [first, second] of edges) {
      connected[first][second] = true;
      connected[second][first] = true;
    }
    return connected.map((row, left) => row.map((value, right) => (left === right || !value ? 1 : 0)));
  }

  static reduceCliqueToIndependentSet(vertexCount: number, edges: [number, number][]): number[][] {
    return ComputationalTheory.complementGraph(vertexCount, edges);
  }

  static reduces(complement: number[][], candidate: number[]): boolean {
    for (let left = 0; left < candidate.length; left++) {
      for (let right = left + 1; right < candidate.length; right++) {
        if (complement[candidate[left]][candidate[right]] === 0) return false;
      }
    }
    return true;
  }
}
```

{{< /tab >}}
{{< tab name="Go" >}}
```go
package theory

type ComputationalTheory struct{}

type Edge struct {
	First  int
	Second int
}

func (ComputationalTheory) ComplementGraph(vertexCount int, edges []Edge) [][]int {
	connected := make([][]bool, vertexCount)
	complement := make([][]int, vertexCount)
	for vertex := 0; vertex < vertexCount; vertex++ {
		connected[vertex] = make([]bool, vertexCount)
		complement[vertex] = make([]int, vertexCount)
	}
	for _, edge := range edges {
		connected[edge.First][edge.Second] = true
		connected[edge.Second][edge.First] = true
	}
	for left := 0; left < vertexCount; left++ {
		for right := 0; right < vertexCount; right++ {
			if left == right || !connected[left][right] {
				complement[left][right] = 1
			}
		}
	}
	return complement
}

func (ComputationalTheory) ReduceCliqueToIndependentSet(vertexCount int, edges []Edge) [][]int {
	return ComputationalTheory{}.ComplementGraph(vertexCount, edges)
}

func (ComputationalTheory) Reduces(complement [][]int, candidate []int) bool {
	for left := 0; left < len(candidate); left++ {
		for right := left + 1; right < len(candidate); right++ {
			if complement[candidate[left]][candidate[right]] == 0 {
				return false
			}
		}
	}
	return true
}
{{< /tab >}}
{{< /tabs >}}

## Complexity
For an input with \(n\) bits, an \(O(n^k)\) algorithm is polynomial for fixed \(k\). Polynomial constants can still be large, so polynomial membership does not guarantee a fast program for a particular input size.

| Task | Time | Space |
| --- | --- | --- |
| Build a complement adjacency matrix | O(V²) | O(V²) |
| Check one candidate set | O(k²) | O(1) extra |
| Verify a Boolean assignment | O(L) | O(L) for a formula parser |

## When to use
- You need to justify why an optimization problem is at least as hard as a known hard problem.
- You need to establish that two problem definitions can be transformed into one another efficiently.
- You need to distinguish exhaustive search, randomized search, and guaranteed polynomial algorithms.
- You need to review a claimed efficient algorithm for hidden assumptions or an invalid reduction direction.

## Alternatives
- **Parameterized algorithms** — can solve NP-hard problems quickly when a parameter such as a feedback vertex set is small, but do not remove the worst-case difficulty.
- **SAT solvers and integer programming** — handle many structured practical instances despite NP-completeness, usually with heuristics and incomplete time limits.
- **Circuit complexity** — studies lower bounds through Boolean circuits and can refine what P versus NP leaves unresolved.

## Related
- [Randomized & Approximation Algorithms: Reservoir Sampling, Fisher-Yates, MinHash, and Approximation Bounds](02-randomized-approximation-algorithms.md)
- [Computational Geometry Algorithms](04-computational-geometry.md)
- [Graph Traversals: Breadth-First Search (BFS) and Depth-First Search (DFS)](../04-graphs/02-graph-traversals.md)
- [Finite Automata & Formal Languages: NFA/DFA Constructions, Thompson's Construction, and Regex Engine Compilation](03-automata-formal-languages.md)
