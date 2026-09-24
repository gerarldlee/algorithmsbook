---
title: "Greedy Choice Paradigms & Interval Scheduling"
weight: 2
toc: true
---

## What it is

A **greedy algorithm** commits to a locally best choice at each step without revisiting earlier choices. A greedy choice is optimal only when a proof, often an **exchange argument**, shows that some optimal solution contains the choice made by the algorithm.

## How it works

Interval scheduling chooses the maximum number of non-overlapping intervals. The algorithm sorts intervals by increasing finish time, keeps the first interval, and then keeps each interval that starts no earlier than the last selected interval. Replacing the first compatible interval in an optimal schedule with the earliest-finishing interval cannot remove any later choice, because the replacement finishes no later. Repeating that argument proves optimality.

The same proof structure appears in other greedy paradigms. Fractional knapsack repeatedly takes the highest value-to-weight ratio because any fractional solution can exchange a smaller item for the remaining fraction of that item. Huffman coding repeatedly combines the two least frequent symbols, and Prim's and Kruskal's algorithms repeatedly add the cheapest edge that preserves a partial solution.

The implementations expose one `select` operation that returns the chosen intervals in start-time order. They require intervals whose start is less than or equal to their finish, sort by finish time with start time as the tie-breaker, and allow touching endpoints. In C, `select` writes the result length through `selected_size`, and the returned array belongs to the caller.

```java
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

public class ActivitySelection {
    public record Interval(int start, int end) {}

    public static List<Interval> select(List<Interval> intervals) {
        List<Interval> candidates = new ArrayList<>(intervals);
        candidates.sort(Comparator.comparingInt(Interval::end).thenComparingInt(Interval::start));
        List<Interval> selected = new ArrayList<>();
        int lastEnd = Integer.MIN_VALUE;
        for (Interval interval : candidates) {
            if (interval.start() >= lastEnd) {
                selected.add(interval);
                lastEnd = interval.end();
            }
        }
        return selected;
    }
}
```

```c
#include <limits.h>
#include <stddef.h>
#include <stdlib.h>

typedef struct {
    int start;
    int end;
} Interval;

static int compare_intervals(const void *left, const void *right) {
    const Interval *a = left;
    const Interval *b = right;
    if (a->end != b->end) return a->end < b->end ? -1 : 1;
    if (a->start != b->start) return a->start < b->start ? -1 : 1;
    return 0;
}

Interval *activity_selection_select(const Interval *intervals, size_t size, size_t *selected_size) {
    Interval *candidates = malloc(size * sizeof(Interval));
    Interval *selected = malloc(size * sizeof(Interval));
    if (size > 0 && (candidates == NULL || selected == NULL)) abort();
    for (size_t i = 0; i < size; i++) candidates[i] = intervals[i];
    qsort(candidates, size, sizeof(Interval), compare_intervals);
    size_t count = 0;
    int last_end = INT_MIN;
    for (size_t i = 0; i < size; i++) {
        if (candidates[i].start >= last_end) {
            selected[count++] = candidates[i];
            last_end = candidates[i].end;
        }
    }
    free(candidates);
    *selected_size = count;
    return selected;
}
```

```python
class Interval:
    def __init__(self, start, end):
        self.start = start
        self.end = end


class ActivitySelection:
    @staticmethod
    def select(intervals):
        candidates = sorted(intervals, key=lambda interval: (interval.end, interval.start))
        selected = []
        last_end = float("-inf")
        for interval in candidates:
            if interval.start >= last_end:
                selected.append(interval)
                last_end = interval.end
        return selected
```

```rust
pub struct Interval {
    pub start: i32,
    pub end: i32,
}

pub struct ActivitySelection;

impl ActivitySelection {
    pub fn select(intervals: &[Interval]) -> Vec<Interval> {
        let mut candidates = intervals.to_vec();
        candidates.sort_by_key(|interval| (interval.end, interval.start));
        let mut selected = Vec::new();
        let mut last_end = i32::MIN;
        for interval in candidates {
            if interval.start >= last_end {
                last_end = interval.end;
                selected.push(interval);
            }
        }
        selected
    }
}
```

```typescript
export type Interval = [number, number];

export class ActivitySelection {
  static select(intervals: Interval[]): Interval[] {
    const candidates = intervals
      .map((interval) => [...interval] as Interval)
      .sort((a, b) => a[1] - b[1] || a[0] - b[0]);
    const selected: Interval[] = [];
    let lastEnd = -Infinity;
    for (const [start, end] of candidates) {
      if (start >= lastEnd) {
        selected.push([start, end]);
        lastEnd = end;
      }
    }
    return selected;
  }
}
```

```go
package greedyselection

import "sort"

type Interval struct {
    Start int
    End   int
}

type ActivitySelection struct{}

func (ActivitySelection) Select(intervals []Interval) []Interval {
    candidates := append([]Interval(nil), intervals...)
    sort.Slice(candidates, func(i, j int) bool {
        if candidates[i].End == candidates[j].End {
            return candidates[i].Start < candidates[j].Start
        }
        return candidates[i].End < candidates[j].End
    })
    selected := make([]Interval, 0, len(candidates))
    lastEnd := 0
    for index, interval := range candidates {
        if index == 0 || interval.Start >= lastEnd {
            selected = append(selected, interval)
            lastEnd = interval.End
        }
    }
    return selected
}
```

## Complexity

| Algorithm | Time | Extra space |
| --- | --- | --- |
| Interval scheduling | O(n log n) | O(n), including the selected output |
| Fractional knapsack after sorting | O(n log n) | O(n) or O(1) depending on the sort |
| Huffman coding with a binary heap | O(n log n) | O(n) |
| Prim's algorithm with a binary heap | O((V + E) log V) | O(V) |

## When to use

- You can prove that an optimal solution can begin with the local choice the algorithm makes.
- An exchange argument can transform an optimal solution to include each greedy choice.
- Early commitments are never invalidated by later choices, as in interval scheduling.
- The input can be sorted or searched for the next greedy candidate efficiently.
- You need a fast solution and can establish the optimality property rather than treating the rule as a heuristic.

## Alternatives

- **Dynamic programming** — handles overlapping choices by storing results for subproblems, but usually costs more time and space.
- **Branch and bound** — explores alternatives when a greedy proof does not apply and prunes them with a cost bound.
- **Approximation algorithm** — guarantees a computable relationship to the optimum for large problems, but does not guarantee the exact optimum.

## Related

- [Divide-and-Conquer & Advanced Sorting (Quick, Merge, Radix, Counting Sort)](01-divide-and-conquer-sorting.md)
- [Dynamic Programming (Memoization, Tabulation, State Compression, Space Optimization)](03-dynamic-programming.md)
- [Minimum Spanning Trees](../04-graphs/04-minimum-spanning-trees.md)
- [Shortest Paths](../04-graphs/05-shortest-paths.md)
