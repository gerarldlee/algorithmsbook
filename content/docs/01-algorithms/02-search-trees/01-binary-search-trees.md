---
title: "Binary Search Trees"
weight: 1
toc: true
---

## What it is
A binary search tree (BST) is a binary tree in which every node stores a key, and for each node all keys in its left subtree are smaller and all keys in its right subtree are larger. This ordering makes search, insertion, and deletion follow a single root-to-leaf path.

## How it works
A search compares the target key against the current node, recursing left when the target is smaller and right when it is larger. Insertion walks to the leaf position dictated by the same comparison and attaches the new node there; deletion replaces a node with two children by its in-order successor (or predecessor) and unlinks leaf or single-child nodes directly.

```java
public class BST {
    static class Node {
        int key;
        Node left, right;
        Node(int key) { this.key = key; }
    }

    Node root;

    public boolean search(int key) {
        Node cur = root;
        while (cur != null) {
            if (key == cur.key) return true;
            cur = key < cur.key ? cur.left : cur.right;
        }
        return false;
    }

    public void insert(int key) {
        if (root == null) { root = new Node(key); return; }
        Node cur = root;
        while (true) {
            if (key < cur.key) {
                if (cur.left == null) { cur.left = new Node(key); return; }
                cur = cur.left;
            } else {
                if (cur.right == null) { cur.right = new Node(key); return; }
                cur = cur.right;
            }
        }
    }

    public void delete(int key) {
        root = deleteRec(root, key);
    }

    private Node deleteRec(Node node, int key) {
        if (node == null) return null;
        if (key < node.key) node.left = deleteRec(node.left, key);
        else if (key > node.key) node.right = deleteRec(node.right, key);
        else {
            if (node.left == null) return node.right;
            if (node.right == null) return node.left;
            Node min = node.right;
            while (min.left != null) min = min.left;
            node.key = min.key;
            node.right = deleteRec(node.right, min.key);
        }
        return node;
    }
}
```

```c
#include <stdbool.h>
#include <stdlib.h>

typedef struct Node {
    int key;
    struct Node *left, *right;
} Node;

bool bst_search(Node *root, int key) {
    while (root) {
        if (key == root->key) return true;
        root = key < root->key ? root->left : root->right;
    }
    return false;
}

Node *bst_insert(Node *root, int key) {
    if (!root) {
        Node *n = malloc(sizeof(Node));
        n->key = key; n->left = n->right = NULL;
        return n;
    }
    if (key < root->key) root->left = bst_insert(root->left, key);
    else                 root->right = bst_insert(root->right, key);
    return root;
}

Node *bst_delete(Node *root, int key) {
    if (!root) return NULL;
    if (key < root->key) root->left = bst_delete(root->left, key);
    else if (key > root->key) root->right = bst_delete(root->right, key);
    else {
        if (!root->left) { Node *r = root->right; free(root); return r; }
        if (!root->right) { Node *l = root->left; free(root); return l; }
        Node *min = root->right;
        while (min->left) min = min->left;
        root->key = min->key;
        root->right = bst_delete(root->right, min->key);
    }
    return root;
}
```

```python
class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None


class BST:
    def __init__(self):
        self.root = None

    def search(self, key):
        cur = self.root
        while cur:
            if key == cur.key:
                return True
            cur = cur.left if key < cur.key else cur.right
        return False

    def insert(self, key):
        if self.root is None:
            self.root = Node(key)
            return
        cur = self.root
        while True:
            if key < cur.key:
                if cur.left is None:
                    cur.left = Node(key)
                    return
                cur = cur.left
            else:
                if cur.right is None:
                    cur.right = Node(key)
                    return
                cur = cur.right

    def _delete(self, node, key):
        if node is None:
            return None
        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        else:
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            min_node = node.right
            while min_node.left:
                min_node = min_node.left
            node.key = min_node.key
            node.right = self._delete(node.right, min_node.key)
        return node

    def delete(self, key):
        self.root = self._delete(self.root, key)
```

```rust
use std::cmp::Ordering;

#[derive(Debug)]
pub struct Node {
    pub key: i32,
    pub left: Option<Box<Node>>,
    pub right: Option<Box<Node>>,
}

impl Node {
    pub fn new(key: i32) -> Self {
        Node { key, left: None, right: None }
    }

    pub fn search(&self, key: i32) -> bool {
        match key.cmp(&self.key) {
            Ordering::Equal => true,
            Ordering::Less => self.left.as_ref().map_or(false, |l| l.search(key)),
            Ordering::Greater => self.right.as_ref().map_or(false, |r| r.search(key)),
        }
    }

    pub fn insert(&mut self, key: i32) {
        let child = match key.cmp(&self.key) {
            Ordering::Less => &mut self.left,
            Ordering::Greater => &mut self.right,
            Ordering::Equal => return,
        };
        match child {
            Some(c) => c.insert(key),
            None => *child = Some(Box::new(Node::new(key))),
        }
    }

    pub fn delete(mut self: Box<Self>, key: i32) -> Option<Box<Node>> {
        match key.cmp(&self.key) {
            Ordering::Less => {
                if let Some(l) = self.left.take() {
                    self.left = l.delete(key);
                }
                Some(self)
            }
            Ordering::Greater => {
                if let Some(r) = self.right.take() {
                    self.right = r.delete(key);
                }
                Some(self)
            }
            Ordering::Equal => match (self.left.take(), self.right.take()) {
                (None, None) => None,
                (Some(l), None) => Some(l),
                (None, Some(r)) => Some(r),
                (Some(l), Some(r)) => {
                    let min = r.min();
                    self.key = min.key;
                    self.left = Some(l);
                    self.right = r.delete(min.key);
                    Some(self)
                }
            },
        }
    }

    fn min(&self) -> &Node {
        let mut cur = self;
        while let Some(ref l) = cur.left {
            cur = l;
        }
        cur
    }
}
```

```typescript
class BSTNode {
    key: number;
    left: BSTNode | null = null;
    right: BSTNode | null = null;

    constructor(key: number) {
        this.key = key;
    }
}

export class BST {
    root: BSTNode | null = null;

    search(key: number): boolean {
        let cur = this.root;
        while (cur) {
            if (key === cur.key) return true;
            cur = key < cur.key ? cur.left : cur.right;
        }
        return false;
    }

    insert(key: number): void {
        if (this.root === null) {
            this.root = new BSTNode(key);
            return;
        }
        let cur = this.root;
        while (true) {
            if (key < cur.key) {
                if (cur.left === null) {
                    cur.left = new BSTNode(key);
                    return;
                }
                cur = cur.left;
            } else {
                if (cur.right === null) {
                    cur.right = new BSTNode(key);
                    return;
                }
                cur = cur.right;
            }
        }
    }

    private deleteRec(node: BSTNode | null, key: number): BSTNode | null {
        if (node === null) return null;
        if (key < node.key) node.left = this.deleteRec(node.left, key);
        else if (key > node.key) node.right = this.deleteRec(node.right, key);
        else {
            if (node.left === null) return node.right;
            if (node.right === null) return node.left;
            let min = node.right;
            while (min.left) min = min.left;
            node.key = min.key;
            node.right = this.deleteRec(node.right, min.key);
        }
        return node;
    }

    delete(key: number): void {
        this.root = this.deleteRec(this.root, key);
    }
}
```

```go
package bst

type Node struct {
	Key   int
	Left  *Node
	Right *Node
}

func (n *Node) Search(key int) bool {
	for n != nil {
		switch {
		case key == n.Key:
			return true
		case key < n.Key:
			n = n.Left
		default:
			n = n.Right
		}
	}
	return false
}

func (n *Node) Insert(key int) *Node {
	if n == nil {
		return &Node{Key: key}
	}
	if key < n.Key {
		n.Left = n.Left.Insert(key)
	} else if key > n.Key {
		n.Right = n.Right.Insert(key)
	}
	return n
}

func (n *Node) Delete(key int) *Node {
	if n == nil {
		return nil
	}
	switch {
	case key < n.Key:
		n.Left = n.Left.Delete(key)
	case key > n.Key:
		n.Right = n.Right.Delete(key)
	default:
		switch {
		case n.Left == nil:
			return n.Right
		case n.Right == nil:
			return n.Left
		default:
			min := n.Right
			for min.Left != nil {
				min = min.Left
			}
			n.Key = min.Key
			n.Right = n.Right.Delete(min.Key)
		}
	}
	return n
}
```

## Complexity
| Operation | Time (average) | Time (worst) | Space |
| --- | --- | --- | --- |
| Search | O(log n) | O(n) | O(1) iterative / O(log n) recursive |
| Insert | O(log n) | O(n) | O(1) iterative / O(log n) recursive |
| Delete | O(log n) | O(n) | O(log n) |

The worst case occurs when the tree degenerates into a linked list (e.g. inserting keys in sorted order). Balanced variants — AVL and red-black trees — restore the O(log n) worst-case guarantee via rotations.

## When to use
- When keys must support ordered traversal (in-order yields a sorted sequence) in addition to fast lookups.
- When you need predecessor/successor, floor/ceiling, and range queries that hash tables cannot provide.
- When the dataset is dynamic and fits in memory; a balanced BST is preferable to sorting an array on every mutation.

## Alternatives
- Hash table — O(1) average lookup but no ordering or range queries.
- Sorted array + binary search — O(log n) search and compact memory, but O(n) insertion/deletion.
- Balanced BST (AVL/red-black tree) — stricter O(log n) worst-case guarantees at the cost of rotation bookkeeping.

## Related
- [Heaps and Priority Queues](02-heaps-priority-queues.md)
- [Storage Engine Trees (B-Trees and LSM-Trees)](03-storage-engine-trees.md)
- [Dynamic Arrays](../01-linear-data-structures/01-dynamic-arrays.md)
