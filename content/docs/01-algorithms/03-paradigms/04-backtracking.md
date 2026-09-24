---
title: "Backtracking, Branch-and-Bound, and Constraint Satisfaction Problems"
weight: 4
toc: true
---

## What it is

**Backtracking** explores a decision tree depth first, places a choice, and undoes that choice when it violates a constraint or cannot lead to a complete solution. **Constraint satisfaction** organizes variables, domains, and constraints; N-Queens is a constraint-satisfaction problem in which each row and column contains one queen and no two queens share a diagonal.

## How it works

The N-Queens solver places one queen in each row. It tries each unused column, rejects a position that attacks an earlier queen, recursively fills the next row, and backtracks when every column fails. Counting valid complete boards explores the same search while accumulating one for each complete assignment.

**Branch and bound** adds an optimistic cost estimate to backtracking. The assignment solver processes agents in order and tries every unused task. Its bound is the current cost plus, for each unassigned agent, the cheapest unused task that could be assigned to it. If that lower bound cannot improve the best complete assignment, the branch is pruned. The remaining-row minima make the bound admissible: they never overestimate the cheapest completion.

The same two operations appear in every implementation: `NQueens.count` returns the number of valid boards, and `Assignment.solve` returns a minimum-cost one-to-one assignment and its cost. The assignment operation accepts a nonempty square cost matrix with nonnegative costs.

```java
import java.util.Arrays;

public class NQueens {
    public static long count(int n) {
        if (n < 0) throw new IllegalArgumentException();
        return search(n, 0, new int[n]);
    }

    private static long search(int n, int row, int[] queens) {
        if (row == n) return 1;
        long total = 0;
        for (int column = 0; column < n; column++) {
            if (isValid(queens, row, column)) {
                queens[row] = column;
                total += search(n, row + 1, queens);
            }
        }
        return total;
    }

    private static boolean isValid(int[] queens, int row, int column) {
        for (int previous = 0; previous < row; previous++) {
            int difference = Math.abs(column - queens[previous]);
            if (difference == 0 || difference == row - previous) return false;
        }
        return true;
    }
}

class Assignment {
    public record Result(int[] assignment, long cost) {}

    public static Result solve(int[][] costs) {
        int n = costs.length;
        for (int[] row : costs) {
            if (row.length != n) throw new IllegalArgumentException();
        }
        int[] current = new int[n];
        int[] best = new int[n];
        boolean[] used = new boolean[n];
        search(0, 0, 0, costs, current, best, used);
        return new Result(best, cost(best, costs));
    }

    private static void search(int n, int row, long cost, int[][] costs, int[] current, int[] best, boolean[] used) {
        if (row == n) {
            if (best[0] < 0 || cost < cost(best, costs)) System.arraycopy(current, 0, best, 0, n);
            return;
        }
        long lowerBound = cost + remainingMinimum(row, n, costs, used);
        if (best[0] >= 0 && lowerBound >= cost(best, costs)) return;
        for (int task = 0; task < n; task++) {
            if (used[task]) continue;
            used[task] = true;
            current[row] = task;
            search(n, row + 1, cost + costs[row][task], costs, current, best, used);
            used[task] = false;
        }
    }

    private static long remainingMinimum(int row, int n, int[][] costs, boolean[] used) {
        long total = 0;
        for (int agent = row; agent < n; agent++) {
            long minimum = Long.MAX_VALUE;
            for (int task = 0; task < n; task++) {
                if (!used[task] && costs[agent][task] < minimum) minimum = costs[agent][task];
            }
            if (minimum == Long.MAX_VALUE) return Long.MAX_VALUE;
            total += minimum;
        }
        return total;
    }

    private static long cost(int[] assignment, int[][] costs) {
        long total = 0;
        for (int agent = 0; agent < assignment.length; agent++) total += costs[agent][assignment[agent]];
        return total;
    }
}
```

```c
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>
#include <limits.h>

typedef long long AssignmentCost;

static bool n_queens_valid(const int *queens, int row, int column) {
    for (int previous = 0; previous < row; previous++) {
        int difference = column - queens[previous];
        if (difference < 0) difference = -difference;
        if (difference == 0 || difference == row - previous) return false;
    }
    return true;
}

static long long n_queens_search(int n, int row, int *queens) {
    if (row == n) return 1;
    long long total = 0;
    for (int column = 0; column < n; column++) {
        if (n_queens_valid(queens, row, column)) {
            queens[row] = column;
            total += n_queens_search(n, row + 1, queens);
        }
    }
    return total;
}

long long n_queens_count(int n) {
    if (n < 0) return 0;
    int *queens = malloc((size_t)n * sizeof(int));
    if (n > 0 && queens == NULL) abort();
    long long result = n_queens_search(n, 0, queens);
    free(queens);
    return result;
}

static AssignmentCost assignment_cost(const int *assignment, int n, const int *costs) {
    AssignmentCost total = 0;
    for (int agent = 0; agent < n; agent++) total += costs[agent * n + assignment[agent]];
    return total;
}

static AssignmentCost remaining_minimum(int row, int n, const int *costs, const bool *used) {
    AssignmentCost total = 0;
    for (int agent = row; agent < n; agent++) {
        AssignmentCost minimum = LLONG_MAX;
        for (int task = 0; task < n; task++) {
            AssignmentCost candidate = costs[agent * n + task];
            if (!used[task] && candidate < minimum) minimum = candidate;
        }
        if (minimum == LLONG_MAX) return LLONG_MAX;
        total += minimum;
    }
    return total;
}

static void assignment_search(int n, int row, AssignmentCost cost, const int *costs, int *current, int *best, bool *used) {
    if (row == n) {
        if (best[0] < 0 || cost < assignment_cost(best, n, costs)) {
            for (int agent = 0; agent < n; agent++) best[agent] = current[agent];
        }
        return;
    }
    AssignmentCost lower_bound = cost + remaining_minimum(row, n, costs, used);
    if (best[0] >= 0 && lower_bound >= assignment_cost(best, n, costs)) return;
    for (int task = 0; task < n; task++) {
        if (used[task]) continue;
        used[task] = true;
        current[row] = task;
        assignment_search(n, row + 1, cost + costs[row * n + task], costs, current, best, used);
        used[task] = false;
    }
}

AssignmentCost assignment_solve(int n, const int *costs, int *assignment) {
    if (n < 0) return -1;
    int *current = malloc((size_t)n * sizeof(int));
    bool *used = calloc((size_t)n, sizeof(bool));
    if (n > 0 && (current == NULL || used == NULL)) abort();
    for (int agent = 0; agent < n; agent++) current[agent] = -1;
    assignment_search(n, 0, 0, costs, current, assignment, used);
    AssignmentCost result = assignment_cost(assignment, n, costs);
    free(current);
    free(used);
    return result;
}
```

```python
class NQueens:
    @staticmethod
    def count(n):
        if n < 0:
            raise ValueError()

        def is_valid(queens, row, column):
            for previous in range(row):
                difference = abs(column - queens[previous])
                if difference == 0 or difference == row - previous:
                    return False
            return True

        def search(row, queens):
            if row == n:
                return 1
            total = 0
            for column in range(n):
                if is_valid(queens, row, column):
                    queens[row] = column
                    total += search(row + 1, queens)
            return total

        return search(0, [0] * n)


class Assignment:
    @staticmethod
    def solve(costs):
        n = len(costs)
        if any(len(row) != n for row in costs):
            raise ValueError()
        current = [-1] * n
        best = [-1] * n
        used = [False] * n

        def total(assignment):
            return sum(costs[agent][assignment[agent]] for agent in range(n))

        def remaining_minimum(row):
            result = 0
            for agent in range(row, n):
                available = [costs[agent][task] for task in range(n) if not used[task]]
                if not available:
                    return float("inf")
                result += min(available)
            return result

        def search(row, cost):
            nonlocal best
            if row == n:
                if best[0] < 0 or cost < total(best):
                    best = current.copy()
                return
            lower_bound = cost + remaining_minimum(row)
            if best[0] >= 0 and lower_bound >= total(best):
                return
            for task in range(n):
                if used[task]:
                    continue
                used[task] = True
                current[row] = task
                search(row + 1, cost + costs[row][task])
                used[task] = False

        search(0, 0)
        return best, total(best)
```

```rust
pub struct NQueens;

impl NQueens {
    pub fn count(n: i32) -> i64 {
        if n < 0 {
            return 0;
        }
        Self::search(n as usize, 0, &mut vec![0; n as usize])
    }

    fn is_valid(queens: &[usize], row: usize, column: usize) -> bool {
        for previous in 0..row {
            let difference = column.abs_diff(queens[previous]);
            if difference == 0 || difference == row - previous {
                return false;
            }
        }
        true
    }

    fn search(n: usize, row: usize, queens: &mut [usize]) -> i64 {
        if row == n {
            return 1;
        }
        let mut total = 0;
        for column in 0..n {
            if Self::is_valid(queens, row, column) {
                queens[row] = column;
                total += Self::search(n, row + 1, queens);
            }
        }
        total
    }
}

pub struct Assignment;

pub struct AssignmentResult {
    pub assignment: Vec<usize>,
    pub cost: i64,
}

impl Assignment {
    pub fn solve(costs: &[Vec<i64>]) -> AssignmentResult {
        let n = costs.len();
        let mut current = vec![0; n];
        let mut best = vec![usize::MAX; n];
        let mut used = vec![false; n];
        Self::search(0, 0, costs, &mut current, &mut best, &mut used);
        let cost = Self::total(&best, costs);
        AssignmentResult { assignment: best, cost }
    }

    fn total(assignment: &[usize], costs: &[Vec<i64>]) -> i64 {
        assignment
            .iter()
            .enumerate()
            .map(|(agent, &task)| costs[agent][task])
            .sum()
    }

    fn best_cost(assignment: &[usize], costs: &[Vec<i64>]) -> Option<i64> {
        if assignment.first() == Some(&usize::MAX) {
            None
        } else {
            Some(Self::total(assignment, costs))
        }
    }

    fn remaining_minimum(row: usize, costs: &[Vec<i64>], used: &[bool]) -> Option<i64> {
        let mut total = 0;
        for agent in row..costs.len() {
            let minimum = costs[agent]
                .iter()
                .enumerate()
                .filter(|(task, _)| !used[*task])
                .map(|(_, &cost)| cost)
                .min()?;
            total += minimum;
        }
        Some(total)
    }

    fn search(
        row: usize,
        cost: i64,
        costs: &[Vec<i64>],
        current: &mut [usize],
        best: &mut [usize],
        used: &mut [bool],
    ) {
        let n = costs.len();
        if row == n {
            let should_replace = Self::best_cost(best, costs)
                .map_or(true, |best_cost| cost < best_cost);
            if should_replace {
                best.copy_from_slice(current);
            }
            return;
        }
        let Some(remaining) = Self::remaining_minimum(row, costs, used) else {
            return;
        };
        if let Some(best_cost) = Self::best_cost(best, costs) {
            if cost + remaining >= best_cost {
                return;
            }
        }
        for task in 0..n {
            if used[task] {
                continue;
            }
            used[task] = true;
            current[row] = task;
            Self::search(row + 1, cost + costs[row][task], costs, current, best, used);
            used[task] = false;
        }
    }
}
```

```typescript
export class NQueens {
  static count(n: number): number {
    if (n < 0) throw new Error();
    const search = (row: number, queens: number[]): number => {
      if (row === n) return 1;
      let total = 0;
      for (let column = 0; column < n; column++) {
        let valid = true;
        for (let previous = 0; previous < row; previous++) {
          const difference = Math.abs(column - queens[previous]);
          if (difference === 0 || difference === row - previous) {
            valid = false;
            break;
          }
        }
        if (valid) {
          queens[row] = column;
          total += search(row + 1, queens);
        }
      }
      return total;
    };
    return search(0, new Array(n).fill(0));
  }
}

export class Assignment {
  static solve(costs: number[][]): { assignment: number[]; cost: number } {
    const n = costs.length;
    if (costs.some((row) => row.length !== n)) throw new Error();
    const current = new Array<number>(n).fill(-1);
    const best = new Array<number>(n).fill(-1);
    const used = new Array<boolean>(n).fill(false);
    const total = (assignment: number[]) =>
      assignment.reduce((sum, task, agent) => sum + costs[agent][task], 0);
    const remainingMinimum = (row: number): number => {
      let result = 0;
      for (let agent = row; agent < n; agent++) {
        const available: number[] = [];
        for (let task = 0; task < n; task++) if (!used[task]) available.push(costs[agent][task]);
        if (available.length === 0) return Infinity;
        result += Math.min(...available);
      }
      return result;
    };
    const search = (row: number, cost: number): void => {
      if (row === n) {
        if (best[0] < 0 || cost < total(best)) {
          for (let agent = 0; agent < n; agent++) best[agent] = current[agent];
        }
        return;
      }
      const lowerBound = cost + remainingMinimum(row);
      if (best[0] >= 0 && lowerBound >= total(best)) return;
      for (let task = 0; task < n; task++) {
        if (used[task]) continue;
        used[task] = true;
        current[row] = task;
        search(row + 1, cost + costs[row][task]);
        used[task] = false;
      }
    };
    search(0, 0);
    return { assignment: best, cost: total(best) };
  }
}
```

```go
package backtracking

type NQueens struct{}

func (NQueens) Count(n int) int64 {
    if n < 0 {
        return 0
    }
    queens := make([]int, n)
    var search func(int) int64
    search = func(row int) int64 {
        if row == n {
            return 1
        }
        var total int64
        for column := 0; column < n; column++ {
            valid := true
            for previous := 0; previous < row; previous++ {
                difference := column - queens[previous]
                if difference < 0 {
                    difference = -difference
                }
                if difference == 0 || difference == row-previous {
                    valid = false
                    break
                }
            }
            if valid {
                queens[row] = column
                total += search(row + 1)
            }
        }
        return total
    }
    return search(0)
}

type Assignment struct{}

func (Assignment) Solve(costs [][]int) ([]int, int64) {
    n := len(costs)
    current := make([]int, n)
    best := make([]int, n)
    used := make([]bool, n)
    for agent := 0; agent < n; agent++ {
        current[agent] = -1
        best[agent] = -1
    }
    total := func(assignment []int) int64 {
        var result int64
        for agent, task := range assignment {
            result += int64(costs[agent][task])
        }
        return result
    }
    var search func(int, int64)
    search = func(row int, cost int64) {
        if row == n {
            if best[0] < 0 || cost < total(best) {
                copy(best, current)
            }
            return
        }
        var remaining int64
        for agent := row; agent < n; agent++ {
            minimum := int64(-1)
            for task := 0; task < n; task++ {
                candidate := int64(costs[agent][task])
                if !used[task] && (minimum < 0 || candidate < minimum) {
                    minimum = candidate
                }
            }
            if minimum < 0 {
                return
            }
            remaining += minimum
        }
        if best[0] >= 0 && cost+remaining >= total(best) {
            return
        }
        for task := 0; task < n; task++ {
            if used[task] {
                continue
            }
            used[task] = true
            current[row] = task
            search(row+1, cost+int64(costs[row][task]))
            used[task] = false
        }
    }
    search(0, 0)
    return best, total(best)
}
```

## Complexity

| Algorithm | Worst-case time | Space |
| --- | --- | --- |
| N-Queens counting | O(n!) | O(n) |
| Assignment branch and bound | O(n² · n!) | O(n) |
| General backtracking | O(bᵈ) | O(d) |

A bound can reduce the practical search but cannot change the worst-case bound. Here, `b` is the branching factor and `d` is the tree depth; the assignment implementation spends O(n²) work computing its bound at a node.

## When to use

- You must enumerate valid solutions or find a complete solution under explicit constraints.
- A partial assignment can reveal that no completion is possible.
- The branching factor or input size is small enough for depth-first search.
- You can compute an admissible lower bound to prune an optimization search.
- No more efficient special-purpose algorithm applies to the problem instance.

## Alternatives

- **Dynamic programming** — merges equivalent states in a recurrence, but requires a compact state representation and can use more memory.
- **Constraint programming solver** — propagates domains and constraints declaratively, but introduces solver-specific modeling and search behavior.
- **Heuristic search** — finds a feasible or approximate solution quickly on large instances, but does not guarantee the optimum.

## Related

- [Divide-and-Conquer & Advanced Sorting (Quick, Merge, Radix, Counting Sort)](01-divide-and-conquer-sorting.md)
- [Dynamic Programming (Memoization, Tabulation, State Compression, Space Optimization)](03-dynamic-programming.md)
- [Greedy Choice Paradigms & Interval Scheduling](02-greedy.md)
- [Memory Works (Templates)](../../00-essentials/06-memory-works-templates.md)
