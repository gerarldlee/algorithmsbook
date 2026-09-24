---
title: "Stacks, Queues, and Deques"
weight: 3
toc: true
---

## What it is

A stack is a Last-In-First-Out (LIFO) collection: only the most recently added element is accessible, and push/pop happen at the same "top" end. A queue is First-In-First-Out (FIFO): you enqueue at the back and dequeue from the front. A deque (double-ended queue) combines both, allowing O(1) insertion and removal at either end. All three are restricted-access interfaces built on top of an array or a linked list.

## How it works

## Stacks

A stack is a linked list like data structure that follows the LIFO rule.  We can visualize this as vertical or horizontal, it does not matter, both are correct.  Last element added, is the first one removed.

## Queues

A queue is also a linked list like data structure that follows the FIFO rule.  The first element added to it, becomes the top most element in it, therefore it is the one that's removed.  The last element added is the last to be removed.

A stack enforces LIFO by exposing only `push` (add to top) and `pop` (remove from top); a queue enforces FIFO with `enqueue` (add to back) and `dequeue` (remove from front). Deques add `pushFront`/`popFront`/`pushBack`/`popBack`. Because only the ends are touched, every operation is O(1):

```java
import java.util.ArrayDeque;

// Stack (LIFO): push on top, pop off top
class Stack<T> {
    private final ArrayDeque<T> data = new ArrayDeque<>();
    void push(T value) { data.addLast(value); }    // O(1)
    T pop() { return data.removeLast(); }          // O(1)
    T peek() { return data.peekLast(); }           // O(1)
    boolean isEmpty() { return data.isEmpty(); }
}

// Queue (FIFO): enqueue at back, dequeue from front
class Queue<T> {
    private final ArrayDeque<T> data = new ArrayDeque<>();
    void enqueue(T value) { data.addLast(value); } // O(1)
    T dequeue() { return data.removeFirst(); }     // O(1)
    T peek() { return data.peekFirst(); }          // O(1)
    boolean isEmpty() { return data.isEmpty(); }
}
```

```c
#include <stdlib.h>

// --- Stack (LIFO) as a singly linked list ---
typedef struct SNode {
    int value;
    struct SNode *next;
} SNode;

typedef struct {
    SNode *top;
} Stack;

void stack_push(Stack *s, int value) {            // O(1)
    SNode *n = malloc(sizeof(SNode));
    n->value = value;
    n->next = s->top;
    s->top = n;
}

int stack_pop(Stack *s) {                         // O(1)
    SNode *n = s->top;
    int value = n->value;
    s->top = n->next;
    free(n);
    return value;
}

// --- Queue (FIFO) with head/tail pointers ---
typedef struct QNode {
    int value;
    struct QNode *next;
} QNode;

typedef struct {
    QNode *head, *tail;
} Queue;

void queue_enqueue(Queue *q, int value) {         // O(1)
    QNode *n = malloc(sizeof(QNode));
    n->value = value;
    n->next = NULL;
    if (q->tail) q->tail->next = n; else q->head = n;
    q->tail = n;
}

int queue_dequeue(Queue *q) {                     // O(1)
    QNode *n = q->head;
    int value = n->value;
    q->head = n->next;
    if (!q->head) q->tail = NULL;
    free(n);
    return value;
}
```

```python
from collections import deque

class Stack:
    """Stack (LIFO): last in, first out."""
    def __init__(self):
        self.data = []
    def push(self, value):         # O(1) amortized
        self.data.append(value)
    def pop(self):                 # O(1)
        return self.data.pop()
    def peek(self):
        return self.data[-1]
    def is_empty(self):
        return len(self.data) == 0

class Queue:
    """Queue (FIFO): first in, first out."""
    def __init__(self):
        self.data = deque()
    def enqueue(self, value):      # O(1)
        self.data.append(value)
    def dequeue(self):             # O(1)
        return self.data.popleft()
    def peek(self):
        return self.data[0]
    def is_empty(self):
        return len(self.data) == 0
```

```rust
use std::collections::VecDeque;

pub struct Stack<T> {
    data: Vec<T>,
}

impl<T> Stack<T> {
    pub fn new() -> Self { Stack { data: Vec::new() } }
    pub fn push(&mut self, value: T) { self.data.push(value); }  // O(1) amortized
    pub fn pop(&mut self) -> Option<T> { self.data.pop() }        // O(1)
    pub fn peek(&self) -> Option<&T> { self.data.last() }
    pub fn is_empty(&self) -> bool { self.data.is_empty() }
}

pub struct Queue<T> {
    data: VecDeque<T>,
}

impl<T> Queue<T> {
    pub fn new() -> Self { Queue { data: VecDeque::new() } }
    pub fn enqueue(&mut self, value: T) { self.data.push_back(value); } // O(1)
    pub fn dequeue(&mut self) -> Option<T> { self.data.pop_front() }     // O(1)
    pub fn peek(&self) -> Option<&T> { self.data.front() }
    pub fn is_empty(&self) -> bool { self.data.is_empty() }
}
```

```typescript
class Stack<T> {
    private data: T[] = [];
    push(value: T): void { this.data.push(value); }     // O(1) amortized
    pop(): T | undefined { return this.data.pop(); }    // O(1)
    peek(): T | undefined { return this.data[this.data.length - 1]; }
    get isEmpty(): boolean { return this.data.length === 0; }
}

class Queue<T> {
    private data: T[] = [];
    private head = 0;
    enqueue(value: T): void { this.data.push(value); }  // O(1)
    dequeue(): T | undefined {                          // O(1) amortized
        if (this.head >= this.data.length) return undefined;
        const value = this.data[this.head++];
        if (this.head > 256 && this.head * 2 >= this.data.length) {
            this.data = this.data.slice(this.head);
            this.head = 0;
        }
        return value;
    }
    peek(): T | undefined { return this.data[this.head]; }
    get isEmpty(): boolean { return this.head >= this.data.length; }
}
```

```go
type Stack struct {
	data []int
}

func (s *Stack) Push(value int) { s.data = append(s.data, value) } // O(1) amortized
func (s *Stack) Pop() int {
	v := s.data[len(s.data)-1]
	s.data = s.data[:len(s.data)-1]
	return v
}
func (s *Stack) Peek() int { return s.data[len(s.data)-1] }
func (s *Stack) IsEmpty() bool { return len(s.data) == 0 }

type Queue struct {
	data []int
	head int
}

func (q *Queue) Enqueue(value int) { q.data = append(q.data, value) } // O(1)
func (q *Queue) Dequeue() int {                                       // O(1) amortized
	v := q.data[q.head]
	q.head++
	if q.head > 256 && q.head*2 >= len(q.data) {
		q.data = q.data[q.head:]
		q.head = 0
	}
	return v
}
func (q *Queue) Peek() int { return q.data[q.head] }
func (q *Queue) IsEmpty() bool { return q.head >= len(q.data) }
```

## Complexity

| Operation | Time | Space |
| --- | --- | --- |
| Stack push | O(1) amortized | O(1) |
| Stack pop / peek | O(1) | O(1) |
| Queue enqueue | O(1) | O(1) |
| Queue dequeue / peek | O(1) | O(1) |
| Deque push/pop at either end | O(1) | O(1) |
| Search (unsupported interface) | O(n) | O(1) |

## When to use

- **Stack**: undo/redo, function call frames, expression/balanced-parenthesis evaluation, depth-first traversal, backtracking.
- **Queue**: breadth-first traversal, task/job scheduling, buffers between producer and consumer.
- **Deque**: sliding-window maximum/minimum, LRU-style front/back access, palindromes.

## Alternatives

- **Dynamic array used directly** — allows arbitrary index access, but you lose the LIFO/FIFO discipline that prevents bugs.
- **Linked list** — also O(1) at the ends, but with pointer overhead and worse cache locality.
- **Priority queue** — orders elements by priority rather than arrival time, at O(log n) per operation.

## Related

- [Dynamic Arrays, Memory Allocation, and Amortized Analysis](01-dynamic-arrays.md)
- [Linked Lists and Node-Based Structures](02-linked-lists.md)
- [Heaps and Priority Queues](../02-search-trees/02-heaps-priority-queues.md)
