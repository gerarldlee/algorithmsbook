---
title: "Storage Engine Trees: B-Trees, B+ Trees, and Log-Structured Merge-Trees (LSM-Trees)"
weight: 3
toc: true
level: normal
---

## What it is
Storage-engine trees keep ordered data efficient when records live in pages or immutable files rather than contiguous memory. A B-tree provides ordered point lookup and range traversal in a self-balancing tree, a B+ tree concentrates records in linked leaves for scans, and a log-structured merge-tree (LSM-tree) buffers writes and merges sorted runs in the background.

## How it works
A B-tree stores many sorted keys in each node. With minimum degree `t`, a node has between `t-1` and `2t-1` keys and up to `2t` children. Search compares within a node, insertion descends to a leaf, and a full child splits around a median key that moves into the parent. A high branching factor makes the tree shallow and aligns internal nodes with storage pages.

A B+ tree keeps separator keys in internal nodes and links leaf pages in key order. A range scan locates the first leaf and follows links, which avoids returning to the root after each leaf. A B-tree also supports both operations but can require more internal-node work during a scan.

An LSM-tree writes updates to an in-memory **memtable**. When the memtable reaches a threshold, the engine flushes its sorted contents to an immutable **SSTable** and starts a new memtable. Reads inspect the memtable and relevant SSTables; **compaction** merges runs to remove obsolete versions and limit the number that a read must probe. Leveled and tiered compaction policies trade write cost, read cost, and temporary space differently. LevelDB and RocksDB use leveled designs, while Cassandra and HBase commonly use tiered families.

The implementations below demonstrate a minimum-degree-2 B-tree with the same `search` and `insert` operations in all six languages. Storage engines add page pinning, checksums, concurrency, and recovery around this core structure.

```mermaid
flowchart LR
    W[Write record] --> M[Memtable]
    M -->|threshold reached| S[Immutable SSTable]
    S --> C[Compaction]
    C --> R[Read path]
    Q[Read request] --> M
    Q --> R
    R --> V[Visible version]
```

```java
import java.util.ArrayList;
import java.util.List;

public class BTree {
    private static final int T = 2;

    static class BTreeNode {
        final List<Integer> keys = new ArrayList<>();
        final List<BTreeNode> children = new ArrayList<>();
        final boolean leaf;

        BTreeNode(boolean leaf) {
            this.leaf = leaf;
        }

        boolean isFull() {
            return keys.size() == 2 * T - 1;
        }
    }

    private BTreeNode root = new BTreeNode(true);

    public boolean search(int key) {
        return search(root, key);
    }

    public void insert(int key) {
        if (root.isFull()) {
            BTreeNode parent = new BTreeNode(false);
            parent.children.add(root);
            splitChild(parent, 0);
            root = parent;
        }
        insertNonFull(root, key);
    }

    private boolean search(BTreeNode node, int key) {
        int index = 0;
        while (index < node.keys.size() && key > node.keys.get(index)) index++;
        if (index < node.keys.size() && key == node.keys.get(index)) return true;
        return !node.leaf && search(node.children.get(index), key);
    }

    private void splitChild(BTreeNode parent, int index) {
        BTreeNode full = parent.children.get(index);
        BTreeNode right = new BTreeNode(full.leaf);
        for (int offset = 0; offset < T - 1; offset++) {
            right.keys.add(full.keys.remove(T));
        }
        if (!full.leaf) {
            for (int offset = 0; offset < T; offset++) {
                right.children.add(full.children.remove(T));
            }
        }
        parent.keys.add(index, full.keys.remove(T - 1));
        parent.children.add(index + 1, right);
    }

    private void insertNonFull(BTreeNode node, int key) {
        int index = node.keys.size() - 1;
        if (node.leaf) {
            while (index >= 0 && key < node.keys.get(index)) index--;
            node.keys.add(index + 1, key);
            return;
        }
        while (index >= 0 && key < node.keys.get(index)) index--;
        index++;
        if (node.children.get(index).isFull()) {
            splitChild(node, index);
            if (key > node.keys.get(index)) index++;
        }
        insertNonFull(node.children.get(index), key);
    }
}
```

```c
#include <stdbool.h>
#include <stdlib.h>

#define T 2

typedef struct BTreeNode {
    int keys[2 * T - 1];
    struct BTreeNode *children[2 * T];
    int size;
    bool leaf;
} BTreeNode;

typedef struct BTree {
    BTreeNode *root;
} BTree;

BTreeNode *btree_node_new(bool leaf) {
    BTreeNode *node = malloc(sizeof(BTreeNode));
    node->size = 0;
    node->leaf = leaf;
    return node;
}

BTree *btree_new(void) {
    BTree *tree = malloc(sizeof(BTree));
    tree->root = btree_node_new(true);
    return tree;
}

void btree_node_destroy(BTreeNode *node) {
    if (!node->leaf) {
        for (int index = 0; index <= node->size; index++) {
            btree_node_destroy(node->children[index]);
        }
    }
    free(node);
}

void btree_destroy(BTree *tree) {
    btree_node_destroy(tree->root);
    free(tree);
}

bool btree_search(BTree *tree, int key) {
    BTreeNode *node = tree->root;
    while (node) {
        int index = 0;
        while (index < node->size && key > node->keys[index]) index++;
        if (index < node->size && key == node->keys[index]) return true;
        if (node->leaf) return false;
        node = node->children[index];
    }
    return false;
}

void btree_split_child(BTreeNode *parent, int index) {
    BTreeNode *full = parent->children[index];
    BTreeNode *right = btree_node_new(full->leaf);
    right->size = T - 1;
    for (int offset = 0; offset < T - 1; offset++) {
        right->keys[offset] = full->keys[offset + T];
    }
    if (!full->leaf) {
        for (int offset = 0; offset < T; offset++) {
            right->children[offset] = full->children[offset + T];
        }
    }
    for (int offset = parent->size; offset > index; offset--) {
        parent->children[offset + 1] = parent->children[offset];
    }
    parent->children[index + 1] = right;
    for (int offset = parent->size - 1; offset >= index; offset--) {
        parent->keys[offset + 1] = parent->keys[offset];
    }
    parent->keys[index] = full->keys[T - 1];
    parent->size++;
    full->size = T - 1;
}

void btree_insert_nonfull(BTreeNode *node, int key) {
    int index = node->size - 1;
    if (node->leaf) {
        while (index >= 0 && key < node->keys[index]) {
            node->keys[index + 1] = node->keys[index];
            index--;
        }
        node->keys[index + 1] = key;
        node->size++;
        return;
    }
    while (index >= 0 && key < node->keys[index]) index--;
    index++;
    if (node->children[index]->size == 2 * T - 1) {
        btree_split_child(node, index);
        if (key > node->keys[index]) index++;
    }
    btree_insert_nonfull(node->children[index], key);
}

void btree_insert(BTree *tree, int key) {
    if (tree->root->size == 2 * T - 1) {
        BTreeNode *root = btree_node_new(false);
        root->children[0] = tree->root;
        btree_split_child(root, 0);
        tree->root = root;
    }
    btree_insert_nonfull(tree->root, key);
}
```

```python
class BTreeNode:
    def __init__(self, leaf=True):
        self.keys = []
        self.children = []
        self.leaf = leaf

    def is_full(self):
        return len(self.keys) == 3


class BTree:
    def __init__(self):
        self.root = BTreeNode()

    def search(self, key):
        node = self.root
        while node is not None:
            index = 0
            while index < len(node.keys) and key > node.keys[index]:
                index += 1
            if index < len(node.keys) and key == node.keys[index]:
                return True
            if node.leaf:
                return False
            node = node.children[index]
        return False

    def insert(self, key):
        if self.root.is_full():
            root = BTreeNode(leaf=False)
            root.children.append(self.root)
            self._split_child(root, 0)
            self.root = root
        self._insert_nonfull(self.root, key)

    def _split_child(self, parent, index):
        full = parent.children[index]
        right = BTreeNode(full.leaf)
        right.keys = full.keys[2:]
        if not full.leaf:
            right.children = full.children[2:]
        parent.keys.insert(index, full.keys[1])
        parent.children.insert(index + 1, right)
        full.keys = full.keys[:1]
        full.children = full.children[:2]

    def _insert_nonfull(self, node, key):
        index = len(node.keys) - 1
        if node.leaf:
            while index >= 0 and key < node.keys[index]:
                index -= 1
            node.keys.insert(index + 1, key)
            return
        while index >= 0 and key < node.keys[index]:
            index -= 1
        index += 1
        if node.children[index].is_full():
            self._split_child(node, index)
            if key > node.keys[index]:
                index += 1
        self._insert_nonfull(node.children[index], key)
```

```rust
const T: usize = 2;

#[derive(Clone)]
pub struct BTreeNode {
    keys: Vec<i32>,
    children: Vec<BTreeNode>,
    leaf: bool,
}

impl BTreeNode {
    fn new(leaf: bool) -> Self {
        BTreeNode { keys: Vec::new(), children: Vec::new(), leaf }
    }

    fn is_full(&self) -> bool {
        self.keys.len() == 2 * T - 1
    }
}

pub struct BTree {
    root: BTreeNode,
}

impl BTree {
    pub fn new() -> Self {
        BTree { root: BTreeNode::new(true) }
    }

    pub fn search(&self, key: i32) -> bool {
        let mut node = &self.root;
        loop {
            let mut index = 0;
            while index < node.keys.len() && key > node.keys[index] {
                index += 1;
            }
            if index < node.keys.len() && key == node.keys[index] {
                return true;
            }
            if node.leaf {
                return false;
            }
            node = &node.children[index];
        }
    }

    pub fn insert(&mut self, key: i32) {
        if self.root.is_full() {
            let mut root = BTreeNode::new(false);
            root.children.push(std::mem::replace(&mut self.root, BTreeNode::new(true)));
            Self::split_child(&mut root, 0);
            self.root = root;
        }
        Self::insert_nonfull(&mut self.root, key);
    }

    fn split_child(parent: &mut BTreeNode, index: usize) {
        let mut full = parent.children[index].clone();
        let mut right = BTreeNode::new(full.leaf);
        right.keys = full.keys.split_off(T);
        if !full.leaf {
            right.children = full.children.split_off(T);
        }
        let median = full.keys.pop().unwrap();
        full.keys.truncate(T - 1);
        parent.keys.insert(index, median);
        parent.children[index] = full;
        parent.children.insert(index + 1, right);
    }

    fn insert_nonfull(node: &mut BTreeNode, key: i32) {
        let mut index = node.keys.len();
        if node.leaf {
            node.keys.push(key);
            while index > 0 && node.keys[index - 1] > key {
                node.keys[index] = node.keys[index - 1];
                index -= 1;
            }
            node.keys[index] = key;
            return;
        }
        while index > 0 && key < node.keys[index - 1] {
            index -= 1;
        }
        if node.children[index].is_full() {
            Self::split_child(node, index);
            if key > node.keys[index] {
                index += 1;
            }
        }
        Self::insert_nonfull(&mut node.children[index], key);
    }
}
```

```typescript
class BTreeNode {
    keys: number[] = [];
    children: BTreeNode[] = [];
    leaf: boolean;

    constructor(leaf: boolean) {
        this.leaf = leaf;
    }

    isFull(): boolean {
        return this.keys.length === 3;
    }
}

export class BTree {
    private root = new BTreeNode(true);

    search(key: number): boolean {
        let node: BTreeNode | undefined = this.root;
        while (node !== undefined) {
            let index = 0;
            while (index < node.keys.length && key > node.keys[index]) index++;
            if (index < node.keys.length && key === node.keys[index]) return true;
            if (node.leaf) return false;
            node = node.children[index];
        }
        return false;
    }

    insert(key: number): void {
        if (this.root.isFull()) {
            const root = new BTreeNode(false);
            root.children.push(this.root);
            BTree.splitChild(root, 0);
            this.root = root;
        }
        BTree.insertNonFull(this.root, key);
    }

    private static splitChild(parent: BTreeNode, index: number): void {
        const full = parent.children[index];
        const right = new BTreeNode(full.leaf);
        right.keys = full.keys.splice(2);
        if (!full.leaf) right.children = full.children.splice(2);
        parent.keys.splice(index, 0, full.keys.splice(1, 1)[0]);
        parent.children.splice(index + 1, 0, right);
    }

    private static insertNonFull(node: BTreeNode, key: number): void {
        let index = node.keys.length;
        if (node.leaf) {
            node.keys.push(key);
            while (index > 0 && node.keys[index - 1] > key) {
                node.keys[index] = node.keys[index - 1];
                index--;
            }
            node.keys[index] = key;
            return;
        }
        while (index > 0 && key < node.keys[index - 1]) index--;
        if (node.children[index].isFull()) {
            BTree.splitChild(node, index);
            if (key > node.keys[index]) index++;
        }
        BTree.insertNonFull(node.children[index], key);
    }
}
```

```go
package btree

const minimumDegree = 2

type BTreeNode struct {
	keys     []int
	children []*BTreeNode
	leaf     bool
}

func newBTreeNode(leaf bool) *BTreeNode {
	return &BTreeNode{leaf: leaf}
}

func (node *BTreeNode) isFull() bool {
	return len(node.keys) == 2*minimumDegree - 1
}

type BTree struct {
	root *BTreeNode
}

func New() *BTree {
	return &BTree{root: newBTreeNode(true)}
}

func (tree *BTree) Search(key int) bool {
	node := tree.root
	for node != nil {
		index := 0
		for index < len(node.keys) && key > node.keys[index] {
			index++
		}
		if index < len(node.keys) && key == node.keys[index] {
			return true
		}
		if node.leaf {
			return false
		}
		node = node.children[index]
	}
	return false
}

func (tree *BTree) Insert(key int) {
	if tree.root.isFull() {
		root := newBTreeNode(false)
		root.children = append(root.children, tree.root)
		tree.splitChild(root, 0)
		tree.root = root
	}
	tree.insertNonFull(tree.root, key)
}

func (tree *BTree) splitChild(parent *BTreeNode, index int) {
	full := parent.children[index]
	right := newBTreeNode(full.leaf)
	right.keys = append(right.keys, full.keys[minimumDegree:]...)
	if !full.leaf {
		right.children = append(right.children, full.children[minimumDegree:]...)
	}
	parent.keys = append(parent.keys, 0)
	copy(parent.keys[index+1:], parent.keys[index:])
	parent.keys[index] = full.keys[minimumDegree-1]
	parent.children = append(parent.children, nil)
	copy(parent.children[index+2:], parent.children[index+1:])
	parent.children[index+1] = right
	full.keys = full.keys[:minimumDegree-1]
	full.children = full.children[:minimumDegree]
}

func (tree *BTree) insertNonFull(node *BTreeNode, key int) {
    index := len(node.keys)
    if node.leaf {
        node.keys = append(node.keys, key)
        for index > 0 && node.keys[index-1] > key {
            node.keys[index] = node.keys[index-1]
            index--
        }
        node.keys[index] = key
        return
    }
    for index > 0 && key < node.keys[index-1] {
        index--
    }
    if node.children[index].isFull() {
        tree.splitChild(node, index)
        if key > node.keys[index] {
            index++
        }
    }
    tree.insertNonFull(node.children[index], key)
}
```

### B+ trees and LSM-trees

A B+ tree keeps most or all records in leaves and uses internal keys mainly as separators. Because leaves are linked, a range scan follows leaf pointers instead of restarting a root search for every key. A B+ tree is therefore a strong fit for database indexes that need broad scans and predictable page access.

An LSM-tree changes the write path: updates enter a memtable, reach disk as sorted immutable tables, and are merged by compaction. Reads may need to inspect several tables before finding the newest version. LSM-trees favor write-heavy workloads, but they require versioning, sequence identifiers, compaction scheduling, and recovery logic around the tree structure.

## Complexity
| Operation or property | B-tree or B+ tree | LSM-tree |
| --- | --- | --- |
| Search | O(log n) key comparisons | O(F log n) for `F` candidate files or levels |
| Insert or update | O(log n) key comparisons and page updates | O(1) expected memtable append before flush and compaction |
| Delete | O(log n) key comparisons and page updates | O(1) expected tombstone append before flush and compaction |
| Ordered range result | O(log n + k) for `k` results | O(F(log n + k)) under a simple leveled layout |
| Build from sorted keys | O(n) | O(n) plus merge and flush cost |

`F` is the number of candidate SSTable files or levels consulted. These bounds omit I/O latency. The B+ tree keeps a small height because page-sized nodes have a large fan-out, but random page faults can dominate key comparisons.

## When to use
- You need ordered point lookups and range scans over indexes larger than memory.
- Read latency matters more than raw write throughput, favoring a B+ tree.
- Write-heavy ingestion benefits from sequential LSM flushes and tolerates compaction overhead.
- The storage engine needs concurrent versions, recovery, or level-based retention.

## Alternatives
- **Hash index** — gives expected O(1) point lookup but no ordered range traversal.
- **In-memory balanced search tree** — gives simpler low-latency operations but does not solve page or file persistence by itself.
- **Log-structured array** — optimizes scan and ingestion, but requires indexes for point lookup and more compaction work.
- **Fractal tree or buffered B-tree** — reduces random write amplification with internal buffers, but adds metadata and implementation complexity.

## Related
- [Binary Search Trees](01-binary-search-trees.md)
- [Range Query Trees (Segment Trees and Fenwick Trees)](04-range-query-trees.md)
- [Storage Engines](../../04-distributed-systems/02-databases/03-storage-engines.md)
- [Spatial Indexing & Geospatial Data Structures](07-spatial-indexing.md)
