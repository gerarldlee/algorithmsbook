---
title: "Linked Lists and Node-Based Structures"
weight: 2
toc: true
---

## What it is

A linked list is a sequential collection of nodes, each holding a value and a pointer to the next (and, in a doubly linked list, the previous) node. Unlike an array, nodes need not be contiguous in memory, so the list can grow without relocating existing elements. The trade-off is O(n) access by index, since you must follow pointers from the head.

## How it works

A linked list is an array, or list, or collection of elements, represented contiguously, and does not impose a size limitation.  It can grow indefinitely.

- Represented contiguously means that it does not have to be contiguous in memory like an array; but from the developers perspective, it is represented contiguous.  A node that has a value, is linked to another node that has value, forming a list of nodes.
- Does not have a size limitation means that we can create new nodes that holds new values and link it to the already existing list.

Note that even though we can create the linked list data structure with a node, we can also create the linked list with an array implementation, which is more efficient with regards to space requirements, too.

Java's `ArrayList` is a linked list too, and a linked list is not to be confused with the Java's `LinkedList`.  In fact, a stack and a queue is a form of linked list, too.  We will derive it as we go along.

```java
// a node that has a value, and a next that pointers to the next node
class Node<T> {
	T value;
	Node next;
	public Node(T value) {
		this.value = value;
	}

	// for a doubly linked list, we might use the prev pointer to point to the previous node
	Node prev;
}
```

Linked list Node representations:

- Singly Linked Node - is represented by a Node with a value, and a single pointer that points to the next Node
- Doubly Linked Node - is represented by a Node with a value, just like the singly linked list, but adds another pointer that points to the previous Node.  Like the Two-Pointers approach in the Arrays, we can also use a second pointer in a Singly Linked list to form a Doubly Linked list.  It will make it more convenient for us to track back the previous Node, when we are iterating from the middle, or from the tail.

The same node representation maps one-to-one into the other five languages:

```c
#include <stdlib.h>

// a node that has a value, and a next that points to the next node
typedef struct Node {
	int value;
	struct Node *next;
	// for a doubly linked list, we might use the prev pointer to point to the previous node
	struct Node *prev;
} Node;

Node *node_create(int value) {
	Node *n = malloc(sizeof(Node));
	n->value = value;
	n->next = NULL;
	n->prev = NULL;
	return n;
}
```

```python
class Node:
    """A node that has a value, and a next that points to the next node."""
    def __init__(self, value):
        self.value = value
        self.next = None
        # for a doubly linked list, use prev to point to the previous node
        self.prev = None
```

```rust
use std::rc::Rc;
use std::cell::RefCell;

// a node that has a value, and a next that points to the next node
struct Node<T> {
    value: T,
    next: Option<Rc<RefCell<Node<T>>>>,
    // for a doubly linked list, use prev to point to the previous node
    prev: Option<Rc<RefCell<Node<T>>>>,
}

impl<T> Node<T> {
    fn new(value: T) -> Rc<RefCell<Node<T>>> {
        Rc::new(RefCell::new(Node { value, next: None, prev: None }))
    }
}
```

```typescript
// a node that has a value, and a next that points to the next node
class Node<T> {
    value: T;
    next: Node<T> | null;
    // for a doubly linked list, use prev to point to the previous node
    prev: Node<T> | null;

    constructor(value: T) {
        this.value = value;
        this.next = null;
        this.prev = null;
    }
}
```

```go
// a node that has a value, and a next that points to the next node
type Node struct {
	value int
	next  *Node
	// for a doubly linked list, use prev to point to the previous node
	prev *Node
}

func NewNode(value int) *Node {
	return &Node{value: value}
}
```

## Complexity

| Operation | Time | Space |
| --- | --- | --- |
| Access by index | O(n) | O(1) |
| Search | O(n) | O(1) |
| Insert / delete at head | O(1) | O(1) |
| Insert / delete at tail (with tail pointer) | O(1) | O(1) |
| Insert / delete in middle (given the node) | O(1) | O(1) |
| Insert / delete in middle (by index) | O(n) | O(1) |

## When to use

- You need frequent O(1) insert/delete at the head, tail, or a known node position.
- The size is unknown up front or changes unpredictably, and you want to avoid reallocations.
- You only traverse sequentially and rarely need random access by index.

## Alternatives

- **Dynamic array** — O(1) random access and better cache locality, but O(n) insert/delete in the middle.
- **Unrolled linked list** — stores several elements per node for better locality, but more complex node management.
- **Skip list** — O(log n) expected search while staying node-based, but uses more memory and random pointers.

## Related

- [Dynamic Arrays, Memory Allocation, and Amortized Analysis](01-dynamic-arrays.md)
- [Stacks, Queues, and Deques](03-stacks-queues-deques.md)
- [Heaps and Priority Queues](../02-search-trees/02-heaps-priority-queues.md)
