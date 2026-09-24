---
title: "Storage Engine Trees (B-Trees and LSM-Trees)"
weight: 3
toc: true
---

## What it is
B-trees and LSM-trees are the two dominant on-disk indexing structures. A B-tree is a self-balancing search tree with high branching factor that keeps data sorted and supports O(log n) point reads and range scans; an LSM-tree (log-structured merge-tree) appends writes to an in-memory buffer and immutable sorted files on disk, later merging them in background compaction.

## How it works
A B-tree stores many keys per node (between `t-1` and `2t-1` for minimum degree `t`) so each node is roughly the size of a disk page, minimizing I/O. Insertion descends to the correct leaf and, when a full node would overflow, splits it and pushes the median key up to the parent. An LSM-tree instead writes sequentially: writes land in a memtable, flush to an immutable sorted SSTable, and compaction merges overlapping files to bound read amplification.

```java
import java.util.ArrayList;
import java.util.List;

public class BTree {
    static final int T = 2; // minimum degree

    static class Node {
        List<Integer> keys = new ArrayList<>();
        List<Node> children = new ArrayList<>();
        boolean leaf = true;

        boolean isFull() { return keys.size() == 2 * T - 1; }
    }

    Node root = new Node();

    public boolean search(int key) {
        return search(root, key);
    }

    private boolean search(Node node, int key) {
        int i = 0;
        while (i < node.keys.size() && key > node.keys.get(i)) i++;
        if (i < node.keys.size() && key == node.keys.get(i)) return true;
        if (node.leaf) return false;
        return search(node.children.get(i), key);
    }

    public void insert(int key) {
        if (root.isFull()) {
            Node s = new Node();
            s.leaf = false;
            s.children.add(root);
            splitChild(s, 0);
            root = s;
        }
        insertNonFull(root, key);
    }

    private void splitChild(Node parent, int i) {
        Node full = parent.children.get(i);
        Node right = new Node();
        right.leaf = full.leaf;
        for (int j = 0; j < T - 1; j++) right.keys.add(full.keys.remove(T));
        if (!full.leaf)
            for (int j = 0; j < T; j++) right.children.add(full.children.remove(T));
        parent.keys.add(i, full.keys.remove(T - 1));
        parent.children.add(i + 1, right);
    }

    private void insertNonFull(Node node, int key) {
        int i = node.keys.size() - 1;
        if (node.leaf) {
            while (i >= 0 && key < node.keys.get(i)) i--;
            node.keys.add(i + 1, key);
            return;
        }
        while (i >= 0 && key < node.keys.get(i)) i--;
        i++;
        if (node.children.get(i).isFull()) {
            splitChild(node, i);
            if (key > node.keys.get(i)) i++;
        }
        insertNonFull(node.children.get(i), key);
    }
}
```

```c
#include <stdbool.h>
#include <stdlib.h>

#define T 2

typedef struct Node {
    int keys[2 * T - 1];
    struct Node *children[2 * T];
    int n;
    bool leaf;
} Node;

Node *node_new(bool leaf) {
    Node *n = malloc(sizeof(Node));
    n->n = 0; n->leaf = leaf;
    return n;
}

bool btree_search(Node *node, int key) {
    int i = 0;
    while (i < node->n && key > node->keys[i]) i++;
    if (i < node->n && key == node->keys[i]) return true;
    if (node->leaf) return false;
    return btree_search(node->children[i], key);
}

static void split_child(Node *parent, int i) {
    Node *full = parent->children[i];
    Node *right = node_new(full->leaf);
    right->n = T - 1;
    for (int j = 0; j < T - 1; j++) right->keys[j] = full->keys[j + T];
    if (!full->leaf)
        for (int j = 0; j < T; j++) right->children[j] = full->children[j + T];
    for (int j = parent->n; j > i; j--) parent->children[j + 1] = parent->children[j];
    parent->children[i + 1] = right;
    for (int j = parent->n - 1; j >= i; j--) parent->keys[j + 1] = parent->keys[j];
    parent->keys[i] = full->keys[T - 1];
    parent->n++;
    full->n = T - 1;
}

static void insert_nonfull(Node *node, int key) {
    int i = node->n - 1;
    if (node->leaf) {
        while (i >= 0 && key < node->keys[i]) {
            node->keys[i + 1] = node->keys[i];
            i--;
        }
        node->keys[i + 1] = key;
        node->n++;
        return;
    }
    while (i >= 0 && key < node->keys[i]) i--;
    i++;
    if (node->children[i]->n == 2 * T - 1) {
        split_child(node, i);
        if (key > node->keys[i]) i++;
    }
    insert_nonfull(node->children[i], key);
}

Node *btree_insert(Node *root, int key) {
    if (root->n == 2 * T - 1) {
        Node *s = node_new(false);
        s->children[0] = root;
        split_child(s, 0);
        root = s;
    }
    insert_nonfull(root, key);
    return root;
}
```

```python
T = 2  # minimum degree


class BTreeNode:
    def __init__(self, leaf=True):
        self.keys = []
        self.children = []
        self.leaf = leaf

    def is_full(self):
        return len(self.keys) == 2 * T - 1


class BTree:
    def __init__(self):
        self.root = BTreeNode()

    def search(self, key):
        return self._search(self.root, key)

    def _search(self, node, key):
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return True
        if node.leaf:
            return False
        return self._search(node.children[i], key)

    def _split_child(self, parent, i):
        full = parent.children[i]
        right = BTreeNode(full.leaf)
        right.keys = full.keys[T:]
        if not full.leaf:
            right.children = full.children[T:]
        parent.keys.insert(i, full.keys[T - 1])
        parent.children.insert(i + 1, right)
        full.keys = full.keys[:T - 1]
        full.children = full.children[:T]

    def _insert_nonfull(self, node, key):
        i = len(node.keys) - 1
        if node.leaf:
            node.keys.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = key
            return
        while i >= 0 and key < node.keys[i]:
            i -= 1
        i += 1
        if node.children[i].is_full():
            self._split_child(node, i)
            if key > node.keys[i]:
                i += 1
        self._insert_nonfull(node.children[i], key)

    def insert(self, key):
        if self.root.is_full():
            s = BTreeNode(leaf=False)
            s.children.append(self.root)
            self._split_child(s, 0)
            self.root = s
        self._insert_nonfull(self.root, key)
```

```rust
const T: usize = 2; // minimum degree

#[derive(Clone)]
pub struct BTreeNode {
    pub keys: Vec<i32>,
    pub children: Vec<BTreeNode>,
    pub leaf: bool,
}

impl BTreeNode {
    pub fn new(leaf: bool) -> Self {
        BTreeNode { keys: Vec::new(), children: Vec::new(), leaf }
    }

    fn is_full(&self) -> bool {
        self.keys.len() == 2 * T - 1
    }

    pub fn search(&self, key: i32) -> bool {
        let mut i = 0;
        while i < self.keys.len() && key > self.keys[i] {
            i += 1;
        }
        if i < self.keys.len() && key == self.keys[i] {
            return true;
        }
        if self.leaf {
            return false;
        }
        self.children[i].search(key)
    }
}

pub struct BTree {
    pub root: BTreeNode,
}

impl BTree {
    pub fn new() -> Self {
        BTree { root: BTreeNode::new(true) }
    }

    pub fn insert(&mut self, key: i32) {
        if self.root.is_full() {
            let mut s = BTreeNode::new(false);
            s.children.push(std::mem::replace(&mut self.root, BTreeNode::new(true)));
            Self::split_child(&mut s, 0);
            self.root = s;
        }
        Self::insert_nonfull(&mut self.root, key);
    }

    fn split_child(parent: &mut BTreeNode, i: usize) {
        let mut full = parent.children[i].clone();
        let mut right = BTreeNode::new(full.leaf);
        right.keys = full.keys.split_off(T);
        if !full.leaf {
            right.children = full.children.split_off(T);
        }
        let median = full.keys.pop().unwrap();
        full.keys.truncate(T - 1);
        parent.keys.insert(i, median);
        parent.children[i] = full;
        parent.children.insert(i + 1, right);
    }

    fn insert_nonfull(node: &mut BTreeNode, key: i32) {
        let mut i = node.keys.len();
        if node.leaf {
            node.keys.push(key);
            while i > 0 && node.keys[i - 1] > key {
                node.keys[i] = node.keys[i - 1];
                i -= 1;
            }
            node.keys[i] = key;
            return;
        }
        while i > 0 && key < node.keys[i - 1] {
            i -= 1;
        }
        if node.children[i].is_full() {
            Self::split_child(node, i);
            if key > node.keys[i] {
                i += 1;
            }
        }
        Self::insert_nonfull(&mut node.children[i], key);
    }
}
```

```typescript
const T = 2; // minimum degree

class BTreeNode {
    keys: number[] = [];
    children: BTreeNode[] = [];
    leaf: boolean;

    constructor(leaf: boolean) {
        this.leaf = leaf;
    }

    isFull(): boolean {
        return this.keys.length === 2 * T - 1;
    }

    search(key: number): boolean {
        let i = 0;
        while (i < this.keys.length && key > this.keys[i]) i++;
        if (i < this.keys.length && key === this.keys[i]) return true;
        if (this.leaf) return false;
        return this.children[i].search(key);
    }
}

export class BTree {
    root: BTreeNode = new BTreeNode(true);

    search(key: number): boolean {
        return this.root.search(key);
    }

    insert(key: number): void {
        if (this.root.isFull()) {
            const s = new BTreeNode(false);
            s.children.push(this.root);
            BTree.splitChild(s, 0);
            this.root = s;
        }
        BTree.insertNonFull(this.root, key);
    }

    private static splitChild(parent: BTreeNode, i: number): void {
        const full = parent.children[i];
        const right = new BTreeNode(full.leaf);
        right.keys = full.keys.splice(T);
        if (!full.leaf) right.children = full.children.splice(T);
        const median = full.keys.splice(T - 1, 1)[0];
        parent.keys.splice(i, 0, median);
        parent.children.splice(i + 1, 0, right);
    }

    private static insertNonFull(node: BTreeNode, key: number): void {
        let i = node.keys.length - 1;
        if (node.leaf) {
            while (i >= 0 && key < node.keys[i]) i--;
            node.keys.splice(i + 1, 0, key);
            return;
        }
        while (i >= 0 && key < node.keys[i]) i--;
        i++;
        if (node.children[i].isFull()) {
            BTree.splitChild(node, i);
            if (key > node.keys[i]) i++;
        }
        BTree.insertNonFull(node.children[i], key);
    }
}
```

```go
package btree

const T = 2 // minimum degree

type Node struct {
	keys     []int
	children []*Node
	leaf     bool
}

func newBTreeNode(leaf bool) *Node {
	return &Node{leaf: leaf}
}

func (n *Node) isFull() bool {
	return len(n.keys) == 2*T-1
}

func (n *Node) search(key int) bool {
	i := 0
	for i < len(n.keys) && key > n.keys[i] {
		i++
	}
	if i < len(n.keys) && key == n.keys[i] {
		return true
	}
	if n.leaf {
		return false
	}
	return n.children[i].search(key)
}

type BTree struct {
	root *Node
}

func New() *BTree {
	return &BTree{root: newBTreeNode(true)}
}

func splitChild(parent *Node, i int) {
	full := parent.children[i]
	right := newBTreeNode(full.leaf)
	right.keys = append(right.keys, full.keys[T:]...)
	if !full.leaf {
		right.children = append(right.children, full.children[T:]...)
	}
	parent.keys = append(parent.keys, 0)
	copy(parent.keys[i+1:], parent.keys[i:])
	parent.keys[i] = full.keys[T-1]
	parent.children = append(parent.children, nil)
	copy(parent.children[i+2:], parent.children[i+1:])
	parent.children[i+1] = right
	full.keys = full.keys[:T-1]
	full.children = full.children[:T]
}

func insertNonFull(node *Node, key int) {
	i := len(node.keys) - 1
	if node.leaf {
		node.keys = append(node.keys, 0)
		for i >= 0 && key < node.keys[i] {
			node.keys[i+1] = node.keys[i]
			i--
		}
		node.keys[i+1] = key
		return
	}
	for i >= 0 && key < node.keys[i] {
		i--
	}
	i++
	if node.children[i].isFull() {
		splitChild(node, i)
		if key > node.keys[i] {
			i++
		}
	}
	insertNonFull(node.children[i], key)
}

func (t *BTree) Insert(key int) {
	if t.root.isFull() {
		s := newBTreeNode(false)
		s.children = append(s.children, t.root)
		splitChild(s, 0)
		t.root = s
	}
	insertNonFull(t.root, key)
}
```

## Complexity
| Operation | B-tree | LSM-tree |
| --- | --- | --- |
| Point read (search) | O(log n) | O(log n) worst case (may probe multiple levels) |
| Write / insert | O(log n) | O(1) memtable append (amortized) |
| Delete | O(log n) | O(1) tombstone append |
| Range scan | O(log n + k) | O(log n + k) |
| Space amplification | Low | Higher (old versions until compaction) |
| Write amplification | Higher (in-place updates) | Lower (sequential writes) |

The B-tree's high fan-out means log base is large, so tree height is only a handful of levels even for billions of keys — a single root-to-leaf path touches a few disk pages.

## When to use
- B-tree: read-heavy workloads with point reads and range scans, where you want strong read latency guarantees and few surprises (e.g. PostgreSQL, InnoDB, most SQL engines).
- LSM-tree: write-heavy workloads that benefit from sequential I/O and high throughput, accepting higher read cost and background compaction (e.g. RocksDB, LevelDB, Cassandra, HBase).

## Alternatives
- Hash index — O(1) point lookups but no ordered range scans.
- In-memory balanced BST — fastest when data fits in RAM but loses persistence and page-oriented I/O efficiency.
- Fractal tree / write-optimized B-tree — lower write amplification via buffers in internal nodes, at added implementation complexity.

## Related
- [Binary Search Trees](01-binary-search-trees.md)
- [Heaps and Priority Queues](02-heaps-priority-queues.md)
