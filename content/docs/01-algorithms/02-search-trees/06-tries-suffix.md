---
title: "Tries, Radix Trees, Suffix Trees/Arrays, and Advanced String Matching (KMP, Rabin-Karp, Aho-Corasick)"
weight: 6
toc: true
---

## What it is
A trie, or prefix tree, stores strings so that nodes represent prefixes. A radix tree compresses chains of single-child trie nodes into labeled edges. A suffix tree is a compact trie of all suffixes of one text, while a suffix array stores the starting positions of those suffixes in lexicographic order.

## How it works
A trie follows one character per edge from the root, creates missing nodes during insertion, and marks the final node as a key endpoint. Exact search also requires that endpoint flag; prefix search succeeds at the node reached by the prefix. A radix tree stores a string on each edge, splitting an edge when a later key diverges inside it. Both structures make each operation linear in the inspected key length, although radix trees use fewer nodes and more edge-label bookkeeping.

A suffix tree builds a compact trie of the text's suffixes. A unique sentinel ensures that every suffix reaches a leaf, and suffix links connect suffixes that omit their first character. The compact edge labels let one comparison consume many characters, and suffix links support efficient repeated-substring and longest-common-substring algorithms. A suffix array instead sorts suffix positions. Substring search can binary-search the array and compare candidates; a longest-common-prefix array lets the implementation skip portions of matching text.

The implementations below expose the same string-based `insert`, `search`, and `startsWith` operations in all six languages. Production trie indexes replace fixed branches with maps, arrays, or compressed transitions according to key size and lookup patterns.

```java
import java.util.HashMap;
import java.util.Map;

public class Trie {
    static class TrieNode {
        Map<Character, TrieNode> children = new HashMap<>();
        boolean isEnd;
    }

    private final TrieNode root = new TrieNode();

    public void insert(String word) {
        TrieNode current = root;
        for (char character : word.toCharArray()) {
            current = current.children.computeIfAbsent(character, key -> new TrieNode());
        }
        current.isEnd = true;
    }

    public boolean search(String word) {
        TrieNode current = root;
        for (char character : word.toCharArray()) {
            current = current.children.get(character);
            if (current == null) return false;
        }
        return current.isEnd;
    }

    public boolean startsWith(String prefix) {
        TrieNode current = root;
        for (char character : prefix.toCharArray()) {
            current = current.children.get(character);
            if (current == null) return false;
        }
        return true;
    }
}
```

```c
#include <stdbool.h>
#include <stdlib.h>

typedef struct TrieNode TrieNode;

typedef struct TrieEdge {
    unsigned char value;
    TrieNode *child;
    struct TrieEdge *next;
} TrieEdge;

struct TrieNode {
    TrieEdge *children;
    bool is_end;
};

typedef struct {
    TrieNode *root;
} Trie;

TrieNode *trie_node_new(void) {
    TrieNode *node = calloc(1, sizeof(TrieNode));
    return node;
}

void trie_node_destroy(TrieNode *node) {
    TrieEdge *edge = node->children;
    while (edge) {
        TrieEdge *next = edge->next;
        trie_node_destroy(edge->child);
        free(edge);
        edge = next;
    }
    free(node);
}

Trie *trie_new(void) {
    Trie *trie = malloc(sizeof(Trie));
    trie->root = trie_node_new();
    return trie;
}

void trie_destroy(Trie *trie) {
    trie_node_destroy(trie->root);
    free(trie);
}

TrieNode *trie_walk(TrieNode *root, const char *value, bool create) {
    TrieNode *current = root;
    for (const unsigned char *cursor = (const unsigned char *)value; *cursor; cursor++) {
        TrieEdge *edge = current->children;
        while (edge && edge->value != *cursor) edge = edge->next;
        if (!edge) {
            if (!create) return NULL;
            edge = malloc(sizeof(TrieEdge));
            edge->value = *cursor;
            edge->child = trie_node_new();
            edge->next = current->children;
            current->children = edge;
        }
        current = edge->child;
    }
    return current;
}

void trie_insert(Trie *trie, const char *word) {
    trie_walk(trie->root, word, true)->is_end = true;
}

bool trie_search(Trie *trie, const char *word) {
    TrieNode *node = trie_walk(trie->root, word, false);
    return node && node->is_end;
}

bool trie_starts_with(Trie *trie, const char *prefix) {
    return trie_walk(trie->root, prefix, false) != NULL;
}
```

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        current = self.root
        for character in word:
            current = current.children.setdefault(character, TrieNode())
        current.is_end = True

    def search(self, word):
        current = self.root
        for character in word:
            current = current.children.get(character)
            if current is None:
                return False
        return current.is_end

    def starts_with(self, prefix):
        current = self.root
        for character in prefix:
            current = current.children.get(character)
            if current is None:
                return False
        return True
```

```rust
use std::collections::HashMap;

#[derive(Default)]
struct TrieNode {
    children: HashMap<char, TrieNode>,
    is_end: bool,
}

pub struct Trie {
    root: TrieNode,
}

impl Trie {
    pub fn new() -> Self {
        Trie { root: TrieNode::default() }
    }

    pub fn insert(&mut self, word: &str) {
        let mut current = &mut self.root;
        for character in word.chars() {
            current = current.children.entry(character).or_default();
        }
        current.is_end = true;
    }

    pub fn search(&self, word: &str) -> bool {
        let mut current = &self.root;
        for character in word.chars() {
            match current.children.get(&character) {
                Some(node) => current = node,
                None => return false,
            }
        }
        current.is_end
    }

    pub fn starts_with(&self, prefix: &str) -> bool {
        let mut current = &self.root;
        for character in prefix.chars() {
            match current.children.get(&character) {
                Some(node) => current = node,
                None => return false,
            }
        }
        true
    }
}
```

```typescript
class TrieNode {
    children: Record<string, TrieNode> = {};
    isEnd = false;
}

export class Trie {
    private root = new TrieNode();

    insert(word: string): void {
        let current = this.root;
        for (const character of word) {
            const next = current.children[character];
            if (next) current = next;
            else {
                const node = new TrieNode();
                current.children[character] = node;
                current = node;
            }
        }
        current.isEnd = true;
    }

    search(word: string): boolean {
        let current: TrieNode | null = this.root;
        for (const character of word) {
            current = current.children[character];
            if (!current) return false;
        }
        return current.isEnd;
    }

    startsWith(prefix: string): boolean {
        let current: TrieNode | null = this.root;
        for (const character of prefix) {
            current = current.children[character];
            if (!current) return false;
        }
        return true;
    }
}
```

```go
package trie

type TrieNode struct {
	children map[rune]*TrieNode
	isEnd    bool
}

type Trie struct {
	root *TrieNode
}

func New() *Trie {
	return &Trie{root: &TrieNode{children: make(map[rune]*TrieNode)}}
}

func (trie *Trie) Insert(word string) {
	current := trie.root
	for _, character := range word {
		next := current.children[character]
		if next == nil {
			next = &TrieNode{children: make(map[rune]*TrieNode)}
			current.children[character] = next
		}
		current = next
	}
	current.isEnd = true
}

func (trie *Trie) Search(word string) bool {
	current := trie.root
	for _, character := range word {
		current = current.children[character]
		if current == nil {
			return false
		}
	}
	return current.isEnd
}

func (trie *Trie) StartsWith(prefix string) bool {
    current := trie.root
    for _, character := range prefix {
        current = current.children[character]
        if current == nil {
            return false
        }
    }
    return true
}
```

## Complexity
| Structure and operation | Time | Space or output |
| --- | --- | --- |
| Trie insert, exact search, or prefix search | O(L) | O(L) nodes per inserted key in the worst case |
| Radix-tree insert, exact search, or prefix search | O(L) | O(L) stored key bytes in the worst case |
| Suffix-tree construction | O(n) | O(n) |
| Suffix-tree substring search | O(m) | O(1) auxiliary space |
| Suffix-array construction with prefix doubling | O(n log n) | O(n) |
| Suffix-array substring search with LCP support | O(m + log n) | O(n) for the array and LCP data |

Here `L` is the inspected key length, `m` is the pattern length, and `n` is the fixed text length. Ukkonen's suffix-tree construction and linear-time suffix-array construction can reduce the corresponding O(n log n) build bound, at the cost of more involved algorithms.

## When to use
- You need exact-key or prefix lookup for a large set of strings.
- Shared prefixes dominate and ordered string traversal is not required.
- You need fixed-text substring, repeated-substring, or longest-common-substring queries.
- You need longest-prefix matching over router prefixes or another hierarchical address set.

## Alternatives
- **Hash table of strings** — gives expected O(L) exact lookup with simpler storage, but no direct prefix or ordered traversal.
- **Balanced search tree of strings** — gives O(L log n) worst-case comparison time and ordered iteration, with larger constants.
- **Ternary search tree** — can reduce node count with skewed string distributions, but lookup is O(L) only under balance conditions and is commonly O(L log n).
- **Suffix array** — has compact array storage and efficient binary search, but substring queries need LCP data or repeated comparisons.
- **Aho-Corasick automaton** — wins for matching many patterns in one pass, but costs more memory than independent tries.

## Related
- [Binary Search Trees](01-binary-search-trees.md)
- [Divide and Conquer Sorting](../03-paradigms/01-divide-and-conquer-sorting.md)
- [Amortized Analysis](../03-paradigms/05-amortized-analysis.md)
- [Finite Automata & Formal Languages](../04a-computational-theory/03-automata-formal-languages.md)
