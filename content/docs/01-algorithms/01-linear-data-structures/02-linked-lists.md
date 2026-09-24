---
title: "Linked Lists (Singly, Doubly, Skip Lists)"
weight: 2
toc: true
---

## What it is

A linked list is a sequential collection of nodes, each holding a value and a reference to the next node. Nodes do not need to occupy contiguous memory, so insertion and removal can avoid relocating the rest of the collection. The cost is that access by index requires following references from the head and therefore takes O(n) time.

## How it works

A singly linked list stores each value in a node with one forward reference. A doubly linked list adds a backward reference, which makes traversal in both directions and removal of a known node easier. A skip list adds multiple ordered levels so search can skip large ranges of nodes, at the cost of additional pointers and update work.

The implementation below demonstrates a singly linked list. Every language provides the same logical operations: push a value at the head, remove the first matching value, test membership, convert the list to an array, and report its size. A production implementation would also define ownership and memory-release rules for its language.

```java
class Node {
    int value;
    Node next;

    Node(int value) {
        this.value = value;
    }
}

class LinkedList {
    private Node head;
    private int size;

    void pushFront(int value) {
        Node node = new Node(value);
        node.next = head;
        head = node;
        size++;
    }

    boolean remove(int value) {
        if (head == null) return false;
        if (head.value == value) {
            head = head.next;
            size--;
            return true;
        }
        Node current = head;
        while (current.next != null && current.next.value != value) {
            current = current.next;
        }
        if (current.next == null) return false;
        current.next = current.next.next;
        size--;
        return true;
    }

    boolean contains(int value) {
        Node current = head;
        while (current != null) {
            if (current.value == value) return true;
            current = current.next;
        }
        return false;
    }

    int[] toArray() {
        int[] values = new int[size];
        int index = 0;
        Node current = head;
        while (current != null) {
            values[index++] = current.value;
            current = current.next;
        }
        return values;
    }

    int length() {
        return size;
    }
}
```

```c
#include <stdbool.h>
#include <stdlib.h>

typedef struct Node {
    int value;
    struct Node *next;
} Node;

typedef struct {
    Node *head;
    int size;
} LinkedList;

void ll_init(LinkedList *list) {
    list->head = NULL;
    list->size = 0;
}

void ll_push_front(LinkedList *list, int value) {
    Node *node = malloc(sizeof(Node));
    if (node == NULL) abort();
    node->value = value;
    node->next = list->head;
    list->head = node;
    list->size++;
}

bool ll_remove(LinkedList *list, int value) {
    Node **link = &list->head;
    while (*link != NULL) {
        if ((*link)->value == value) {
            Node *removed = *link;
            *link = removed->next;
            free(removed);
            list->size--;
            return true;
        }
        link = &(*link)->next;
    }
    return false;
}

bool ll_contains(const LinkedList *list, int value) {
    for (Node *current = list->head; current != NULL; current = current->next) {
        if (current->value == value) return true;
    }
    return false;
}

int ll_to_array(const LinkedList *list, int *values) {
    int index = 0;
    for (Node *current = list->head; current != NULL; current = current->next) {
        values[index++] = current->value;
    }
    return index;
}

int ll_length(const LinkedList *list) {
    return list->size;
}

void ll_free(LinkedList *list) {
    Node *current = list->head;
    while (current != NULL) {
        Node *next = current->next;
        free(current);
        current = next;
    }
    list->head = NULL;
    list->size = 0;
}
```

```python
class Node:
    def __init__(self, value):
        self.value = value
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.size = 0

    def push_front(self, value):
        node = Node(value)
        node.next = self.head
        self.head = node
        self.size += 1

    def remove(self, value):
        if self.head is None:
            return False
        if self.head.value == value:
            self.head = self.head.next
            self.size -= 1
            return True
        current = self.head
        while current.next is not None and current.next.value != value:
            current = current.next
        if current.next is None:
            return False
        current.next = current.next.next
        self.size -= 1
        return True

    def contains(self, value):
        current = self.head
        while current is not None:
            if current.value == value:
                return True
            current = current.next
        return False

    def to_array(self):
        values = []
        current = self.head
        while current is not None:
            values.append(current.value)
            current = current.next
        return values

    def length(self):
        return self.size
```

```rust
pub struct Node {
    pub value: i32,
    pub next: Option<Box<Node>>,
}

pub struct LinkedList {
    head: Option<Box<Node>>,
    size: usize,
}

impl LinkedList {
    pub fn new() -> Self {
        LinkedList { head: None, size: 0 }
    }

    pub fn push_front(&mut self, value: i32) {
        self.head = Some(Box::new(Node { value, next: self.head.take() }));
        self.size += 1;
    }

    pub fn remove(&mut self, value: i32) -> bool {
        if Self::remove_from(&mut self.head, value) {
            self.size -= 1;
            true
        } else {
            false
        }
    }

    fn remove_from(link: &mut Option<Box<Node>>, value: i32) -> bool {
        if let Some(current) = link.as_mut() {
            if current.value == value {
                *link = current.next.take();
                true
            } else {
                Self::remove_from(&mut current.next, value)
            }
        } else {
            false
        }
    }

    pub fn contains(&self, value: i32) -> bool {
        let mut current = self.head.as_ref();
        while let Some(node) = current {
            if node.value == value {
                return true;
            }
            current = node.next.as_ref();
        }
        false
    }

    pub fn to_array(&self) -> Vec<i32> {
        let mut values = Vec::with_capacity(self.size);
        let mut current = self.head.as_ref();
        while let Some(node) = current {
            values.push(node.value);
            current = node.next.as_ref();
        }
        values
    }

    pub fn length(&self) -> usize {
        self.size
    }
}
```

```typescript
class Node {
  value: number;
  next: Node | null;

  constructor(value: number) {
    this.value = value;
    this.next = null;
  }
}

class LinkedList {
  private head: Node | null = null;
  private size = 0;

  pushFront(value: number): void {
    const node = new Node(value);
    node.next = this.head;
    this.head = node;
    this.size++;
  }

  remove(value: number): boolean {
    if (this.head === null) return false;
    if (this.head.value === value) {
      this.head = this.head.next;
      this.size--;
      return true;
    }
    let current = this.head;
    while (current.next !== null && current.next.value !== value) {
      current = current.next;
    }
    if (current.next === null) return false;
    current.next = current.next.next;
    this.size--;
    return true;
  }

  contains(value: number): boolean {
    let current = this.head;
    while (current !== null) {
      if (current.value === value) return true;
      current = current.next;
    }
    return false;
  }

  toArray(): number[] {
    const values: number[] = [];
    let current = this.head;
    while (current !== null) {
      values.push(current.value);
      current = current.next;
    }
    return values;
  }

  length(): number {
    return this.size;
  }
}
```

```go
package main
type Node struct {
	Value int
	Next  *Node
}

type LinkedList struct {
	Head *Node
	Size int
}

func NewLinkedList() *LinkedList {
	return &LinkedList{}
}

func (list *LinkedList) PushFront(value int) {
	list.Head = &Node{Value: value, Next: list.Head}
	list.Size++
}

func (list *LinkedList) Remove(value int) bool {
	link := &list.Head
	for *link != nil {
		if (*link).Value == value {
			removed := *link
			*link = removed.Next
			list.Size--
			return true
		}
		link = &(*link).Next
	}
	return false
}

func (list *LinkedList) Contains(value int) bool {
	for current := list.Head; current != nil; current = current.Next {
		if current.Value == value {
			return true
		}
	}
	return false
}

func (list *LinkedList) ToArray() []int {
	values := make([]int, 0, list.Size)
	for current := list.Head; current != nil; current = current.Next {
		values = append(values, current.Value)
	}
	return values
}

func (list *LinkedList) Length() int {
    return list.Size
}
```

### Variants

A **singly linked node** has one forward reference and is the smallest representation. A **doubly linked node** also stores a backward reference, which supports reverse traversal and O(1) removal when the node is already known. A **skip list** stores several forward references at increasing levels, so search can skip larger ranges while retaining node-based updates.

## Complexity

| Operation | Time | Space |
| --- | --- | --- |
| Access by index | O(n) | O(1) |
| Search | O(n) | O(1) |
| Push at head | O(1) | O(1) |
| Remove first matching value | O(n) | O(1) |
| Convert to an array | O(n) | O(n) output |
| Report size | O(1) | O(1) |

Doubly linked lists add a backward reference per node. Skip lists add multiple levels of references, trading extra space and update work for O(log n) expected search.

## When to use

- You need O(1) insertion or removal at the head and do not need random access by index.
- Nodes must be allocated independently, or ownership is shared across components.
- The collection is primarily traversed sequentially and changes size frequently.

## Alternatives

- **Dynamic array** — O(1) random access and better cache locality, but O(n) insertion and removal in the middle.
- **Unrolled linked list** — stores several values per node for better locality, at the cost of more complex node management.
- **Skip list** — O(log n) expected search while staying node-based, but uses more memory and update work.

## Related

- [Dynamic Arrays, Memory Allocation, and Amortized Analysis](01-dynamic-arrays.md)
- [Stacks, Queues, Deques, and Ring/Circular Buffers](03-stacks-queues-deques.md)
