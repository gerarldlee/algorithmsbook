---
title: "Amortized Analysis Techniques (Aggregate, Accounting, and Potential Methods)"
weight: 5
toc: true
---

## What it is

**Amortized analysis** assigns a sequence of operations a total upper bound and divides that bound by the sequence length. It does not average over inputs or assume random behavior: the bound must hold for every valid operation sequence, including an adversarial one.

## How it works

A dynamic array starts with capacity 1 and doubles it when full. Ordinary pushes copy O(n) elements, so a single push can cost O(n), but copies occur at capacities 1, 2, 4, 8, and so on.

The **aggregate method** sums costs across a sequence. The copying costs form the geometric series 1 + 2 + 4 + ... + n/2, which is O(n), so n pushes plus their resizes cost O(n) in total.

The **accounting method** charges 3 units for each push and stores unused charge in an account. The initial capacity contributes 1 unit of starting credit. When an array with size `m` grows, the accumulated credit pays for the O(m) copy and leaves the account with enough credit to cover the next expansion.

The **potential method** assigns a potential to the object and charges an operation its actual cost plus the change in potential. Choosing Φ = 2 × size − capacity + 1 keeps Φ nonnegative and makes the amortized cost of push constant. The stored credit in accounting analysis and the potential in potential analysis play the same mathematical role.

The implementations expose the same `DynamicArray` operations: `new`, `push`, `get`, and `len`. The C result is owned by the caller and must be released with `da_free`.

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
        if (index < 0 || index >= size) throw new IndexOutOfBoundsException();
        return data[index];
    }

    public int len() {
        return size;
    }
}
```

```c
#include <stdbool.h>
#include <stdlib.h>

typedef struct {
    int *data;
    int size;
    int capacity;
} DynamicArray;

DynamicArray da_new(void) {
    DynamicArray result = {malloc(sizeof(int)), 0, 1};
    if (result.data == NULL) abort();
    return result;
}

void da_push(DynamicArray *array, int value) {
    if (array->size == array->capacity) {
        int capacity = array->capacity * 2;
        int *data = malloc((size_t)capacity * sizeof(int));
        if (data == NULL) abort();
        for (int i = 0; i < array->size; i++) data[i] = array->data[i];
        free(array->data);
        array->data = data;
        array->capacity = capacity;
    }
    array->data[array->size++] = value;
}

bool da_get(const DynamicArray *array, int index, int *value) {
    if (index < 0 || index >= array->size) return false;
    *value = array->data[index];
    return true;
}

int da_len(const DynamicArray *array) {
    return array->size;
}

void da_free(DynamicArray *array) {
    free(array->data);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
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
        if index < 0 or index >= self.size:
            raise IndexError()
        return self.data[index]

    def __len__(self):
        return self.size
```

```rust
pub struct DynamicArray {
    data: Vec<Option<i32>>,
    size: usize,
}

impl DynamicArray {
    pub fn new() -> Self {
        DynamicArray {
            data: vec![None],
            size: 0,
        }
    }

    pub fn push(&mut self, value: i32) {
        if self.size == self.data.len() {
            self.data.resize(self.data.len() * 2, None);
        }
        self.data[self.size] = Some(value);
        self.size += 1;
    }

    pub fn get(&self, index: usize) -> Option<i32> {
        if index >= self.size {
            return None;
        }
        self.data[index]
    }

    pub fn len(&self) -> usize {
        self.size
    }
}
```

```typescript
export class DynamicArray {
  private data: number[];
  private size: number;

  constructor() {
    this.data = new Array(1);
    this.size = 0;
  }

  push(value: number): void {
    if (this.size === this.data.length) {
      const bigger = new Array<number>(this.data.length * 2);
      for (let index = 0; index < this.size; index++) bigger[index] = this.data[index];
      this.data = bigger;
    }
    this.data[this.size++] = value;
  }

  get(index: number): number {
    if (index < 0 || index >= this.size) throw new Error();
    return this.data[index];
  }

  len(): number {
    return this.size;
  }
}
```

```go
package amortizedanalysis

type DynamicArray struct {
    data     []int
    size     int
    capacity int
}

func NewDynamicArray() *DynamicArray {
    return &DynamicArray{data: make([]int, 1), capacity: 1}
}

func (array *DynamicArray) Push(value int) {
    if array.size == array.capacity {
        data := make([]int, array.capacity*2)
        copy(data, array.data)
        array.data = data
        array.capacity *= 2
    }
    array.data[array.size] = value
    array.size++
}

func (array *DynamicArray) Get(index int) (int, bool) {
    if index < 0 || index >= array.size {
        return 0, false
    }
    return array.data[index], true
}

func (array *DynamicArray) Len() int {
    return array.size
}
```

## Complexity

| Operation or method | Time | Space or invariant |
| --- | --- | --- |
| Dynamic-array `get` | O(1) worst case | O(1) auxiliary |
| Dynamic-array `push` | O(1) amortized; O(n) worst case for a resize | O(n) total; O(n) temporary during growth |
| n pushes, including all resizes | O(n) total by aggregate, accounting, or potential analysis | O(n) total |
| Union-find with path compression and union by rank | O(α(n)) amortized per operation | O(n) |
| Splay-tree access sequence | O(log n) amortized per operation | O(n) |

## When to use

- Individual operation bounds are pessimistic but a total sequence bound is tight.
- Expensive operations occur only after geometrically increasing numbers of cheap operations.
- A sequence stores credits or a potential to redistribute the cost of occasional work.
- You need a guarantee for adversarial operation sequences rather than an input-distribution assumption.
- You are comparing dynamic structures whose occasional worst cases obscure their guaranteed sequence cost.

## Alternatives

- **Worst-case analysis** — bounds every operation separately and is necessary when callers cannot tolerate one expensive operation.
- **Average-case analysis** — averages over a stated input distribution and does not guarantee behavior for adversarial sequences.
- **Banker's method** — treats used capacity as potential and avoids copying when a large allocation can pay for the unused space.

## Related

- [Dynamic Arrays, Memory Allocation, and Amortized Analysis](../01-linear-data-structures/01-dynamic-arrays.md)
- [Union-Find (Disjoint Set Union)](../02-search-trees/05-union-find.md)
- [Divide-and-Conquer & Advanced Sorting (Quick, Merge, Radix, Counting Sort)](01-divide-and-conquer-sorting.md)
- [Concurrency & Parallel Computing](06-concurrency-parallel-computing.md)
