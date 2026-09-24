---
title: "Dynamic Programming"
weight: 3
toc: true
---

## What it is

Dynamic programming solves optimization problems by breaking them into overlapping subproblems, solving each subproblem once, and storing the result in a table to avoid recomputation. It applies when a problem has both optimal substructure (an optimal solution is built from optimal sub-solutions) and overlapping subproblems.

## How it works

The 0/1 knapsack problem is the canonical example: for each item, either include it (if it fits) or exclude it, taking the maximum. A one-dimensional table `dp[capacity]` is filled item by item, iterating capacity downward so each item is used at most once.

```java
public class Knapsack {
    public static int knapsack(int[] weights, int[] values, int capacity) {
        int[] dp = new int[capacity + 1];
        for (int i = 0; i < weights.length; i++) {
            for (int w = capacity; w >= weights[i]; w--) {
                dp[w] = Math.max(dp[w], dp[w - weights[i]] + values[i]);
            }
        }
        return dp[capacity];
    }
}
```

```c
#include <stdlib.h>

int knapsack(int *weights, int *values, int n, int capacity) {
    int *dp = calloc(capacity + 1, sizeof(int));
    for (int i = 0; i < n; i++) {
        for (int w = capacity; w >= weights[i]; w--) {
            int candidate = dp[w - weights[i]] + values[i];
            if (candidate > dp[w]) dp[w] = candidate;
        }
    }
    int result = dp[capacity];
    free(dp);
    return result;
}
```

```python
def knapsack(weights, values, capacity):
    dp = [0] * (capacity + 1)
    for w, v in zip(weights, values):
        for c in range(capacity, w - 1, -1):
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[capacity]
```

```rust
pub fn knapsack(weights: &[usize], values: &[usize], capacity: usize) -> usize {
    let mut dp = vec![0; capacity + 1];
    for (w, v) in weights.iter().zip(values) {
        for c in (*w..=capacity).rev() {
            dp[c] = dp[c].max(dp[c - w] + v);
        }
    }
    dp[capacity]
}
```

```typescript
function knapsack(weights: number[], values: number[], capacity: number): number {
  const dp = new Array(capacity + 1).fill(0);
  for (let i = 0; i < weights.length; i++) {
    for (let c = capacity; c >= weights[i]; c--) {
      dp[c] = Math.max(dp[c], dp[c - weights[i]] + values[i]);
    }
  }
  return dp[capacity];
}
```

```go
func knapsack(weights, values []int, capacity int) int {
    dp := make([]int, capacity+1)
    for i := range weights {
        for c := capacity; c >= weights[i]; c-- {
            candidate := dp[c-weights[i]] + values[i]
            if candidate > dp[c] {
                dp[c] = candidate
            }
        }
    }
    return dp[capacity]
}
```

## Complexity

| Problem | Time | Space |
| --- | --- | --- |
| 0/1 knapsack | O(n · W) | O(W) |
| Longest common subsequence | O(n · m) | O(min(n, m)) |
| Fibonacci (memoized) | O(n) | O(n) |

## When to use

- When a problem has overlapping subproblems and optimal substructure (knapsack, LCS, edit distance, matrix-chain multiplication).
- When a recursive solution recomputes the same subproblem many times and memoization would eliminate that waste.
- When the state space can be expressed as a table indexed by a small number of integer parameters.

## Alternatives

- **Greedy algorithm**: faster when a greedy choice is provably optimal, but produces wrong answers on problems that lack the greedy-choice property.
- **Recursion with memoization (top-down)**: simpler to derive but uses more stack space than the bottom-up tabulation shown here.
- **Backtracking / brute force**: simpler to implement for small inputs but exponential, infeasible for larger instances.

## Related

- [Greedy Algorithms](02-greedy.md)
- [Backtracking](04-backtracking.md)
- [Shortest Paths](../04-graphs/05-shortest-paths.md)
