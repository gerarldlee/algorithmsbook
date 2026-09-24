---
title: "Stacks, Queues, Deques, Ring/Circular Buffers, and Call Stack Mechanics (Tail-Call Optimization, Recursion Frames)"
weight: 3
toc: true
---

## What it is

A stack is a Last-In-First-Out (LIFO) collection, a queue is First-In-First-Out (FIFO), and a deque allows insertion and removal at both ends. A **circular buffer** stores a fixed-capacity sequence in an array and reuses positions after the boundaries wrap around. The same circular-buffer operations can back a stack, queue, or deque.

## How it works

A stack exposes one end: `pushBack` adds a value and `popBack` removes the most recently added value. A queue uses `pushBack` with `popFront`. A deque uses all four end operations. A circular buffer tracks a head index, a capacity, and a size, so it never shifts existing elements when it removes a value.

The implementation below uses a fixed-capacity circular buffer. Every language provides the same logical operations: push and pop at either end, peek at either end, report size, and test emptiness. A full buffer rejects insertion rather than overwriting an unread value.

```java
class CircularBuffer {
    private final int[] data;
    private final int capacity;
    private int head;
    private int size;

    CircularBuffer(int capacity) {
        if (capacity <= 0) throw new IllegalArgumentException();
        this.data = new int[capacity];
        this.capacity = capacity;
    }

    boolean pushFront(int value) {
        if (isFull()) return false;
        head = (head - 1 + capacity) % capacity;
        data[head] = value;
        size++;
        return true;
    }

    boolean pushBack(int value) {
        if (isFull()) return false;
        data[(head + size) % capacity] = value;
        size++;
        return true;
    }

    Integer popFront() {
        if (isEmpty()) return null;
        int value = data[head];
        head = (head + 1) % capacity;
        size--;
        return value;
    }

    Integer popBack() {
        if (isEmpty()) return null;
        int index = (head + size - 1) % capacity;
        int value = data[index];
        size--;
        return value;
    }

    Integer peekFront() {
        return isEmpty() ? null : data[head];
    }

    Integer peekBack() {
        return isEmpty() ? null : data[(head + size - 1) % capacity];
    }

    int size() {
        return size;
    }

    boolean isEmpty() {
        return size == 0;
    }

    boolean isFull() {
        return size == capacity;
    }
}
```

```c
#include <stdbool.h>
#include <stdlib.h>

typedef struct {
    int *data;
    int capacity;
    int head;
    int size;
} CircularBuffer;

void cb_init(CircularBuffer *buffer, int capacity) {
    if (capacity <= 0) abort();
    buffer->data = malloc((size_t)capacity * sizeof(int));
    if (buffer->data == NULL) abort();
    buffer->capacity = capacity;
    buffer->head = 0;
    buffer->size = 0;
}

bool cb_push_front(CircularBuffer *buffer, int value) {
    if (buffer->size == buffer->capacity) return false;
    buffer->head = (buffer->head - 1 + buffer->capacity) % buffer->capacity;
    buffer->data[buffer->head] = value;
    buffer->size++;
    return true;
}

bool cb_push_back(CircularBuffer *buffer, int value) {
    if (buffer->size == buffer->capacity) return false;
    buffer->data[(buffer->head + buffer->size) % buffer->capacity] = value;
    buffer->size++;
    return true;
}

bool cb_pop_front(CircularBuffer *buffer, int *value) {
    if (buffer->size == 0) return false;
    *value = buffer->data[buffer->head];
    buffer->head = (buffer->head + 1) % buffer->capacity;
    buffer->size--;
    return true;
}

bool cb_pop_back(CircularBuffer *buffer, int *value) {
    if (buffer->size == 0) return false;
    int index = (buffer->head + buffer->size - 1) % buffer->capacity;
    *value = buffer->data[index];
    buffer->size--;
    return true;
}

bool cb_peek_front(const CircularBuffer *buffer, int *value) {
    if (buffer->size == 0) return false;
    *value = buffer->data[buffer->head];
    return true;
}

bool cb_peek_back(const CircularBuffer *buffer, int *value) {
    if (buffer->size == 0) return false;
    *value = buffer->data[(buffer->head + buffer->size - 1) % buffer->capacity];
    return true;
}

int cb_size(const CircularBuffer *buffer) {
    return buffer->size;
}

bool cb_is_empty(const CircularBuffer *buffer) {
    return buffer->size == 0;
}

void cb_free(CircularBuffer *buffer) {
    free(buffer->data);
    buffer->data = NULL;
    buffer->capacity = 0;
    buffer->head = 0;
    buffer->size = 0;
}
```

```python
class CircularBuffer:
    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.data = [0] * capacity
        self.capacity = capacity
        self.head = 0
        self.size = 0

    def push_front(self, value):
        if self.is_full():
            return False
        self.head = (self.head - 1 + self.capacity) % self.capacity
        self.data[self.head] = value
        self.size += 1
        return True

    def push_back(self, value):
        if self.is_full():
            return False
        self.data[(self.head + self.size) % self.capacity] = value
        self.size += 1
        return True

    def pop_front(self):
        if self.is_empty():
            return None
        value = self.data[self.head]
        self.head = (self.head + 1) % self.capacity
        self.size -= 1
        return value

    def pop_back(self):
        if self.is_empty():
            return None
        index = (self.head + self.size - 1) % self.capacity
        value = self.data[index]
        self.size -= 1
        return value

    def peek_front(self):
        return None if self.is_empty() else self.data[self.head]

    def peek_back(self):
        if self.is_empty():
            return None
        return self.data[(self.head + self.size - 1) % self.capacity]

    def size(self):
        return self.size

    def is_empty(self):
        return self.size == 0

    def is_full(self):
        return self.size == self.capacity
```

```rust
pub struct CircularBuffer {
    data: Vec<i32>,
    capacity: usize,
    head: usize,
    size: usize,
}

impl CircularBuffer {
    pub fn new(capacity: usize) -> Option<Self> {
        if capacity == 0 {
            return None;
        }
        Some(CircularBuffer {
            data: vec![0; capacity],
            capacity,
            head: 0,
            size: 0,
        })
    }

    pub fn push_front(&mut self, value: i32) -> bool {
        if self.is_full() {
            return false;
        }
        self.head = (self.head + self.capacity - 1) % self.capacity;
        self.data[self.head] = value;
        self.size += 1;
        true
    }

    pub fn push_back(&mut self, value: i32) -> bool {
        if self.is_full() {
            return false;
        }
        self.data[(self.head + self.size) % self.capacity] = value;
        self.size += 1;
        true
    }

    pub fn pop_front(&mut self) -> Option<i32> {
        if self.is_empty() {
            return None;
        }
        let value = self.data[self.head];
        self.head = (self.head + 1) % self.capacity;
        self.size -= 1;
        Some(value)
    }

    pub fn pop_back(&mut self) -> Option<i32> {
        if self.is_empty() {
            return None;
        }
        let index = (self.head + self.size - 1) % self.capacity;
        let value = self.data[index];
        self.size -= 1;
        Some(value)
    }

    pub fn peek_front(&self) -> Option<i32> {
        if self.is_empty() {
            None
        } else {
            Some(self.data[self.head])
        }
    }

    pub fn peek_back(&self) -> Option<i32> {
        if self.is_empty() {
            None
        } else {
            Some(self.data[(self.head + self.size - 1) % self.capacity])
        }
    }

    pub fn size(&self) -> usize {
        self.size
    }

    pub fn is_empty(&self) -> bool {
        self.size == 0
    }

    pub fn is_full(&self) -> bool {
        self.size == self.capacity
    }
}
```

```typescript
class CircularBuffer {
  private data: number[];
  private capacity: number;
  private head = 0;
  private size = 0;

  constructor(capacity: number) {
    if (capacity <= 0) throw new Error("capacity must be positive");
    this.data = new Array(capacity).fill(0);
    this.capacity = capacity;
  }

  pushFront(value: number): boolean {
    if (this.isFull()) return false;
    this.head = (this.head - 1 + this.capacity) % this.capacity;
    this.data[this.head] = value;
    this.size++;
    return true;
  }

  pushBack(value: number): boolean {
    if (this.isFull()) return false;
    this.data[(this.head + this.size) % this.capacity] = value;
    this.size++;
    return true;
  }

  popFront(): number | undefined {
    if (this.isEmpty()) return undefined;
    const value = this.data[this.head];
    this.head = (this.head + 1) % this.capacity;
    this.size--;
    return value;
  }

  popBack(): number | undefined {
    if (this.isEmpty()) return undefined;
    const index = (this.head + this.size - 1) % this.capacity;
    const value = this.data[index];
    this.size--;
    return value;
  }

  peekFront(): number | undefined {
    return this.isEmpty() ? undefined : this.data[this.head];
  }

  peekBack(): number | undefined {
    return this.isEmpty()
      ? undefined
      : this.data[(this.head + this.size - 1) % this.capacity];
  }

  size(): number {
    return this.size;
  }

  isEmpty(): boolean {
    return this.size === 0;
  }

  isFull(): boolean {
    return this.size === this.capacity;
  }
}
```

```go
type CircularBuffer struct {
	data     []int
	capacity int
	head     int
	size     int
}

func NewCircularBuffer(capacity int) *CircularBuffer {
	if capacity <= 0 {
		return nil
	}
	return &CircularBuffer{
		data:     make([]int, capacity),
		capacity: capacity,
	}
}

func (buffer *CircularBuffer) PushFront(value int) bool {
	if buffer.IsFull() {
		return false
	}
	buffer.head = (buffer.head - 1 + buffer.capacity) % buffer.capacity
	buffer.data[buffer.head] = value
	buffer.size++
	return true
}

func (buffer *CircularBuffer) PushBack(value int) bool {
	if buffer.IsFull() {
		return false
	}
	buffer.data[(buffer.head+buffer.size)%buffer.capacity] = value
	buffer.size++
	return true
}

func (buffer *CircularBuffer) PopFront() (int, bool) {
	if buffer.IsEmpty() {
		return 0, false
	}
	value := buffer.data[buffer.head]
	buffer.head = (buffer.head + 1) % buffer.capacity
	buffer.size--
	return value, true
}

func (buffer *CircularBuffer) PopBack() (int, bool) {
	if buffer.IsEmpty() {
		return 0, false
	}
	index := (buffer.head + buffer.size - 1) % buffer.capacity
	value := buffer.data[index]
	buffer.size--
	return value, true
}

func (buffer *CircularBuffer) PeekFront() (int, bool) {
	if buffer.IsEmpty() {
		return 0, false
	}
	return buffer.data[buffer.head], true
}

func (buffer *CircularBuffer) PeekBack() (int, bool) {
	if buffer.IsEmpty() {
		return 0, false
	}
	return buffer.data[(buffer.head+buffer.size-1)%buffer.capacity], true
}

func (buffer *CircularBuffer) Size() int {
	return buffer.size
}

func (buffer *CircularBuffer) IsEmpty() bool {
	return buffer.size == 0
}

func (buffer *CircularBuffer) IsFull() bool {
	return buffer.size == buffer.capacity
}
```

### Interface views

A stack uses `pushBack` and `popBack`; a queue uses `pushBack` and `popFront`; a deque exposes all four end operations. The circular buffer is the storage mechanism underneath those restricted-access views. A linked-list implementation provides the same interface shape with per-node allocation instead of a fixed capacity.

## Complexity

| Operation | Time | Space |
| --- | --- | --- |
| Push or pop at either end | O(1) | O(1) auxiliary |
| Peek at either end | O(1) | O(1) auxiliary |
| Report size or test emptiness | O(1) | O(1) auxiliary |
| Search (unsupported interface) | O(n) | O(1) auxiliary |
| Buffer storage | O(capacity) | O(capacity) |

## When to use

- You need LIFO behavior for recursion, backtracking, expression evaluation, or undo history.
- You need FIFO behavior for breadth-first traversal, task scheduling, or producer-consumer buffering.
- You need fixed-size end operations for streaming data, sensors, network packets, or bounded work queues.

## Alternatives

- **Dynamic array** — supports arbitrary index access and grows automatically, but middle insertion and removal can require O(n) work.
- **Linked list** — provides O(1) operations at known ends, but adds pointer overhead and usually has worse cache locality.
- **Priority queue** — orders values by priority rather than arrival order, typically with O(log n) updates.

## Related

- [Dynamic Arrays, Memory Allocation, and Amortized Analysis](01-dynamic-arrays.md)
- [Linked Lists (Singly, Doubly, Skip Lists)](02-linked-lists.md)
