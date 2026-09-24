---
title: "Tries and Suffix Trees"
weight: 6
toc: true
---

## What it is
A trie (prefix tree) is a tree in which each node represents a prefix of one or more keys, with edges labeled by characters and a flag marking complete keys. A suffix tree compresses all suffixes of a string (and, with a sentinel, all substrings) into a compact tree enabling fast substring and pattern queries.

## How it works
A trie stores each key by following one edge per character from the root, creating nodes on demand, and marking the final node as a terminal. Lookup, insertion, and prefix search each take O(L) time where L is the key length, independent of the number of stored keys. Suffix trees extend this idea to all suffixes of a single string, giving O(m) substring search for a pattern of length m.

A string is an array of characters.  It can also be represented as a Trie — a tree data structure that's composed of nodes that are prefixes of each character of the string leading to the full string.

```java
import java.util.HashMap;
import java.util.Map;

public class Trie {
    static class Node {
        Map<Character, Node> children = new HashMap<>();
        boolean isEnd = false;
    }

    private final Node root = new Node();

    public void insert(String word) {
        Node cur = root;
        for (char c : word.toCharArray())
            cur = cur.children.computeIfAbsent(c, k -> new Node());
        cur.isEnd = true;
    }

    public boolean search(String word) {
        Node cur = root;
        for (char c : word.toCharArray()) {
            cur = cur.children.get(c);
            if (cur == null) return false;
        }
        return cur.isEnd;
    }

    public boolean startsWith(String prefix) {
        Node cur = root;
        for (char c : prefix.toCharArray()) {
            cur = cur.children.get(c);
            if (cur == null) return false;
        }
        return true;
    }
}
```

```c
#include <stdbool.h>
#include <stdlib.h>

typedef struct TrieNode {
    struct TrieNode *children[26];
    bool is_end;
} TrieNode;

TrieNode *trie_node_new(void) {
    TrieNode *n = calloc(1, sizeof(TrieNode));
    return n;
}

void trie_insert(TrieNode *root, const char *word) {
    TrieNode *cur = root;
    for (const char *p = word; *p; p++) {
        int idx = *p - 'a';
        if (!cur->children[idx]) cur->children[idx] = trie_node_new();
        cur = cur->children[idx];
    }
    cur->is_end = true;
}

bool trie_search(TrieNode *root, const char *word) {
    TrieNode *cur = root;
    for (const char *p = word; *p; p++) {
        cur = cur->children[*p - 'a'];
        if (!cur) return false;
    }
    return cur->is_end;
}

bool trie_starts_with(TrieNode *root, const char *prefix) {
    TrieNode *cur = root;
    for (const char *p = prefix; *p; p++) {
        cur = cur->children[*p - 'a'];
        if (!cur) return false;
    }
    return true;
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
        cur = self.root
        for ch in word:
            cur = cur.children.setdefault(ch, TrieNode())
        cur.is_end = True

    def search(self, word):
        cur = self.root
        for ch in word:
            cur = cur.children.get(ch)
            if cur is None:
                return False
        return cur.is_end

    def starts_with(self, prefix):
        cur = self.root
        for ch in prefix:
            cur = cur.children.get(ch)
            if cur is None:
                return False
        return True
```

```rust
use std::collections::HashMap;

#[derive(Default)]
pub struct TrieNode {
    children: HashMap<char, TrieNode>,
    is_end: bool,
}

#[derive(Default)]
pub struct Trie {
    root: TrieNode,
}

impl Trie {
    pub fn insert(&mut self, word: &str) {
        let mut cur = &mut self.root;
        for c in word.chars() {
            cur = cur.children.entry(c).or_default();
        }
        cur.is_end = true;
    }

    pub fn search(&self, word: &str) -> bool {
        let mut cur = &self.root;
        for c in word.chars() {
            match cur.children.get(&c) {
                Some(n) => cur = n,
                None => return false,
            }
        }
        cur.is_end
    }

    pub fn starts_with(&self, prefix: &str) -> bool {
        let mut cur = &self.root;
        for c in prefix.chars() {
            match cur.children.get(&c) {
                Some(n) => cur = n,
                None => return false,
            }
        }
        true
    }
}
```

```typescript
interface TrieChildren {
    [key: string]: TrieNode;
}

class TrieNode {
    children: TrieChildren = {};
    isEnd = false;
}

export class Trie {
    private root = new TrieNode();

    insert(word: string): void {
        let cur = this.root;
        for (const c of word) {
            if (!cur.children[c]) cur.children[c] = new TrieNode();
            cur = cur.children[c];
        }
        cur.isEnd = true;
    }

    search(word: string): boolean {
        let cur = this.root;
        for (const c of word) {
            cur = cur.children[c];
            if (!cur) return false;
        }
        return cur.isEnd;
    }

    startsWith(prefix: string): boolean {
        let cur = this.root;
        for (const c of prefix) {
            cur = cur.children[c];
            if (!cur) return false;
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

func newTrieNode() *TrieNode {
	return &TrieNode{children: make(map[rune]*TrieNode)}
}

type Trie struct {
	root *TrieNode
}

func New() *Trie {
	return &Trie{root: newTrieNode()}
}

func (t *Trie) Insert(word string) {
	cur := t.root
	for _, c := range word {
		if cur.children[c] == nil {
			cur.children[c] = newTrieNode()
		}
		cur = cur.children[c]
	}
	cur.isEnd = true
}

func (t *Trie) Search(word string) bool {
	cur := t.root
	for _, c := range word {
		cur = cur.children[c]
		if cur == nil {
			return false
		}
	}
	return cur.isEnd
}

func (t *Trie) StartsWith(prefix string) bool {
	cur := t.root
	for _, c := range prefix {
		cur = cur.children[c]
		if cur == nil {
			return false
		}
	}
	return true
}
```

## Complexity
| Operation | Time | Space |
| --- | --- | --- |
| Trie insert | O(L) | O(L) per key |
| Trie search | O(L) | O(1) |
| Trie prefix search (startsWith) | O(L) | O(1) |
| Suffix tree build | O(n) | O(n) |
| Suffix tree substring search | O(m) | O(1) |

Here L is the length of the key and m the length of the pattern, independent of the total number of stored keys. A suffix tree over a string of length n can be built in O(n) time (Ukkonen's algorithm).

## When to use
- Autocomplete, spell-checking, and predictive text, where prefix lookups are the dominant query.
- IP routing (longest-prefix match) and dictionary implementations.
- Storing large sets of strings with shared prefixes to save memory over separate entries.
- Suffix tree: fast repeated substring, longest repeated substring, and longest common substring queries over a fixed text.

## Alternatives
- Hash table of strings — O(L) average lookup with less pointer overhead, but no prefix or ordered traversal.
- Balanced BST of strings — O(L log n) lookups with ordered iteration but slower and more memory.
- Ternary search tree — combines trie prefix behavior with BST memory efficiency at the cost of O(L log n)-ish average time.

## Related
- [Binary Search Trees](01-binary-search-trees.md)
- [Memory Works (Templates)](../../00-essentials/06-memory-works-templates.md)
