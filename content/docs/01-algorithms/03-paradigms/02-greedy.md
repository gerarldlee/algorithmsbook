---
title: "Greedy Algorithms"
weight: 2
toc: true
---

## What it is

A greedy algorithm builds a solution incrementally, always choosing the locally optimal option at each step in the hope of reaching a global optimum. Greedy works only when the problem has an optimal-substructure property and a greedy-choice property that guarantees local optimality leads to the global optimum.

## How it works

The classic activity-selection (interval scheduling) problem demonstrates the greedy choice: sort intervals by finish time, then repeatedly pick the earliest-finishing interval that does not overlap the last selected one. Choosing by earliest finish time always leaves the maximum room for the remaining intervals.

```java
import java.util.*;

public class ActivitySelection {
    public static int select(int[][] intervals) {
        Arrays.sort(intervals, Comparator.comparingInt(a -> a[1]));
        int count = 0, lastEnd = Integer.MIN_VALUE;
        for (int[] iv : intervals) {
            if (iv[0] >= lastEnd) {
                count++;
                lastEnd = iv[1];
            }
        }
        return count;
    }
}
```

```c
#include <stdlib.h>
#include <limits.h>

static int cmp(const void *a, const void *b) {
    return ((const int *)a)[1] - ((const int *)b)[1];
}

int activity_selection(int intervals[][2], int n) {
    qsort(intervals, n, sizeof(intervals[0]), cmp);
    int count = 0, last_end = INT_MIN;
    for (int i = 0; i < n; i++) {
        if (intervals[i][0] >= last_end) {
            count++;
            last_end = intervals[i][1];
        }
    }
    return count;
}
```

```python
def activity_selection(intervals):
    intervals.sort(key=lambda x: x[1])
    count = 0
    last_end = float('-inf')
    for start, end in intervals:
        if start >= last_end:
            count += 1
            last_end = end
    return count
```

```rust
pub fn activity_selection(mut intervals: Vec<(i32, i32)>) -> usize {
    intervals.sort_by_key(|iv| iv.1);
    let mut count = 0;
    let mut last_end = i32::MIN;
    for (start, end) in intervals {
        if start >= last_end {
            count += 1;
            last_end = end;
        }
    }
    count
}
```

```typescript
function activitySelection(intervals: [number, number][]): number {
  intervals.sort((a, b) => a[1] - b[1]);
  let count = 0;
  let lastEnd = -Infinity;
  for (const [start, end] of intervals) {
    if (start >= lastEnd) {
      count++;
      lastEnd = end;
    }
  }
  return count;
}
```

```go
import "sort"

func activitySelection(intervals [][]int) int {
    sort.Slice(intervals, func(i, j int) bool {
        return intervals[i][1] < intervals[j][1]
    })
    count := 0
    lastEnd := -1 << 63
    for _, iv := range intervals {
        if iv[0] >= lastEnd {
            count++
            lastEnd = iv[1]
        }
    }
    return count
}
```

## Complexity

| Algorithm | Time | Space |
| --- | --- | --- |
| Activity selection | O(n log n) | O(1) in-place |
| Dijkstra (binary heap) | O((V + E) log V) | O(V) |
| Huffman coding | O(n log n) | O(n) |

## When to use

- When a problem has optimal substructure and a provable greedy-choice property (interval scheduling, fractional knapsack, Huffman coding, Prim's/Kruskal's MST).
- When you need a fast, simple heuristic that produces an acceptable solution even if optimality is not required.
- As a building block inside other algorithms (e.g. greedy vertex selection in matching or clustering).

## Alternatives

- **Dynamic programming**: handles problems where greedy fails by exploring all choices, but costs more time and space.
- **Backtracking**: exhaustively finds the true optimum when greedy choices cannot be proven correct, at exponential cost.
- **Branch and bound**: prunes the search to beat plain backtracking while still guaranteeing optimality, but requires a good bound.

## Related

- [Divide and Conquer Sorting](01-divide-and-conquer-sorting.md)
- [Dynamic Programming](03-dynamic-programming.md)
- [Minimum Spanning Trees](../04-graphs/04-minimum-spanning-trees.md)
- [Shortest Paths](../04-graphs/05-shortest-paths.md)
