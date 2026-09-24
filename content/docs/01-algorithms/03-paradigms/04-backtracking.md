---
title: "Backtracking"
weight: 4
toc: true
---

## What it is

Backtracking is a systematic, depth-first search over the space of candidate solutions that abandons ("backtracks") a partial solution as soon as it is determined to be invalid. It is the standard technique for constraint-satisfaction and combinatorial search problems such as N-Queens, Sudoku, and generating permutations or subsets.

## How it works

The N-Queens solver places one queen per row, trying each column in turn. At each step it checks whether the current placement attacks any previously placed queen; if not, it recurses to the next row, and otherwise it backtracks and tries the next column.

```java
import java.util.*;

public class NQueens {
    public int solve(int n) {
        return backtrack(n, 0, new int[n]);
    }

    private int backtrack(int n, int row, int[] queens) {
        if (row == n) return 1;
        int total = 0;
        for (int col = 0; col < n; col++) {
            if (isValid(queens, row, col)) {
                queens[row] = col;
                total += backtrack(n, row + 1, queens);
            }
        }
        return total;
    }

    private boolean isValid(int[] queens, int row, int col) {
        for (int i = 0; i < row; i++) {
            int diff = Math.abs(col - queens[i]);
            if (diff == 0 || diff == row - i) return false;
        }
        return true;
    }
}
```

```c
#include <stdlib.h>
#include <stdbool.h>

static bool is_valid(int *queens, int row, int col) {
    for (int i = 0; i < row; i++) {
        int diff = abs(col - queens[i]);
        if (diff == 0 || diff == row - i) return false;
    }
    return true;
}

static int backtrack(int n, int row, int *queens) {
    if (row == n) return 1;
    int total = 0;
    for (int col = 0; col < n; col++) {
        if (is_valid(queens, row, col)) {
            queens[row] = col;
            total += backtrack(n, row + 1, queens);
        }
    }
    return total;
}

int n_queens_count(int n) {
    int *queens = malloc(n * sizeof(int));
    int count = backtrack(n, 0, queens);
    free(queens);
    return count;
}
```

```python
def n_queens_count(n):
    def is_valid(queens, row, col):
        for i in range(row):
            diff = abs(col - queens[i])
            if diff == 0 or diff == row - i:
                return False
        return True

    def backtrack(row, queens):
        if row == n:
            return 1
        total = 0
        for col in range(n):
            if is_valid(queens, row, col):
                queens[row] = col
                total += backtrack(row + 1, queens)
        return total

    return backtrack(0, [0] * n)
```

```rust
pub fn n_queens_count(n: usize) -> usize {
    fn is_valid(queens: &[usize], row: usize, col: usize) -> bool {
        for i in 0..row {
            let diff = (col as isize - queens[i] as isize).abs();
            if diff == 0 || diff as usize == row - i {
                return false;
            }
        }
        true
    }

    fn backtrack(n: usize, row: usize, queens: &mut [usize]) -> usize {
        if row == n {
            return 1;
        }
        let mut total = 0;
        for col in 0..n {
            if is_valid(queens, row, col) {
                queens[row] = col;
                total += backtrack(n, row + 1, queens);
            }
        }
        total
    }

    backtrack(n, 0, &mut vec![0; n])
}
```

```typescript
function nQueensCount(n: number): number {
  function isValid(queens: number[], row: number, col: number): boolean {
    for (let i = 0; i < row; i++) {
      const diff = Math.abs(col - queens[i]);
      if (diff === 0 || diff === row - i) return false;
    }
    return true;
  }

  function backtrack(row: number, queens: number[]): number {
    if (row === n) return 1;
    let total = 0;
    for (let col = 0; col < n; col++) {
      if (isValid(queens, row, col)) {
        queens[row] = col;
        total += backtrack(row + 1, queens);
      }
    }
    return total;
  }

  return backtrack(0, new Array(n).fill(0));
}
```

```go
func nQueensCount(n int) int {
    queens := make([]int, n)
    isValid := func(row, col int) bool {
        for i := 0; i < row; i++ {
            diff := col - queens[i]
            if diff < 0 {
                diff = -diff
            }
            if diff == 0 || diff == row-i {
                return false
            }
        }
        return true
    }
    var backtrack func(row int) int
    backtrack = func(row int) int {
        if row == n {
            return 1
        }
        total := 0
        for col := 0; col < n; col++ {
            if isValid(row, col) {
                queens[row] = col
                total += backtrack(row + 1)
            }
        }
        return total
    }
    return backtrack(0)
}
```

## Complexity

| Algorithm | Time (worst) | Space |
| --- | --- | --- |
| N-Queens | O(n!) | O(n) |
| General backtracking | O(b^d) | O(d) |

(Here `b` is the branching factor and `d` the depth of the search tree.)

## When to use

- When you must enumerate all valid solutions (permutations, subsets, combinations) or find any solution to a constraint-satisfaction problem.
- When the search space is large but pruning by constraints can eliminate most branches early (N-Queens, Sudoku, graph coloring).
- When no polynomial-time algorithm is known and the input size is small enough for exhaustive search.

## Alternatives

- **Dynamic programming**: replaces repeated overlapping subproblems with a table, but requires the problem to have optimal substructure.
- **Branch and bound**: adds a cost bound to prune the search tree and find optima faster, at the cost of computing the bound.
- **Local search / heuristic**: finds a good (not necessarily optimal) solution quickly for large instances where exhaustive search is infeasible.

## Related

- [Divide and Conquer Sorting](01-divide-and-conquer-sorting.md)
- [Dynamic Programming](03-dynamic-programming.md)
- [Memory Works (Templates)](../../00-essentials/06-memory-works-templates.md)
