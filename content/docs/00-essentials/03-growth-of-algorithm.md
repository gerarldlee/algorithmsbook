---
title: "Growth of Algorithm"
weight: 3
---

Algorithm growth describes how work and extra memory change as the input size \(n\) increases. The
goal is to compare growth rates, not to predict an exact runtime on every machine.

## Asymptotic notation

Asymptotic notation describes bounds while ignoring constant factors and lower-order terms:

- \(O(f(n))\) is an asymptotic upper bound.
- \(\Omega(f(n))\) is an asymptotic lower bound.
- \(\Theta(f(n))\) is a tight bound when both the upper and lower bounds grow as \(f(n)\).

Worst-case analysis asks for the maximum work over inputs of size \(n\); best-case analysis asks for
the minimum. Average-case analysis requires a stated input distribution, so it should not be
claimed without that assumption.

## Bubble sort example

Bubble sort repeatedly compares adjacent elements and swaps them when they are out of order:

```java
for (int j=0; j<array.length-1; j++) {
    for (int i = 0; i < array.length - j - 1; i++) {
        if (array[i] > array[i + 1]) {
            int tmp = array[i];
            array[i] = array[i + 1];
            array[i + 1] = tmp;
        }
    }
}
```

With an early-exit flag, an already sorted array is the best case: the algorithm makes one pass and
performs no swaps, so it takes \(O(n)\) time. Without that optimization, the best case is still
\(O(n^2)\) because every pass is performed.

With or without early exit, a reverse-sorted array is a worst case and takes \(O(n^2)\) time. Bubble
sort uses \(O(1)\) extra space because it sorts in place.
