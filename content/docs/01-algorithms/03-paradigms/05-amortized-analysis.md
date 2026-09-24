---
title: "Amortized Analysis"
weight: 5
toc: true
---

## What it is

Amortized analysis averages the cost of a sequence of operations over the worst case, rather than analyzing each operation in isolation. It shows that a data structure can have occasional expensive operations (like array resizing) while the average cost per operation remains cheap.

## How it works

A dynamic array starts with a small capacity and doubles it whenever it is full, so a push is usually O(1) but occasionally O(n). Because the doubling happens geometrically, the total cost of `n` pushes is O(n), giving an amortized O(1) per push.

```java
public class DynamicArray {
    private int[] data;
    private int size;

    public DynamicArray() {
        data = new int[1];
        size = 0;
    }

    public void push(int value) {
        if (size == data.length) {
            int[] bigger = new int[data.length * 2];
            System.arraycopy(data, 0, bigger, 0, size);
            data = bigger;
        }
        data[size++] = value;
    }

    public int get(int index) {
        return data[index];
    }
}
```

```c
#include <stdlib.h>

typedef struct {
    int *data;
    int size;
    int capacity;
} DynamicArray;

DynamicArray da_new(void) {
    DynamicArray da;
    da.data = malloc(sizeof(int));
    da.size = 0;
    da.capacity = 1;
    return da;
}

void da_push(DynamicArray *da, int value) {
    if (da->size == da->capacity) {
        da->capacity *= 2;
        da->data = realloc(da->data, sizeof(int) * da->capacity);
    }
    da->data[da->size++] = value;
}
```

```python
class DynamicArray:
    def __init__(self):
        self.data = [None]
        self.size = 0

    def push(self, value):
        if self.size == len(self.data):
            self.data = self.data + [None] * len(self.data)
        self.data[self.size] = value
        self.size += 1

    def get(self, index):
        return self.data[index]
```

```rust
pub struct DynamicArray {
    data: Vec<Option<i32>>,
    size: usize,
}

impl DynamicArray {
    pub fn new() -> Self {
        DynamicArray { data: vec![None], size: 0 }
    }

    pub fn push(&mut self, value: i32) {
        if self.size == self.data.len() {
            self.data.resize(self.data.len() * 2, None);
        }
        self.data[self.size] = Some(value);
        self.size += 1;
    }

    pub fn get(&self, index: usize) -> i32 {
        self.data[index].unwrap()
    }
}
```

```typescript
class DynamicArray {
  private data: number[];
  private size: number;

  constructor() {
    this.data = new Array(1);
    this.size = 0;
  }

  push(value: number): void {
    if (this.size === this.data.length) {
      const bigger = new Array(this.data.length * 2);
      for (let i = 0; i < this.size; i++) bigger[i] = this.data[i];
      this.data = bigger;
    }
    this.data[this.size++] = value;
  }

  get(index: number): number {
    return this.data[index];
  }
}
```

```go
type DynamicArray struct {
    data []int
    size int
}

func NewDynamicArray() *DynamicArray {
    return &DynamicArray{data: make([]int, 1)}
}

func (da *DynamicArray) Push(value int) {
    if da.size == len(da.data) {
        bigger := make([]int, len(da.data)*2)
        copy(bigger, da.data)
        da.data = bigger
    }
    da.data[da.size] = value
    da.size++
}

func (da *DynamicArray) Get(index int) int {
    return da.data[index]
}
```

## Complexity

| Operation | Amortized | Notes |
| --- | --- | --- |
| Dynamic array push | O(1) | geometric doubling |
| Union-find (path compression + union by rank) | O(α(n)) | inverse Ackermann, nearly constant |
| Splay tree | O(log n) | amortized over a sequence of operations |

## When to use

- When a data structure occasionally performs an expensive operation whose cost is balanced by many cheap ones (dynamic arrays, hash table resizing).
- When analyzing union-find operations, where a single find can be costly but a sequence of them is nearly O(1) each.
- When comparing data structures whose worst-case bound is misleading versus their typical sequence cost.

## Alternatives

- **Worst-case analysis**: gives a stricter per-operation guarantee but is overly pessimistic for amortized data structures like dynamic arrays.
- **Average-case analysis over random inputs**: models probabilistic input, unlike amortized analysis which assumes an adversarial sequence of operations.
- **Accounting / potential methods**: are themselves the standard techniques (with the aggregate method) for deriving amortized bounds, not alternatives to the goal.

## Related

- [Dynamic Arrays, Memory Allocation, and Amortized Analysis](../01-linear-data-structures/01-dynamic-arrays.md)
- [Union-Find](../02-search-trees/05-union-find.md)
- [Divide and Conquer Sorting](01-divide-and-conquer-sorting.md)
