---
title: "Mindmap"
weight: 7
---

Use this map as a study index. Each item points to a family of techniques; the linked algorithm
chapters provide the full explanation and implementations.

## Foundations

- [Power of 2](04-maths.md)
- [Data types and memory bytes](02-how-memory-works.md)

- [Memory layout and data types](02-how-memory-works.md)

## Data structures and algorithms

### [Arrays](../01-algorithms/01-linear-data-structures/01-dynamic-arrays.md)

- Searching in arrays
  - Linear search
  - [Binary search](../01-algorithms/02-search-trees/01-binary-search-trees.md)
- Sorting in arrays
  - [Basic sorts (bubble, selection, insertion)](../01-algorithms/03-paradigms/01-divide-and-conquer-sorting.md)

### [Linked lists](../01-algorithms/01-linear-data-structures/02-linked-lists.md)

- Searching in linked lists
- Sorting linked lists

### [Stacks and queues](../01-algorithms/01-linear-data-structures/03-stacks-queues-deques.md)

- Traversing stacks
- Traversing queues

### [Trees](../01-algorithms/02-search-trees/01-binary-search-trees.md)

- Traversals
  - Bfs iterative traversal
  - Dfs iterative traversal
- Binary search trees

### [Heaps](../01-algorithms/02-search-trees/02-heaps-priority-queues.md)

- Heapify
- Sift down
- Heap sort

### [Graphs](../01-algorithms/04-graphs/01-graph-representations.md)

- Adjacency lists
- Adjacency matrix
- [Dfs graph traversal](../01-algorithms/04-graphs/02-graph-traversals.md)
- [Bfs graph traversal](../01-algorithms/04-graphs/02-graph-traversals.md)
- [Topological sorting](../01-algorithms/04-graphs/03-topological-sort-scc.md)

### [Disjoint sets](../01-algorithms/02-search-trees/05-union-find.md)

- Union find
  - [Minimum spanning trees](../01-algorithms/04-graphs/04-minimum-spanning-trees.md)
    - Prim’s algorithm
    - Kruskal’s algorithm
  - [Maximum flow](../01-algorithms/04-graphs/06-network-flow.md)
  - [Shortest paths](../01-algorithms/04-graphs/05-shortest-paths.md)
    - Bellman-Ford
    - Dijkstra’s algorithm
    - Floyd-Warshall

[Trie](../01-algorithms/02-search-trees/06-tries-suffix.md)

- String matching
- Edit distances

[Hash set](../01-algorithms/01-linear-data-structures/04-hash-tables.md)

- Hash table
- Hash function

Use basic implementations first; add the optimized or advanced variant after the invariant is clear.

The material is organized by dependency rather than difficulty.

## Advanced structures

- [Red black trees](../01-algorithms/02-search-trees/01-binary-search-trees.md)
- [AVL trees](../01-algorithms/02-search-trees/01-binary-search-trees.md)
- Binomial heap
- [Fibonacci heap](../01-algorithms/02-search-trees/02-heaps-priority-queues.md)

## Techniques

- [Bit manipulation](../01-algorithms/01-linear-data-structures/05-bitwise-bloom-filters.md)
- [Bit masking](../01-algorithms/01-linear-data-structures/05-bitwise-bloom-filters.md)
- [Ones complement](../01-algorithms/01-linear-data-structures/05-bitwise-bloom-filters.md)
- [Twos complement](../01-algorithms/01-linear-data-structures/05-bitwise-bloom-filters.md)
- Two pointers
- [Cycle detection](../01-algorithms/04-graphs/02-graph-traversals.md)
- Sliding windows
- Prefix sum
- [Dynamic programming](../01-algorithms/03-paradigms/03-dynamic-programming.md)
  - 0/1, fractional, unlimited Knapsack method
  - Recursion, top-down, memoization
  - [Combinatorics, backtracking](../01-algorithms/03-paradigms/04-backtracking.md)
  - Iteration, bottom-up
- [Greedy programming](../01-algorithms/03-paradigms/02-greedy.md)
- [Morris traversal](../01-algorithms/02-search-trees/01-binary-search-trees.md)
- [A* path finding](../01-algorithms/04-graphs/05-shortest-paths.md)
- [Rabin karp pattern matching](../01-algorithms/02-search-trees/06-tries-suffix.md)
- [Knuth Morris pratt pattern matching](../01-algorithms/02-search-trees/06-tries-suffix.md)
- Levenshtein distance

## Mathematics

- Primes, sieve
- Catalan
- Permutation
- [Binary to decimal, to hex conversions](04-maths.md)
- [Logarithms to base](04-maths.md)
- [Bit shifting](../01-algorithms/01-linear-data-structures/05-bitwise-bloom-filters.md)
- Fastest way to add, subtract, multiply, divide, exponent, sqrt
- [Computational complexity](../01-algorithms/04a-computational-theory/01-complexity-theory.md)

## Review checklist

- [Templates](06-memory-works-templates.md)
- [Memory bytes sizes reference](02-how-memory-works.md)
- Network latency reference
