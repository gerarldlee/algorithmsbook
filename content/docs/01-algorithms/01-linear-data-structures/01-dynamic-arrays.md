---
title: "Dynamic Arrays, Memory Allocation, and Amortized Analysis"
weight: 1
toc: true
---

## What it is

A dynamic array is a contiguous, random-access collection whose capacity grows (and can shrink) automatically as elements are added or removed. Unlike a fixed-size array, it hides the reallocation behind an abstraction, giving you amortized O(1) append at the cost of occasional O(n) resizing when it runs out of space. Dynamic arrays are the substrate of every list type in real languages: Java's `ArrayList`, Python's `list`, C++'s `std::vector`, Rust's `Vec`, and Go's slices.

## How it works

Arrays are a linear, contiguous collection of items or elements of pre-allocated size in the memory.

- you want to store contiguous elements to easily access it
- you already know how many elements to store, before you declare it. (if not, you use a linked list instead)
- you want O(1) access given an index of the middle of the array.  Obviously, head and tail of the array are always O(1) since you know array[0] and array[size-1] already.

Note that arrays are the basic building blocks of all data structures. I will show you that we can derive all data structures from an array as we go along.

Declare an array of type `int`:

```java
// an array always has a size
int[] array = new int[10];
```

Access an element of an array with a specific index:

```java
// get the value of array[5]
int fifthElement = array[5];

// set the value of array[5]
array[5] = 30;
```

Iterate an array:

```java
for (int index=0; index < array.length; index++) {
	int tmp = array[index];
	// do useful stuff with tmp
}
```

## Techniques for iterating through an Array

### Single-pointer approach

How we just iterate an array through its index is also called single pointer.  We use the concept of the array's index as a pointer to its element value.  This is very trivial.

- We can manipulate how we want to increment or decrement its index.
- We can use `while` or `for` loops if we want to access elements in the array *randomly*
- Or an `Iterator` or a simplified `for-each` loop, to iterate through the array or a linked list

Note that ideally, its better to use a `for-each` loop, to prevent bugs such as accidentally deleting an element in the array with `Iterators` or accidentally accessing `iterator.next()`, unless you intentionally want to.

Using the index to access elements in an array or linked list is the most efficient way as its because of O(1) access time.

### Two-pointer approach

We can also access array elements with 2 pointers approach, and is much more efficient than the single pointer.  It can cut the time of iterating over an array in half.

2 pointers mean there will be 2 separate indexes accessing different elements of the array at the same time.  As with the single pointer, the second pointer can also be positioned anywhere in the array that make sense.  e.g. at the last index, at the first index, at the middle, or anywhere.

## Searching for an element in an Array

### Linear search

- We iterate each element, until we found the element we are looking for.

```java
int valueToFind = 4;
for (int index=0; index < array.length; index++) {
	if (array[index] == valueToFind) {
		// we can either return the index of the element, or the value itself
		return index;
	}
}
```

### Binary Search

See the [Memory works (Templates)](../../00-essentials/06-memory-works-templates.md) page for the binary search template.

The "dynamic" part comes from growth by a constant factor. When `push` runs out of capacity, the array is copied into a new buffer of double the size (a common growth factor of 2). Because the expensive copy happens only after a geometrically growing number of cheap pushes, the total cost of `n` pushes is O(n), so each push is O(1) *amortized*. This is the classic amortized-analysis result: charging a constant amount to each operation "pays off" the occasional full-copy.

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
}

void da_push(DynamicArray *a, int value) {        // amortized O(1)
    if (a->size == a->capacity) {
        a->capacity *= 2;
        a->data = realloc(a->data, a->capacity * sizeof(int));
    }
    a->data[a->size++] = value;
}

int da_get(DynamicArray *a, int index) {          // O(1)
    return a->data[index];
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
}

impl DynamicArray {
    pub fn new() -> Self {
        DynamicArray { data: Vec::with_capacity(1) }
    }

    // Vec grows by doubling internally, so push is amortized O(1)
    pub fn push(&mut self, value: i32) {
        self.data.push(value);
    }

    pub fn get(&self, index: usize) -> Option<&i32> {  // O(1)
        self.data.get(index)
    }

    pub fn len(&self) -> usize {
        self.data.len()
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
| Append / pop at end (push) | O(1) amortized | O(1) |
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

- [Linked Lists and Node-Based Structures](02-linked-lists.md)
- [Stacks, Queues, and Deques](03-stacks-queues-deques.md)
- [Binary Search Trees](../02-search-trees/01-binary-search-trees.md)
- [Memory Works (Templates)](../../00-essentials/06-memory-works-templates.md)
