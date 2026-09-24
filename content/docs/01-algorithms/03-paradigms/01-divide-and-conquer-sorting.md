---
title: "Divide and Conquer Sorting"
weight: 1
toc: true
---

## What it is

Divide and conquer solves a problem by splitting it into smaller independent subproblems of the same type, solving each recursively, and combining the results. Sorting algorithms built on this strategy (merge sort, quicksort) repeatedly halve the input and merge or partition the sorted halves, giving them predictable O(n log n) average-case performance.

## How it works

Merge sort divides the array into two halves, recursively sorts each half, then merges the two sorted halves into a single sorted sequence. Because merging two sorted halves takes linear time and the recursion tree has O(log n) levels, the total work is O(n log n).

```java
public class MergeSort {
    public static void mergeSort(int[] arr, int left, int right) {
        if (left >= right) return;
        int mid = left + (right - left) / 2;
        mergeSort(arr, left, mid);
        mergeSort(arr, mid + 1, right);
        merge(arr, left, mid, right);
    }

    private static void merge(int[] arr, int left, int mid, int right) {
        int[] tmp = new int[right - left + 1];
        int i = left, j = mid + 1, k = 0;
        while (i <= mid && j <= right) {
            tmp[k++] = arr[i] <= arr[j] ? arr[i++] : arr[j++];
        }
        while (i <= mid) tmp[k++] = arr[i++];
        while (j <= right) tmp[k++] = arr[j++];
        System.arraycopy(tmp, 0, arr, left, tmp.length);
    }
}
```

```c
#include <stdlib.h>

static void merge(int *arr, int left, int mid, int right) {
    int n = right - left + 1;
    int *tmp = malloc(sizeof(int) * n);
    int i = left, j = mid + 1, k = 0;
    while (i <= mid && j <= right)
        tmp[k++] = arr[i] <= arr[j] ? arr[i++] : arr[j++];
    while (i <= mid) tmp[k++] = arr[i++];
    while (j <= right) tmp[k++] = arr[j++];
    for (k = 0; k < n; k++) arr[left + k] = tmp[k];
    free(tmp);
}

void merge_sort(int *arr, int left, int right) {
    if (left >= right) return;
    int mid = left + (right - left) / 2;
    merge_sort(arr, left, mid);
    merge_sort(arr, mid + 1, right);
    merge(arr, left, mid, right);
}
```

```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

```rust
pub fn merge_sort(arr: &mut [i32]) {
    if arr.len() <= 1 {
        return;
    }
    let mid = arr.len() / 2;
    merge_sort(&mut arr[..mid]);
    merge_sort(&mut arr[mid..]);
    let mut tmp = Vec::with_capacity(arr.len());
    let (mut i, mut j) = (0, mid);
    while i < mid && j < arr.len() {
        if arr[i] <= arr[j] {
            tmp.push(arr[i]); i += 1;
        } else {
            tmp.push(arr[j]); j += 1;
        }
    }
    tmp.extend_from_slice(&arr[i..mid]);
    tmp.extend_from_slice(&arr[j..]);
    arr.copy_from_slice(&tmp);
}
```

```typescript
function mergeSort(arr: number[]): number[] {
  if (arr.length <= 1) return arr;
  const mid = Math.floor(arr.length / 2);
  const left = mergeSort(arr.slice(0, mid));
  const right = mergeSort(arr.slice(mid));
  return merge(left, right);
}

function merge(left: number[], right: number[]): number[] {
  const result: number[] = [];
  let i = 0, j = 0;
  while (i < left.length && j < right.length) {
    result.push(left[i] <= right[j] ? left[i++] : right[j++]);
  }
  return result.concat(left.slice(i), right.slice(j));
}
```

```go
func mergeSort(arr []int) []int {
    if len(arr) <= 1 {
        return arr
    }
    mid := len(arr) / 2
    left := mergeSort(arr[:mid])
    right := mergeSort(arr[mid:])
    return merge(left, right)
}

func merge(left, right []int) []int {
    result := make([]int, 0, len(left)+len(right))
    i, j := 0, 0
    for i < len(left) && j < len(right) {
        if left[i] <= right[j] {
            result = append(result, left[i]); i++
        } else {
            result = append(result, right[j]); j++
        }
    }
    result = append(result, left[i:]...)
    result = append(result, right[j:]...)
    return result
}
```

## Complexity

| Algorithm | Time (average) | Time (worst) | Space |
| --- | --- | --- | --- |
| Merge sort | O(n log n) | O(n log n) | O(n) |
| Quicksort | O(n log n) | O(n²) | O(log n) |
| Heapsort | O(n log n) | O(n log n) | O(1) |

## When to use

- When you need a guaranteed O(n log n) sort regardless of input order (merge sort, especially for linked lists or external/stable sorts).
- When average-case speed and in-place sorting matter more than worst-case guarantees (quicksort).
- When the problem naturally splits into independent halves that can be solved recursively (binary search, matrix multiplication, closest pair).

## Alternatives

- **Insertion sort**: simpler and faster on tiny or nearly-sorted inputs, but O(n²) in the worst case.
- **Heapsort**: in-place O(n log n) with O(1) extra space, but not stable and with poorer cache locality than quicksort.
- **Timsort (adaptive)**: exploits existing runs for near-linear time on real-world data, at the cost of extra implementation complexity.

## Related

- [Greedy Algorithms](02-greedy.md)
- [Dynamic Programming](03-dynamic-programming.md)
- [Backtracking](04-backtracking.md)
- [Memory Works (Templates)](../../00-essentials/06-memory-works-templates.md)
