---
title: "Concepts"
weight: 5
---

These small representations appear repeatedly in the algorithm chapters. Practice converting them
by hand until the place values and invariants feel automatic.

## Number representation

To convert binary to decimal, multiply each bit by its power of two and add the results:

\[
101101_2 = 1\cdot2^5 + 0\cdot2^4 + 1\cdot2^3 + 1\cdot2^2 + 0\cdot2^1 + 1\cdot2^0 = 45_{10}
\]

To convert decimal to binary, repeatedly divide by two and read the remainders from bottom to top.

## Algorithm concepts

- **Invariant** — a property that remains true before and after each loop iteration.
- **State** — the information an algorithm must retain to continue correctly.
- **Base case** — the smallest input a recursive definition solves directly.
- **Recurrence** — an equation that describes a problem in terms of smaller instances.
- **Greedy choice** — a locally best choice that is safe under the problem’s proof conditions.
- **Amortized cost** — the average cost over a sequence of operations, even when individual operations vary.
- **Stable sort** — a sort that preserves the relative order of equal keys.
- **Idempotent operation** — an operation that can be applied repeatedly without changing the result after the first application.

## Related chapters

- [Greedy Algorithms](../01-algorithms/03-paradigms/02-greedy.md)
- [Dynamic Programming](../01-algorithms/03-paradigms/03-dynamic-programming.md)
- [Backtracking](../01-algorithms/03-paradigms/04-backtracking.md)
- [Amortized Analysis Techniques](../01-algorithms/03-paradigms/05-amortized-analysis.md)
- [Divide-and-Conquer & Advanced Sorting](../01-algorithms/03-paradigms/01-divide-and-conquer-sorting.md)
