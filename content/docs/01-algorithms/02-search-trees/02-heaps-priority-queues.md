---
title: "Heaps and Priority Queues"
weight: 2
toc: true
---

## What it is
A heap is a complete binary tree satisfying the heap property: in a min-heap every parent is ≤ its children, in a max-heap every parent is ≥ its children. A priority queue is the abstract data type a heap implements, returning the minimum (or maximum) element in O(1) and supporting insert/delete in O(log n).

## How it works
A heap is stored in a flat array: the children of index `i` live at `2i+1` and `2i+2`, its parent at `(i-1)/2`. Insertion appends the new element at the end and "bubbles up" by swapping with its parent until the heap property is restored; extraction removes the root, moves the last element to the root, and "bubbles down" (sifts) it into place by swapping with the smaller (or larger) child.

```java
import java.util.Arrays;

public class MinHeap {
    private int[] heap = new int[16];
    private int size = 0;

    public void insert(int value) {
        if (size == heap.length) heap = Arrays.copyOf(heap, heap.length * 2);
        heap[size] = value;
        int i = size++;
        while (i > 0) {
            int parent = (i - 1) / 2;
            if (heap[parent] <= heap[i]) break;
            int tmp = heap[parent]; heap[parent] = heap[i]; heap[i] = tmp;
            i = parent;
        }
    }

    public int extractMin() {
        if (size == 0) throw new IllegalStateException("empty heap");
        int min = heap[0];
        heap[0] = heap[--size];
        int i = 0;
        while (true) {
            int left = 2 * i + 1, right = 2 * i + 2, smallest = i;
            if (left < size && heap[left] < heap[smallest]) smallest = left;
            if (right < size && heap[right] < heap[smallest]) smallest = right;
            if (smallest == i) break;
            int tmp = heap[i]; heap[i] = heap[smallest]; heap[smallest] = tmp;
            i = smallest;
        }
        return min;
    }

    public int peek() {
        if (size == 0) throw new IllegalStateException("empty heap");
        return heap[0];
    }
}
```

```c
#include <stdlib.h>

typedef struct {
    int *data;
    size_t size;
    size_t capacity;
} MinHeap;

static void heap_swap(int *a, int *b) { int t = *a; *a = *b; *b = t; }

void heap_init(MinHeap *h) {
    h->capacity = 16;
    h->size = 0;
    h->data = malloc(h->capacity * sizeof(int));
}

void heap_insert(MinHeap *h, int value) {
    if (h->size == h->capacity) {
        h->capacity *= 2;
        h->data = realloc(h->data, h->capacity * sizeof(int));
    }
    h->data[h->size] = value;
    size_t i = h->size++;
    while (i > 0) {
        size_t parent = (i - 1) / 2;
        if (h->data[parent] <= h->data[i]) break;
        heap_swap(&h->data[parent], &h->data[i]);
        i = parent;
    }
}

int heap_extract_min(MinHeap *h) {
    int min = h->data[0];
    h->data[0] = h->data[--h->size];
    size_t i = 0;
    while (1) {
        size_t left = 2 * i + 1, right = 2 * i + 2, smallest = i;
        if (left < h->size && h->data[left] < h->data[smallest]) smallest = left;
        if (right < h->size && h->data[right] < h->data[smallest]) smallest = right;
        if (smallest == i) break;
        heap_swap(&h->data[i], &h->data[smallest]);
        i = smallest;
    }
    return min;
}
```

```python
class MinHeap:
    def __init__(self):
        self.heap = []

    def insert(self, value):
        self.heap.append(value)
        i = len(self.heap) - 1
        while i > 0:
            parent = (i - 1) // 2
            if self.heap[parent] <= self.heap[i]:
                break
            self.heap[parent], self.heap[i] = self.heap[i], self.heap[parent]
            i = parent

    def extract_min(self):
        if not self.heap:
            raise IndexError("empty heap")
        minimum = self.heap[0]
        self.heap[0] = self.heap.pop()
        i = 0
        n = len(self.heap)
        while True:
            left, right, smallest = 2 * i + 1, 2 * i + 2, i
            if left < n and self.heap[left] < self.heap[smallest]:
                smallest = left
            if right < n and self.heap[right] < self.heap[smallest]:
                smallest = right
            if smallest == i:
                break
            self.heap[i], self.heap[smallest] = self.heap[smallest], self.heap[i]
            i = smallest
        return minimum

    def peek(self):
        if not self.heap:
            raise IndexError("empty heap")
        return self.heap[0]
```

```rust
pub struct MinHeap {
    data: Vec<i32>,
}

impl MinHeap {
    pub fn new() -> Self {
        MinHeap { data: Vec::new() }
    }

    pub fn insert(&mut self, value: i32) {
        self.data.push(value);
        let mut i = self.data.len() - 1;
        while i > 0 {
            let parent = (i - 1) / 2;
            if self.data[parent] <= self.data[i] {
                break;
            }
            self.data.swap(parent, i);
            i = parent;
        }
    }

    pub fn extract_min(&mut self) -> Option<i32> {
        if self.data.is_empty() {
            return None;
        }
        let min = self.data[0];
        let last = self.data.pop().unwrap();
        if !self.data.is_empty() {
            self.data[0] = last;
            let mut i = 0;
            let n = self.data.len();
            loop {
                let left = 2 * i + 1;
                let right = 2 * i + 2;
                let mut smallest = i;
                if left < n && self.data[left] < self.data[smallest] {
                    smallest = left;
                }
                if right < n && self.data[right] < self.data[smallest] {
                    smallest = right;
                }
                if smallest == i {
                    break;
                }
                self.data.swap(i, smallest);
                i = smallest;
            }
        }
        Some(min)
    }

    pub fn peek(&self) -> Option<i32> {
        self.data.first().copied()
    }
}
```

```typescript
export class MinHeap {
    private heap: number[] = [];

    insert(value: number): void {
        this.heap.push(value);
        let i = this.heap.length - 1;
        while (i > 0) {
            const parent = Math.floor((i - 1) / 2);
            if (this.heap[parent] <= this.heap[i]) break;
            [this.heap[parent], this.heap[i]] = [this.heap[i], this.heap[parent]];
            i = parent;
        }
    }

    extractMin(): number {
        if (this.heap.length === 0) throw new Error("empty heap");
        const min = this.heap[0];
        this.heap[0] = this.heap.pop()!;
        let i = 0;
        const n = this.heap.length;
        while (true) {
            const left = 2 * i + 1, right = 2 * i + 2;
            let smallest = i;
            if (left < n && this.heap[left] < this.heap[smallest]) smallest = left;
            if (right < n && this.heap[right] < this.heap[smallest]) smallest = right;
            if (smallest === i) break;
            [this.heap[i], this.heap[smallest]] = [this.heap[smallest], this.heap[i]];
            i = smallest;
        }
        return min;
    }

    peek(): number {
        if (this.heap.length === 0) throw new Error("empty heap");
        return this.heap[0];
    }
}
```

```go
package heap

type MinHeap struct {
	data []int
}

func (h *MinHeap) Insert(value int) {
	h.data = append(h.data, value)
	i := len(h.data) - 1
	for i > 0 {
		parent := (i - 1) / 2
		if h.data[parent] <= h.data[i] {
			break
		}
		h.data[parent], h.data[i] = h.data[i], h.data[parent]
		i = parent
	}
}

func (h *MinHeap) ExtractMin() (int, bool) {
	if len(h.data) == 0 {
		return 0, false
	}
	min := h.data[0]
	h.data[0] = h.data[len(h.data)-1]
	h.data = h.data[:len(h.data)-1]
	i := 0
	n := len(h.data)
	for {
		left, right, smallest := 2*i+1, 2*i+2, i
		if left < n && h.data[left] < h.data[smallest] {
			smallest = left
		}
		if right < n && h.data[right] < h.data[smallest] {
			smallest = right
		}
		if smallest == i {
			break
		}
		h.data[i], h.data[smallest] = h.data[smallest], h.data[i]
		i = smallest
	}
	return min, true
}

func (h *MinHeap) Peek() (int, bool) {
	if len(h.data) == 0 {
		return 0, false
	}
	return h.data[0], true
}
```

## Complexity
| Operation | Time | Space |
| --- | --- | --- |
| Peek (min/max) | O(1) | O(1) |
| Insert | O(log n) | O(1) |
| Extract-min / delete | O(log n) | O(1) |
| Heapify (build from array) | O(n) | O(1) in-place |
| Heap sort | O(n log n) | O(1) in-place |

Building a heap bottom-up is O(n), not O(n log n), because the cost of sifting down a node is bounded by its subtree height, and most nodes sit near the leaves.

## When to use
- When you repeatedly need the smallest or largest element of a dynamically changing set.
- Implementing Dijkstra's and Prim's algorithms, where extract-min and decrease-key dominate the cost.
- Top-k selection and merging multiple sorted streams.
- Scheduling and task queues ordered by priority rather than arrival time.

## Alternatives
- Balanced BST — supports arbitrary deletion and ordered traversal in O(log n) but with higher constant factors and more complex bookkeeping.
- Unsorted list — O(1) insert but O(n) to find the minimum.
- Fibonacci heap — faster amortized decrease-key for dense graphs, but complex to implement and rarely worth it in practice.

## Related
- [Binary Search Trees](01-binary-search-trees.md)
- [Dynamic Arrays, Memory Allocation, and Amortized Analysis](../01-linear-data-structures/01-dynamic-arrays.md)
