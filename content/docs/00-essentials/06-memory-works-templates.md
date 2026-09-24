---
title: "Memory Works (Templates)"
weight: 6
---


These templates are starting points, not substitutes for proving the invariant and choosing the
right representation. Adapt the names and stopping conditions to the problem.

1. Binary search
2. Backtracking
3. BFS (tree and graph)
4. DFS (tree and graph)
5. Topological sort
6. Trie
7. Union-Find

## Backtracking

```java
private static void dfs(
        List<Integer> state,
        List<List<Integer>> results,
        List<Integer> choices,
        Predicate<List<Integer>> isSolution) {
    if (isSolution.test(state)) {
        results.add(new ArrayList<>(state)); // add a copy of the state
        return;
    }
    for (int choice : choices) {
        state.add(choice);
        dfs(state, results, choices, isSolution);
        state.remove(state.size() - 1);
    }
}
```

```c
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

typedef int (*IsSolution)(const int *state, size_t state_len);

static void dfs(
        int **state,
        size_t *state_len,
        size_t *state_capacity,
        int ***results,
        size_t *results_len,
        size_t *results_capacity,
        const int *choices,
        size_t choices_len,
        IsSolution is_solution) {
    if (is_solution(*state, *state_len)) {
        int *copy = malloc(*state_len * sizeof(*copy));
        if (copy == NULL) abort();
        memcpy(copy, *state, *state_len * sizeof(*copy));
        if (*results_len == *results_capacity) {
            size_t capacity = *results_capacity == 0 ? 4 : *results_capacity * 2;
            int **grown = realloc(*results, capacity * sizeof(*grown));
            if (grown == NULL) abort();
            *results = grown;
            *results_capacity = capacity;
        }
        (*results)[(*results_len)++] = copy;
        return;
    }
    for (size_t i = 0; i < choices_len; i++) {
        if (*state_len == *state_capacity) {
            size_t capacity = *state_capacity == 0 ? 4 : *state_capacity * 2;
            int *grown = realloc(*state, capacity * sizeof(*grown));
            if (grown == NULL) abort();
            *state = grown;
            *state_capacity = capacity;
        }
        (*state)[(*state_len)++] = choices[i];
        dfs(state, state_len, state_capacity, results, results_len,
            results_capacity, choices, choices_len, is_solution);
    }
}
```

```python
def dfs(state, results, choices, is_solution):
    if is_solution(state):
        results.append(state.copy())
        return
    for choice in choices:
        state.append(choice)
        dfs(state, results, choices, is_solution)
        state.pop()
```

```rust
fn dfs(
    state: &mut Vec<i32>,
    results: &mut Vec<Vec<i32>>,
    choices: &[i32],
    is_solution: &dyn Fn(&[i32]) -> bool,
) {
    if is_solution(state) {
        results.push(state.clone());
        return;
    }
    for &choice in choices {
        state.push(choice);
        dfs(state, results, choices, is_solution);
        state.pop();
    }
}
```

```typescript
function dfs(
  state: number[],
  results: number[][],
  choices: number[],
  isSolution: (state: number[]) => boolean,
): void {
  if (isSolution(state)) {
    results.push([...state]);
    return;
  }
  for (const choice of choices) {
    state.push(choice);
    dfs(state, results, choices, isSolution);
    state.pop();
  }
}
```

```go
func DFS(
	state []int,
	results *[][]int,
	choices []int,
	isSolution func([]int) bool,
) {
	if isSolution(state) {
		stateCopy := make([]int, len(state))
		copy(stateCopy, state)
		*results = append(*results, stateCopy)
		return
	}
	for _, choice := range choices {
		state = append(state, choice)
		DFS(state, results, choices, isSolution)
		state = state[:len(state)-1]
	}
}
```

## Binary Search

```java
public static int binarySearch(List<Integer> arr, int target) {
    int left = 0;
    int right = arr.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        int value = arr.get(mid);
        if (value == target) return mid;
        if (value < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    return -1;
}
```

```c
#include <stddef.h>

int binary_search(const int *arr, size_t len, int target) {
    size_t left = 0;
    size_t right = len;
    while (left < right) {
        size_t mid = left + (right - left) / 2;
        if (arr[mid] == target) return (int)mid;
        if (arr[mid] < target) {
            left = mid + 1;
        } else {
            right = mid;
        }
    }
    return -1;
}
```

```python
def binary_search(arr, target):
    left = 0
    right = len(arr) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

```rust
fn binary_search(arr: &[i32], target: i32) -> i32 {
    let mut left = 0;
    let mut right = arr.len();
    while left < right {
        let mid = left + (right - left) / 2;
        if arr[mid] == target {
            return mid as i32;
        }
        if arr[mid] < target {
            left = mid + 1;
        } else {
            right = mid;
        }
    }
    -1
}
```

```typescript
function binarySearch(arr: number[], target: number): number {
  let left = 0;
  let right = arr.length - 1;
  while (left <= right) {
    const mid = left + Math.floor((right - left) / 2);
    if (arr[mid] === target) return mid;
    if (arr[mid] < target) {
      left = mid + 1;
    } else {
      right = mid - 1;
    }
  }
  return -1;
}
```

```go
func BinarySearch(arr []int, target int) int {
	left := 0
	right := len(arr) - 1
	for left <= right {
		mid := left + (right-left)/2
		if arr[mid] == target {
			return mid
		}
		if arr[mid] < target {
			left = mid + 1
		} else {
			right = mid - 1
		}
	}
	return -1
}
```

## BFS on Tree

```java
public static class Node {
    int value;
    List<Node> children = new ArrayList<>();
}

public static Node bfs(Node root, int target) {
    ArrayDeque<Node> queue = new ArrayDeque<>();
    if (root == null) return null;
    queue.add(root);
    while (!queue.isEmpty()) {
        Node node = queue.poll();
        if (node.value == target) return node;
        queue.addAll(node.children);
    }
    return null;
}
```

```c
#include <stddef.h>
#include <stdlib.h>

typedef struct Node {
    int value;
    struct Node **children;
    size_t child_count;
} Node;

Node *bfs(Node *root, int target) {
    if (root == NULL) return NULL;
    Node **queue = NULL;
    size_t head = 0;
    size_t len = 0;
    size_t capacity = 0;
    queue = malloc(sizeof(*queue));
    if (queue == NULL) abort();
    queue[len++] = root;
    while (head < len) {
        Node *node = queue[head++];
        if (node->value == target) {
            free(queue);
            return node;
        }
        if (len + node->child_count > capacity) {
            capacity = len + node->child_count;
            Node **grown = realloc(queue, capacity * sizeof(*grown));
            if (grown == NULL) abort();
            queue = grown;
        }
        for (size_t i = 0; i < node->child_count; i++) {
            queue[len++] = node->children[i];
        }
    }
    free(queue);
    return NULL;
}
```

```python
from collections import deque

class Node:
    def __init__(self, value, children=()):
        self.value = value
        self.children = list(children)


def bfs(root, target):
    if root is None:
        return None
    queue = deque([root])
    while queue:
        node = queue.popleft()
        if node.value == target:
            return node
        queue.extend(node.children)
    return None
```

```rust
use std::collections::VecDeque;

struct Node {
    value: i32,
    children: Vec<Node>,
}

fn bfs(root: Option<&Node>, target: i32) -> Option<&Node> {
    let mut queue = VecDeque::new();
    if let Some(root) = root {
        queue.push_back(root);
    }
    while let Some(node) = queue.pop_front() {
        if node.value == target {
            return Some(node);
        }
        queue.extend(&node.children);
    }
    None
}
```

```typescript
interface Node {
  value: number;
  children: Node[];
}

function bfs(root: Node | null, target: number): Node | null {
  if (root === null) return null;
  const queue: Node[] = [root];
  for (let head = 0; head < queue.length; head++) {
    const node = queue[head];
    if (node.value === target) return node;
    queue.push(...node.children);
  }
  return null;
}
```

```go
type Node struct {
	Value    int
	Children []*Node
}

func BFS(root *Node, target int) *Node {
	if root == nil {
		return nil
	}
	queue := []*Node{root}
	for head := 0; head < len(queue); head++ {
		node := queue[head]
		if node.Value == target {
			return node
		}
		queue = append(queue, node.Children...)
	}
	return nil
}
```

## DFS on Tree

```java
public static class Node {
    int value;
    Node left;
    Node right;
}

public static Node dfs(Node root, int target) {
    if (root == null) return null;
    if (root.value == target) return root;
    Node left = dfs(root.left, target);
    if (left != null) return left;
    return dfs(root.right, target);
}
```

```c
#include <stddef.h>

typedef struct Node {
    int value;
    struct Node *left;
    struct Node *right;
} Node;

Node *dfs(Node *root, int target) {
    if (root == NULL) return NULL;
    if (root->value == target) return root;
    Node *left = dfs(root->left, target);
    if (left != NULL) return left;
    return dfs(root->right, target);
}
```

```python
class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


def dfs(root, target):
    if root is None:
        return None
    if root.value == target:
        return root
    left = dfs(root.left, target)
    if left is not None:
        return left
    return dfs(root.right, target)
```

```rust
struct Node {
    value: i32,
    left: Option<Box<Node>>,
    right: Option<Box<Node>>,
}

fn dfs(root: Option<&Node>, target: i32) -> Option<&Node> {
    let root = root?;
    if root.value == target {
        return Some(root);
    }
    if let Some(node) = dfs(root.left.as_deref(), target) {
        return Some(node);
    }
    dfs(root.right.as_deref(), target)
}
```

```typescript
interface Node {
  value: number;
  left: Node | null;
  right: Node | null;
}

function dfs(root: Node | null, target: number): Node | null {
  if (root === null) return null;
  if (root.value === target) return root;
  const left = dfs(root.left, target);
  if (left !== null) return left;
  return dfs(root.right, target);
}
```

```go
type Node struct {
	Value int
	Left  *Node
	Right *Node
}

func DFS(root *Node, target int) *Node {
	if root == nil {
		return nil
	}
	if root.Value == target {
		return root
	}
	left := DFS(root.Left, target)
	if left != nil {
		return left
	}
	return DFS(root.Right, target)
}
```

## BFS on Graphs

```java
public static class Node {
    int value;
    List<Node> neighbors = new ArrayList<>();
}

public static void bfs(Node root) {
    ArrayDeque<Node> queue = new ArrayDeque<>();
    queue.add(root);
    Set<Node> visited = new HashSet<>();
    visited.add(root);
    while (!queue.isEmpty()) {
        Node node = queue.poll();
        for (Node neighbor : node.neighbors) {
            if (visited.add(neighbor)) {
                queue.add(neighbor);
            }
        }
    }
}
```

```c
#include <stddef.h>
#include <stdlib.h>

typedef struct Node {
    int value;
    struct Node **neighbors;
    size_t neighbor_count;
} Node;

void bfs(Node *root) {
    Node **queue = malloc(sizeof(*queue));
    if (queue == NULL) abort();
    size_t head = 0;
    size_t len = 0;
    size_t capacity = 1;
    Node **visited = malloc(sizeof(*visited));
    if (visited == NULL) abort();
    size_t visited_len = 0;
    size_t visited_capacity = 1;
    queue[len++] = root;
    visited[visited_len++] = root;
    while (head < len) {
        Node *node = queue[head++];
        for (size_t i = 0; i < node->neighbor_count; i++) {
            Node *neighbor = node->neighbors[i];
            int found = 0;
            for (size_t j = 0; j < visited_len; j++) {
                if (visited[j] == neighbor) {
                    found = 1;
                    break;
                }
            }
            if (!found) {
                if (len == capacity) {
                    capacity *= 2;
                    Node **grown = realloc(queue, capacity * sizeof(*grown));
                    if (grown == NULL) abort();
                    queue = grown;
                }
                if (visited_len == visited_capacity) {
                    visited_capacity *= 2;
                    Node **grown = realloc(visited, visited_capacity * sizeof(*grown));
                    if (grown == NULL) abort();
                    visited = grown;
                }
                queue[len++] = neighbor;
                visited[visited_len++] = neighbor;
            }
        }
    }
    free(queue);
    free(visited);
}
```

```python
from collections import deque

class Node:
    def __init__(self, value, neighbors=()):
        self.value = value
        self.neighbors = list(neighbors)


def bfs(root):
    queue = deque([root])
    visited = {root}
    while queue:
        node = queue.popleft()
        for neighbor in node.neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
```

```rust
use std::collections::VecDeque;

struct Node {
    value: i32,
    neighbors: Vec<Node>,
}

fn bfs(root: &Node) {
    let mut queue = VecDeque::new();
    let mut visited = std::collections::HashSet::new();
    queue.push_back(root);
    visited.insert(root as *const Node);
    while let Some(node) = queue.pop_front() {
        for neighbor in &node.neighbors {
            if visited.insert(neighbor as *const Node) {
                queue.push_back(neighbor);
            }
        }
    }
}
```

```typescript
interface Node {
  value: number;
  neighbors: Node[];
}

function bfs(root: Node): void {
  const queue: Node[] = [root];
  const visited = new Set<Node>([root]);
  for (let head = 0; head < queue.length; head++) {
    const node = queue[head];
    for (const neighbor of node.neighbors) {
      if (!visited.has(neighbor)) {
        visited.add(neighbor);
        queue.push(neighbor);
      }
    }
  }
}
```

```go
type Node struct {
	Value     int
	Neighbors []*Node
}

func BFS(root *Node) {
	queue := []*Node{root}
	visited := map[*Node]bool{root: true}
	for head := 0; head < len(queue); head++ {
		node := queue[head]
		for _, neighbor := range node.Neighbors {
			if !visited[neighbor] {
				visited[neighbor] = true
				queue = append(queue, neighbor)
			}
		}
	}
}
```

## DFS on Graphs

```java
public static class Node {
    int value;
    List<Node> neighbors = new ArrayList<>();
}

public static void dfs(Node root, Set<Node> visited) {
    if (root == null || !visited.add(root)) return;
    for (Node neighbor : root.neighbors) {
        dfs(neighbor, visited);
    }
}
```

```c
#include <stddef.h>

typedef struct Node {
    int value;
    struct Node **neighbors;
    size_t neighbor_count;
} Node;

int node_visited(Node *const *visited, size_t visited_len, Node *node) {
    for (size_t i = 0; i < visited_len; i++) {
        if (visited[i] == node) return 1;
    }
    return 0;
}

void dfs(Node *root, Node **visited, size_t *visited_len) {
    if (root == NULL || node_visited(visited, *visited_len, root)) return;
    visited[(*visited_len)++] = root;
    for (size_t i = 0; i < root->neighbor_count; i++) {
        dfs(root->neighbors[i], visited, visited_len);
    }
}
```

```python
class Node:
    def __init__(self, value, neighbors=()):
        self.value = value
        self.neighbors = list(neighbors)


def dfs(root, visited):
    if root is None or id(root) in visited:
        return
    visited.add(id(root))
    for neighbor in root.neighbors:
        dfs(neighbor, visited)
```

```rust
use std::collections::HashSet;

struct Node {
    value: i32,
    neighbors: Vec<Node>,
}

fn dfs(root: Option<&Node>, visited: &mut HashSet<*const Node>) {
    let Some(root) = root else {
        return;
    };
    if !visited.insert(root as *const Node) {
        return;
    }
    for neighbor in &root.neighbors {
        dfs(Some(neighbor), visited);
    }
}
```

```typescript
interface Node {
  value: number;
  neighbors: Node[];
}

function dfs(root: Node | null, visited: Set<Node>): void {
  if (root === null || visited.has(root)) return;
  visited.add(root);
  for (const neighbor of root.neighbors) {
    dfs(neighbor, visited);
  }
}
```

```go
type Node struct {
	Value     int
	Neighbors []*Node
}

func DFS(root *Node, visited map[*Node]bool) {
	if root == nil || visited[root] {
		return
	}
	visited[root] = true
	for _, neighbor := range root.Neighbors {
		DFS(neighbor, visited)
	}
}
```

## Topological sort

```java
public static <T> Map<T, Integer> countParents(Map<T, List<T>> graph) {
    Map<T, Integer> counts = new HashMap<>();
    graph.keySet().forEach(node -> counts.put(node, 0));
    graph.entrySet().forEach(entry -> {
        for (T node : entry.getValue()) {
            counts.put(node, counts.get(node) + 1);
        }
    });
    return counts;
}

public static <T> List<T> topoSort(Map<T, List<T>> graph) {
    List<T> res = new ArrayList<>();
    Queue<T> q = new ArrayDeque<>();
    Map<T, Integer> counts = countParents(graph);
    counts.entrySet().forEach(entry -> {
        if (entry.getValue() == 0) {
            q.add(entry.getKey());
        }
    });
    while (!q.isEmpty()) {
        T node = q.poll();
        res.add(node);
        for (T child : graph.get(node)) {
            counts.put(child, counts.get(child) - 1);
            if (counts.get(child) == 0) {
                q.add(child);
            }
        }
    }
    return res;
}
```

```c
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

typedef struct Graph {
    size_t node_count;
    const size_t (*edges)[2];
    size_t edge_count;
} Graph;

size_t count_parents(const Graph *graph, size_t *counts) {
    memset(counts, 0, graph->node_count * sizeof(*counts));
    for (size_t i = 0; i < graph->edge_count; i++) {
        counts[graph->edges[i][1]]++;
    }
    return graph->node_count;
}

bool topo_sort(
        const Graph *graph,
        size_t *result,
        size_t *result_len) {
    size_t *counts = calloc(graph->node_count, sizeof(*counts));
    size_t *queue = malloc(graph->node_count * sizeof(*queue));
    if (counts == NULL || queue == NULL) abort();
    count_parents(graph, counts);
    size_t head = 0;
    size_t len = 0;
    for (size_t node = 0; node < graph->node_count; node++) {
        if (counts[node] == 0) queue[len++] = node;
    }
    *result_len = 0;
    while (head < len) {
        size_t node = queue[head++];
        result[(*result_len)++] = node;
        for (size_t i = 0; i < graph->edge_count; i++) {
            size_t child = graph->edges[i][1];
            if (graph->edges[i][0] != node) continue;
            if (--counts[child] == 0) queue[len++] = child;
        }
    }
    bool success = *result_len == graph->node_count;
    free(counts);
    free(queue);
    return success;
}
```

```python
from collections import deque


def count_parents(graph):
    counts = {node: 0 for node in graph}
    for children in graph.values():
        for child in children:
            counts.setdefault(child, 0)
            counts[child] += 1
    return counts


def topo_sort(graph):
    result = []
    queue = deque(node for node, count in count_parents(graph).items() if count == 0)
    counts = count_parents(graph)
    while queue:
        node = queue.popleft()
        result.append(node)
        for child in graph[node]:
            counts[child] -= 1
            if counts[child] == 0:
                queue.append(child)
    return result
```

```rust
use std::collections::{HashMap, VecDeque};
use std::hash::Hash;

fn count_parents<T: Eq + Hash + Clone>(graph: &HashMap<T, Vec<T>>) -> HashMap<T, usize> {
    let mut counts: HashMap<T, usize> = graph.keys().map(|node| (node.clone(), 0)).collect();
    for children in graph.values() {
        for child in children {
            *counts.entry(child.clone()).or_insert(0) += 1;
        }
    }
    counts
}

fn topo_sort<T: Eq + Hash + Clone>(graph: &HashMap<T, Vec<T>>) -> Vec<T> {
    let mut counts = count_parents(graph);
    let mut queue: VecDeque<T> = counts
        .iter()
        .filter(|(_, count)| **count == 0)
        .map(|(node, _)| node.clone())
        .collect();
    let mut result = Vec::new();
    while let Some(node) = queue.pop_front() {
        result.push(node.clone());
        if let Some(children) = graph.get(&node) {
            for child in children {
                let count = counts.get_mut(child).unwrap();
                *count -= 1;
                if *count == 0 {
                    queue.push_back(child.clone());
                }
            }
        }
    }
    result
}
```

```typescript
function countParents<T>(graph: Map<T, T[]>): Map<T, number> {
  const counts = new Map<T, number>();
  for (const node of graph.keys()) {
    counts.set(node, 0);
  }
  for (const children of graph.values()) {
    for (const child of children) {
      counts.set(child, (counts.get(child) ?? 0) + 1);
    }
  }
  return counts;
}

function topoSort<T>(graph: Map<T, T[]>): T[] {
  const result: T[] = [];
  const queue: T[] = [];
  const counts = countParents(graph);
  for (const [node, count] of counts) {
    if (count === 0) queue.push(node);
  }
  for (let head = 0; head < queue.length; head++) {
    const node = queue[head];
    result.push(node);
    for (const child of graph.get(node) ?? []) {
      const count = counts.get(child)! - 1;
      counts.set(child, count);
      if (count === 0) queue.push(child);
    }
  }
  return result;
}
```

```go
func CountParents[T comparable](graph map[T][]T) map[T]int {
	counts := make(map[T]int, len(graph))
	for node := range graph {
		counts[node] = 0
	}
	for _, children := range graph {
		for _, child := range children {
			counts[child]++
		}
	}
	return counts
}

func TopoSort[T comparable](graph map[T][]T) []T {
	result := make([]T, 0, len(graph))
	queue := make([]T, 0, len(graph))
	counts := CountParents(graph)
	for node, count := range counts {
		if count == 0 {
			queue = append(queue, node)
		}
	}
	for head := 0; head < len(queue); head++ {
		node := queue[head]
		result = append(result, node)
		for _, child := range graph[node] {
			counts[child]--
			if counts[child] == 0 {
				queue = append(queue, child)
			}
		}
	}
	return result
}
```

## Trie

```java
import java.util.HashMap;
import java.util.Map;

public class Trie {
    char value;
    Map<Character, Trie> children = new HashMap<>();

    public Trie(char value) {
        this.value = value;
    }

    public void insert(String s, int idx) {
        if (idx == s.length()) return;
        char character = s.charAt(idx);
        Trie child = children.get(character);
        if (child == null) {
            child = new Trie(character);
            children.put(character, child);
        }
        child.insert(s, idx + 1);
    }
}
```

```c
#include <stddef.h>
#include <stdlib.h>

typedef struct Trie {
    char value;
    struct Trie *children;
    size_t child_count;
} Trie;

Trie *trie_find_child(Trie *node, char value) {
    for (size_t i = 0; i < node->child_count; i++) {
        if (node->children[i].value == value) return &node->children[i];
    }
    return NULL;
}

void trie_insert(Trie *node, const char *s, size_t idx) {
    if (s[idx] == '\0') return;
    Trie *child = trie_find_child(node, s[idx]);
    if (child == NULL) {
        Trie *children = realloc(node->children, (node->child_count + 1) * sizeof(*children));
        if (children == NULL) abort();
        node->children = children;
        child = &node->children[node->child_count++];
        child->value = s[idx];
        child->children = NULL;
        child->child_count = 0;
    }
    trie_insert(child, s, idx + 1);
}
```

```python
class Trie:
    def __init__(self, value=None):
        self.value = value
        self.children = {}

    def insert(self, s, idx=0):
        if idx == len(s):
            return
        character = s[idx]
        if character not in self.children:
            self.children[character] = Trie(character)
        self.children[character].insert(s, idx + 1)
```

```rust
use std::collections::HashMap;

struct Trie {
    value: char,
    children: HashMap<char, Trie>,
}

impl Trie {
    fn insert(&mut self, s: &str, idx: usize) {
        let characters: Vec<char> = s.chars().collect();
        if idx >= characters.len() {
            return;
        }
        let character = characters[idx];
        let child = self
            .children
            .entry(character)
            .or_insert(Self {
                value: character,
                children: HashMap::new(),
            });
        child.insert(s, idx + 1);
    }
}
```

```typescript
class Trie {
  value: string;
  children: Map<string, Trie>;

  constructor(value: string) {
    this.value = value;
    this.children = new Map();
  }

  insert(s: string, idx = 0): void {
    if (idx === s.length) return;
    const character = s[idx];
    let child = this.children.get(character);
    if (!child) {
      child = new Trie(character);
      this.children.set(character, child);
    }
    child.insert(s, idx + 1);
  }
}
```

```go
type Trie struct {
	value    rune
	children map[rune]*Trie
}

func NewTrie(value rune) *Trie {
	return &Trie{value: value, children: make(map[rune]*Trie)}
}

func (trie *Trie) Insert(s string, idx int) {
	if idx == len(s) {
		return
	}
	character := []rune(s)[idx]
	child, ok := trie.children[character]
	if !ok {
		child = NewTrie(character)
		trie.children[character] = child
	}
	child.Insert(s, idx+1)
}
```

## Union-Find

```java
import java.util.HashMap;

public class UnionFind<T> {
    private HashMap<T, T> f = new HashMap<>();

    public T find(T x) {
        T y = f.getOrDefault(x, x);
        if (!y.equals(x)) {
            y = find(y);
            f.put(x, y);
        }
        return y;
    }

    public void union(T x, T y) {
        f.put(find(x), find(y));
    }
}
```

```c
#include <stddef.h>
#include <stdlib.h>

typedef int (*EqualKey)(const void *, const void *);

typedef struct {
    void *key;
    void *parent;
} UnionFindEntry;

typedef struct {
    UnionFindEntry *entries;
    size_t len;
    size_t capacity;
    EqualKey equal;
} UnionFind;

void union_find_init(UnionFind *uf, EqualKey equal) {
    uf->entries = NULL;
    uf->len = 0;
    uf->capacity = 0;
    uf->equal = equal;
}

void union_find_destroy(UnionFind *uf) {
    free(uf->entries);
}

void *union_find_find(UnionFind *uf, void *key) {
    size_t i = 0;
    while (i < uf->len && !uf->equal(uf->entries[i].key, key)) i++;
    if (i == uf->len) return key;
    void *parent = uf->entries[i].parent;
    if (uf->equal(key, parent)) return parent;
    void *root = union_find_find(uf, parent);
    uf->entries[i].parent = root;
    return root;
}

void union_find_union(UnionFind *uf, void *x, void *y) {
    void *root_x = union_find_find(uf, x);
    void *root_y = union_find_find(uf, y);
    if (uf->equal(root_x, root_y)) return;
    size_t i = 0;
    while (i < uf->len && !uf->equal(uf->entries[i].key, x)) i++;
    if (i == uf->len) {
        if (uf->len == uf->capacity) {
            size_t capacity = uf->capacity == 0 ? 4 : uf->capacity * 2;
            UnionFindEntry *grown = realloc(uf->entries, capacity * sizeof(*grown));
            if (grown == NULL) abort();
            uf->entries = grown;
            uf->capacity = capacity;
        }
        uf->entries[uf->len++] = (UnionFindEntry){x, root_y};
    } else {
        uf->entries[i].parent = root_y;
    }
}
```

```python
class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        parent = self.parent.get(x, x)
        if parent != x:
            parent = self.find(parent)
            self.parent[x] = parent
        return parent

    def union(self, x, y):
        self.parent[self.find(x)] = self.find(y)
```

```rust
use std::collections::HashMap;
use std::hash::Hash;

struct UnionFind<T: Eq + Hash + Clone> {
    parent: HashMap<T, T>,
}

impl<T: Eq + Hash + Clone> UnionFind<T> {
    fn new() -> Self {
        Self {
            parent: HashMap::new(),
        }
    }

    fn find(&mut self, x: &T) -> T {
        let parent = self.parent.get(x).cloned().unwrap_or_else(|| x.clone());
        if parent == *x {
            return parent;
        }
        let root = self.find(&parent);
        self.parent.insert(x.clone(), root.clone());
        root
    }

    fn union(&mut self, x: &T, y: &T) {
        let root_x = self.find(x);
        let root_y = self.find(y);
        self.parent.insert(root_x, root_y);
    }
}
```

```typescript
class UnionFind<T> {
  private parent: Map<T, T> = new Map();

  find(x: T): T {
    let parent = this.parent.get(x) ?? x;
    if (parent !== x) {
      parent = this.find(parent);
      this.parent.set(x, parent);
    }
    return parent;
  }

  union(x: T, y: T): void {
    this.parent.set(this.find(x), this.find(y));
  }
}
```

```go
type UnionFind[T comparable] struct {
	parent map[T]T
}

func NewUnionFind[T comparable]() *UnionFind[T] {
	return &UnionFind[T]{parent: make(map[T]T)}
}

func (uf *UnionFind[T]) Find(x T) T {
	parent, ok := uf.parent[x]
	if !ok {
		return x
	}
	if parent == x {
		return parent
	}
	root := uf.Find(parent)
	uf.parent[x] = root
	return root
}

func (uf *UnionFind[T]) Union(x, y T) {
	uf.parent[uf.Find(x)] = uf.Find(y)
}
```
