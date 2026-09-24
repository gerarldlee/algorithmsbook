---
title: "Dynamic Arrays, Memory Allocation, Custom Allocators, Cache Locality, and Amortized Analysis"
weight: 1
toc: true
---

## What it is

A dynamic array is a contiguous, random-access collection whose capacity grows automatically as elements are appended. Unlike a fixed-size array, it hides reallocation behind an abstraction, giving you amortized O(1) append at the cost of occasional O(n) resizing when capacity is exhausted. The examples in this chapter demonstrate append, indexed access, and size; removal and shrinking policies vary by language. Java's `ArrayList`, Python's `list`, C++'s `std::vector`, Rust's `Vec`, and Go's slices use this contiguous storage model.

## How it works

Arrays are contiguous, indexed collections of values stored in a preallocated block of memory. An array is useful when you need fast indexed access and know an appropriate initial size. A dynamic array adds automatic capacity growth so callers do not manage resizing themselves.

A fixed array and a dynamic array share the same indexing model. Their difference is ownership: the fixed array exposes allocation and capacity, while the dynamic array exposes operations such as `push`, `get`, and `size`.

Declare an array of type `int`:

```java
// an array always has a size
int[] array = new int[10];
```

```c
// an array always has a size
int array[10];
```

```python
# an array always has a size
array = [0] * 10
```

```rust
// an array always has a size
let mut array = [0; 10];
```

```typescript
// an array always has a size
const array = new Array<number>(10).fill(0);
```

```go
package main
// an array always has a size
array := [10]int{}
```

Access an element of an array with a specific index:

```java
// get the value of array[5]
int fifthElement = array[5];

// set the value of array[5]
array[5] = 30;
```

```c
// get the value of array[5]
int fifth_element = array[5];

// set the value of array[5]
array[5] = 30;
```

```python
# get the value of array[5]
fifth_element = array[5]

# set the value of array[5]
array[5] = 30
```

```rust
// get the value of array[5]
let fifth_element = array[5];

// set the value of array[5]
array[5] = 30;
```

```typescript
// get the value of array[5]
const fifthElement = array[5];

// set the value of array[5]
array[5] = 30;
```

```go
package main
// get the value of array[5]
fifthElement := array[5]

// set the value of array[5]
array[5] = 30
```

Iterate an array:

```java
for (int index=0; index < array.length; index++) {
	int tmp = array[index];
	// do useful stuff with tmp
}
```

```c
for (int index = 0; index < 10; index++) {
    int tmp = array[index];
    // do useful stuff with tmp
}
```

```python
for index in range(len(array)):
    tmp = array[index]
    # do useful stuff with tmp
```

```rust
for tmp in array.iter().copied() {
    // do useful stuff with tmp
}
```

```typescript
for (let index = 0; index < array.length; index++) {
    const tmp = array[index];
    // do useful stuff with tmp
}
```

```go
package main
for index := 0; index < len(array); index++ {
    tmp := array[index]
    // do useful stuff with tmp
}
```

### Techniques for iterating through an array

### Single-pointer approach

Single-pointer iteration uses the array index to visit one element at a time. An index-based loop is appropriate when random access matters; a `for-each` loop is often clearer when only sequential access is needed.

The index provides O(1) access to each position, but indexed iteration is not automatically cheaper than an iterator in every language. Choose the form that makes bounds and mutation behavior explicit.

### Two-pointer approach

A two-pointer algorithm maintains two positions and advances them according to a stopping condition. It can reduce work for problems such as finding a pair, scanning a sorted array, or partitioning values, but there is no general guarantee that it is twice as fast as a single-pointer scan.

Place the first pointer at the beginning, the second at the end, or at another position required by the problem. The invariants of the two positions determine when they move.

### Searching for an element in an array

#### Linear search

A linear search visits each element until it finds the target or reaches the end.

```java
public static int linearSearch(int[] array, int valueToFind) {
    for (int index = 0; index < array.length; index++) {
        if (array[index] == valueToFind) {
            return index;
        }
    }
    return -1;
}
```

```c
int da_linear_search(const int *array, int length, int value_to_find) {
    for (int index = 0; index < length; index++) {
        if (array[index] == value_to_find) {
            return index;
        }
    }
    return -1;
}
```

```python
def linear_search(array, value_to_find):
    for index in range(len(array)):
        if array[index] == value_to_find:
            # we can either return the index of the element, or the value itself
            return index
    return -1
```

```rust
fn linear_search(array: &[i32], value_to_find: i32) -> Option<usize> {
    for (index, value) in array.iter().enumerate() {
        if *value == value_to_find {
            // we can either return the index of the element, or the value itself
            return Some(index);
        }
    }
    None
}
```

```typescript
function linearSearch(array: number[], valueToFind: number): number {
    for (let index = 0; index < array.length; index++) {
        if (array[index] === valueToFind) {
            // we can either return the index of the element, or the value itself
            return index;
        }
    }
    return -1;
}
```

```go
package main
func LinearSearch(array []int, valueToFind int) int {
    for index, value := range array {
        if value == valueToFind {
            // we can either return the index of the element, or the value itself
            return index
        }
    }
    return -1
}
```

#### Binary search

See the [Memory works (Templates)](../../00-essentials/06-memory-works-templates.md) page for the binary search template.

### Dynamic growth and amortized analysis

The dynamic part comes from growth by a constant factor. When `push` runs out of capacity, the array is copied into a new buffer of double the size, which is a common growth factor of 2. Because the expensive copy happens only after a geometrically growing number of cheap pushes, the total cost of `n` pushes is O(n), so each push is O(1) *amortized*. This is the classic amortized-analysis result: charging a constant amount to each operation pays for the occasional full copy.

```java
public class DynamicArray {
    private int[] data;
    private int size;

    public DynamicArray() {
        data = new int[1];
        size = 0;
    }

    public void push(int value) {                 // amortized O(1)
        if (size == data.length) {
            resize(data.length * 2);
        }
        data[size++] = value;
    }

    public int get(int index) {                   // O(1)
        if (index < 0 || index >= size) throw new IndexOutOfBoundsException();
        return data[index];
    }

    private void resize(int capacity) {           // O(n), rare
        int[] copy = new int[capacity];
        System.arraycopy(data, 0, copy, 0, size);
        data = copy;
    }

    public int size() { return size; }
}
```

```c
#include <stdlib.h>

typedef struct {
    int *data;
    int size;
    int capacity;
} DynamicArray;

void da_init(DynamicArray *a) {
    a->capacity = 1;
    a->size = 0;
    a->data = malloc(a->capacity * sizeof(int));
    if (a->data == NULL) abort();
}

void da_push(DynamicArray *a, int value) {        // amortized O(1)
    if (a->size == a->capacity) {
        a->capacity *= 2;
        int *grown = realloc(a->data, a->capacity * sizeof(int));
        if (grown == NULL) abort();
        a->data = grown;
    }
    a->data[a->size++] = value;
}

int da_get(DynamicArray *a, int index) {          // O(1)
    if (index < 0 || index >= a->size) return -1;
    return a->data[index];
}

int da_len(const DynamicArray *a) {
    return a->size;
}

void da_free(DynamicArray *a) {
    free(a->data);
}
```

```python
class DynamicArray:
    def __init__(self):
        self.data = [None]
        self.size = 0

    def push(self, value):                        # amortized O(1)
        if self.size == len(self.data):
            self.data = self.data + [None] * len(self.data)
        self.data[self.size] = value
        self.size += 1

    def get(self, index):                         # O(1)
        if index < 0 or index >= self.size:
            raise IndexError("index out of range")
        return self.data[index]

    def __len__(self):
        return self.size
```

```rust
pub struct DynamicArray {
    data: Vec<i32>,
    size: usize,
    capacity: usize,
}

impl DynamicArray {
    pub fn new() -> Self {
        DynamicArray {
            data: vec![0; 1],
            size: 0,
            capacity: 1,
        }
    }

    pub fn push(&mut self, value: i32) {
        if self.size == self.capacity {
            self.resize(self.capacity * 2);
        }
        self.data[self.size] = value;
        self.size += 1;
    }

    pub fn get(&self, index: usize) -> Option<&i32> {
        if index < self.size {
            self.data.get(index)
        } else {
            None
        }
    }

    pub fn len(&self) -> usize {
        self.size
    }

    fn resize(&mut self, capacity: usize) {
        let mut copy = self.data[..self.size].to_vec();
        copy.resize(capacity, 0);
        self.data = copy;
        self.capacity = capacity;
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

    push(value: number): void {                    // amortized O(1)
        if (this.size === this.data.length) {
            this.resize(this.data.length * 2);
        }
        this.data[this.size++] = value;
    }

    get(index: number): number {                   // O(1)
        if (index < 0 || index >= this.size) throw new Error("index out of range");
        return this.data[index];
    }

    private resize(capacity: number): void {       // O(n), rare
        const copy = new Array(capacity);
        for (let i = 0; i < this.size; i++) copy[i] = this.data[i];
        this.data = copy;
    }

    get length(): number { return this.size; }
}
```

```go
package main
type DynamicArray struct {
	data []int
	size int
}

func NewDynamicArray() *DynamicArray {
	return &DynamicArray{data: make([]int, 1), size: 0}
}

func (a *DynamicArray) Push(value int) {           // amortized O(1)
	if a.size == len(a.data) {
		a.resize(len(a.data) * 2)
	}
	a.data[a.size] = value
	a.size++
}

func (a *DynamicArray) Get(index int) int {       // O(1)
	return a.data[index]
}

func (a *DynamicArray) resize(capacity int) {     // O(n), rare
	copySlice := make([]int, capacity)
	for i := 0; i < a.size; i++ {
		copySlice[i] = a.data[i]
	}
	a.data = copySlice
}

func (a *DynamicArray) Len() int { return a.size }
```

## Complexity

| Operation | Time | Space |
| --- | --- | --- |
| Access (read/write by index) | O(1) | O(1) |
| Search (linear) | O(n) | O(1) |
| Search (binary, on sorted array) | O(log n) | O(1) |
| Append at end (`push`) | O(1) amortized | O(1) auxiliary; O(n) temporary during growth |
| Insert / delete at middle | O(n) | O(1) |
| Resize / growth | O(n) (amortized O(1) per push) | O(n) |

## When to use

- You need O(1) random access by index and mostly append/read at the end.
- You know the access pattern is index-based (not frequent middle insert/delete).
- As the default general-purpose list in most languages, when you don't have a stronger reason to pick a linked structure.

## Alternatives

- **Fixed-size array** — no reallocation overhead, but you must know the size up front and cannot grow.
- **Linked list** — O(1) insert/delete at arbitrary positions, but O(n) access and pointer overhead per node.
- **Unrolled/deque (ring buffer)** — amortized O(1) push/pop at both ends, but loses guaranteed contiguous memory guarantees in some implementations.

## Related

- [Linked Lists (Singly, Doubly, Skip Lists)](02-linked-lists.md)
- [Stacks, Queues, Deques, and Ring/Circular Buffers](03-stacks-queues-deques.md)
- [Binary Search Trees](../02-search-trees/01-binary-search-trees.md)
- [Hash Tables: Hash Functions, Collision Resolution, and Universal Hashing](04-hash-tables.md)
- [Bitwise Algorithms, Bitsets, and Bloom Filters](05-bitwise-bloom-filters.md)
- [Divide-and-Conquer & Advanced Sorting (Quick, Merge, Radix, Counting Sort)](../03-paradigms/01-divide-and-conquer-sorting.md)
- [Amortized Analysis Techniques (Aggregate, Accounting, and Potential Methods)](../03-paradigms/05-amortized-analysis.md)
