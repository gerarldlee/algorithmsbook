---
title: "Topological Sorting & Strongly Connected Components (Tarjan’s, Kosaraju’s)"
weight: 3
toc: true
---

## What it is
**Topological sorting** orders a directed acyclic graph so every edge points from an earlier vertex to a later one, while **strongly connected components (SCCs)** partition a directed graph into maximal groups whose vertices can all reach one another.

## How it works
Kahn's algorithm repeatedly removes vertices with in-degree zero, and a short result reveals a cycle. Tarjan's DFS maintains discovery indices and low-link values, popping vertices from an active stack when a root is found. Kosaraju's algorithm records DFS finish order, traverses the transposed graph in reverse finish order, and assigns one SCC to each traversal. The examples implement all three operations with adjacency lists.

```java
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Deque;
import java.util.List;

public final class TopologicalSCC {
    private TopologicalSCC() {}

    public static List<Integer> topologicalSort(List<List<Integer>> adjacency) {
        int vertexCount = adjacency.size();
        int[] inDegree = new int[vertexCount];
        for (List<Integer> neighbors : adjacency) {
            for (int neighbor : neighbors) inDegree[neighbor]++;
        }
        Deque<Integer> queue = new ArrayDeque<>();
        for (int vertex = 0; vertex < vertexCount; vertex++) {
            if (inDegree[vertex] == 0) queue.add(vertex);
        }
        List<Integer> order = new ArrayList<>();
        while (!queue.isEmpty()) {
            int vertex = queue.removeFirst();
            order.add(vertex);
            for (int neighbor : adjacency.get(vertex)) {
                if (--inDegree[neighbor] == 0) queue.add(neighbor);
            }
        }
        return order.size() == vertexCount ? order : List.of();
    }

    public static List<List<Integer>> tarjan(List<List<Integer>> adjacency) {
        int vertexCount = adjacency.size();
        int[] discovery = new int[vertexCount];
        int[] low = new int[vertexCount];
        Arrays.fill(discovery, -1);
        boolean[] onStack = new boolean[vertexCount];
        Deque<Integer> stack = new ArrayDeque<>();
        List<List<Integer>> components = new ArrayList<>();
        int[] nextIndex = {0};
        for (int vertex = 0; vertex < vertexCount; vertex++) {
            if (discovery[vertex] == -1) strongConnect(adjacency, vertex, discovery, low, onStack, stack, components, nextIndex);
        }
        return components;
    }

    private static void strongConnect(List<List<Integer>> adjacency, int vertex, int[] discovery, int[] low, boolean[] onStack, Deque<Integer> stack, List<List<Integer>> components, int[] nextIndex) {
        discovery[vertex] = low[vertex] = nextIndex[0]++;
        stack.push(vertex);
        onStack[vertex] = true;
        for (int neighbor : adjacency.get(vertex)) {
            if (discovery[neighbor] == -1) {
                strongConnect(adjacency, neighbor, discovery, low, onStack, stack, components, nextIndex);
                low[vertex] = Math.min(low[vertex], low[neighbor]);
            } else if (onStack[neighbor]) {
                low[vertex] = Math.min(low[vertex], discovery[neighbor]);
            }
        }
        if (low[vertex] == discovery[vertex]) {
            List<Integer> component = new ArrayList<>();
            int current;
            do {
                current = stack.pop();
                onStack[current] = false;
                component.add(current);
            } while (current != vertex);
            components.add(component);
        }
    }

    public static List<List<Integer>> kosaraju(List<List<Integer>> adjacency) {
        int vertexCount = adjacency.size();
        boolean[] visited = new boolean[vertexCount];
        List<Integer> finishOrder = new ArrayList<>();
        for (int vertex = 0; vertex < vertexCount; vertex++) {
            if (!visited[vertex]) finish(adjacency, vertex, visited, finishOrder);
        }
        List<List<Integer>> transposed = transpose(adjacency);
        Arrays.fill(visited, false);
        List<List<Integer>> components = new ArrayList<>();
        for (int index = vertexCount - 1; index >= 0; index--) {
            int vertex = finishOrder.get(index);
            if (!visited[vertex]) {
                List<Integer> component = new ArrayList<>();
                collect(transposed, vertex, visited, component);
                components.add(component);
            }
        }
        return components;
    }

    private static void finish(List<List<Integer>> adjacency, int vertex, boolean[] visited, List<Integer> order) {
        visited[vertex] = true;
        for (int neighbor : adjacency.get(vertex)) {
            if (!visited[neighbor]) finish(adjacency, neighbor, visited, order);
        }
        order.add(vertex);
    }

    private static List<List<Integer>> transpose(List<List<Integer>> adjacency) {
        List<List<Integer>> transposed = new ArrayList<>();
        for (int vertex = 0; vertex < adjacency.size(); vertex++) transposed.add(new ArrayList<>());
        for (int vertex = 0; vertex < adjacency.size(); vertex++) {
            for (int neighbor : adjacency.get(vertex)) transposed.get(neighbor).add(vertex);
        }
        return transposed;
    }

    private static void collect(List<List<Integer>> transposed, int vertex, boolean[] visited, List<Integer> component) {
        Deque<Integer> stack = new ArrayDeque<>();
        stack.push(vertex);
        visited[vertex] = true;
        while (!stack.isEmpty()) {
            int current = stack.pop();
            component.add(current);
            for (int neighbor : transposed.get(current)) {
                if (!visited[neighbor]) {
                    visited[neighbor] = true;
                    stack.push(neighbor);
                }
            }
        }
    }
}
```

```c
#include <stdbool.h>
#include <stdlib.h>

typedef struct Node {
    int vertex;
    struct Node* next;
} Node;

typedef struct {
    int size;
    int capacity;
    int* values;
} IntSlice;

typedef struct {
    int size;
    IntSlice* values;
} SliceList;

static void slice_append(IntSlice* slice, int value) {
    if (slice->size == slice->capacity) {
        slice->capacity = slice->capacity == 0 ? 4 : slice->capacity * 2;
        slice->values = realloc(slice->values, slice->capacity * sizeof(int));
    }
    slice->values[slice->size++] = value;
}

static void list_append(SliceList* list, IntSlice value) {
    list->values = realloc(list->values, (list->size + 1) * sizeof(IntSlice));
    list->values[list->size++] = value;
}

int topological_scc_topological_sort(Node** adjacency, int vertex_count, IntSlice* order) {
    int* in_degree = calloc(vertex_count, sizeof(int));
    int* queue = malloc(vertex_count * sizeof(int));
    int head = 0;
    int tail = 0;
    order->size = 0;
    order->capacity = vertex_count;
    order->values = malloc(vertex_count * sizeof(int));
    for (int vertex = 0; vertex < vertex_count; vertex++) {
        for (Node* node = adjacency[vertex]; node; node = node->next) in_degree[node->vertex]++;
    }
    for (int vertex = 0; vertex < vertex_count; vertex++) {
        if (in_degree[vertex] == 0) queue[tail++] = vertex;
    }
    while (head < tail) {
        int vertex = queue[head++];
        order->values[order->size++] = vertex;
        for (Node* node = adjacency[vertex]; node; node = node->next) {
            if (--in_degree[node->vertex] == 0) queue[tail++] = node->vertex;
        }
    }
    free(in_degree);
    free(queue);
    if (order->size != vertex_count) {
        free(order->values);
        order->values = NULL;
        order->size = 0;
    }
    return order->size == vertex_count;
}

typedef struct {
    Node** adjacency;
    int vertex_count;
    int next_index;
    int* discovery;
    int* low;
    bool* on_stack;
    int* stack;
    int stack_size;
    SliceList* components;
} TarjanState;

static void tarjan_connect(TarjanState* state, int vertex) {
    state->discovery[vertex] = state->low[vertex] = state->next_index++;
    state->stack[state->stack_size++] = vertex;
    state->on_stack[vertex] = true;
    for (Node* node = state->adjacency[vertex]; node; node = node->next) {
        int neighbor = node->vertex;
        if (state->discovery[neighbor] == -1) {
            tarjan_connect(state, neighbor);
            if (state->low[neighbor] < state->low[vertex]) state->low[vertex] = state->low[neighbor];
        } else if (state->on_stack[neighbor] && state->discovery[neighbor] < state->low[vertex]) {
            state->low[vertex] = state->discovery[neighbor];
        }
    }
    if (state->low[vertex] == state->discovery[vertex]) {
        IntSlice component = {0, 0, NULL};
        while (state->stack_size > 0) {
            int current = state->stack[--state->stack_size];
            state->on_stack[current] = false;
            slice_append(&component, current);
            if (current == vertex) break;
        }
        list_append(state->components, component);
    }
}

int topological_scc_tarjan(Node** adjacency, int vertex_count, SliceList* components) {
    TarjanState state = {adjacency, vertex_count, 0};
    state.discovery = malloc(vertex_count * sizeof(int));
    state.low = malloc(vertex_count * sizeof(int));
    state.on_stack = calloc(vertex_count, sizeof(bool));
    state.stack = malloc(vertex_count * sizeof(int));
    state.components = components;
    components->size = 0;
    components->values = NULL;
    for (int vertex = 0; vertex < vertex_count; vertex++) state.discovery[vertex] = -1;
    for (int vertex = 0; vertex < vertex_count; vertex++) {
        if (state.discovery[vertex] == -1) tarjan_connect(&state, vertex);
    }
    free(state.discovery);
    free(state.low);
    free(state.on_stack);
    free(state.stack);
    return 1;
}

static void kosaraju_finish(Node** adjacency, int vertex, bool* visited, int* finish_order, int* count) {
    visited[vertex] = true;
    for (Node* node = adjacency[vertex]; node; node = node->next) {
        if (!visited[node->vertex]) kosaraju_finish(adjacency, node->vertex, visited, finish_order, count);
    }
    finish_order[(*count)++] = vertex;
}

static void kosaraju_collect(Node** transposed, int vertex, bool* visited, IntSlice* component) {
    int* stack = NULL;
    int size = 0;
    int capacity = 0;
    visited[vertex] = true;
    capacity = 1;
    stack = malloc(capacity * sizeof(int));
    stack[size++] = vertex;
    while (size > 0) {
        int current = stack[--size];
        slice_append(component, current);
        for (Node* node = transposed[current]; node; node = node->next) {
            if (!visited[node->vertex]) {
                visited[node->vertex] = true;
                if (size == capacity) {
                    capacity *= 2;
                    stack = realloc(stack, capacity * sizeof(int));
                }
                stack[size++] = node->vertex;
            }
        }
    }
    free(stack);
}

int topological_scc_kosaraju(Node** adjacency, int vertex_count, SliceList* components) {
    bool* visited = calloc(vertex_count, sizeof(bool));
    int* finish_order = malloc(vertex_count * sizeof(int));
    int count = 0;
    for (int vertex = 0; vertex < vertex_count; vertex++) {
        if (!visited[vertex]) kosaraju_finish(adjacency, vertex, visited, finish_order, &count);
    }
    Node** transposed = calloc(vertex_count, sizeof(Node*));
    for (int vertex = 0; vertex < vertex_count; vertex++) {
        for (Node* node = adjacency[vertex]; node; node = node->next) {
            Node* reverse = malloc(sizeof(Node));
            reverse->vertex = vertex;
            reverse->next = transposed[node->vertex];
            transposed[node->vertex] = reverse;
        }
    }
    for (int vertex = 0; vertex < vertex_count; vertex++) visited[vertex] = false;
    components->size = 0;
    components->values = NULL;
    for (int index = vertex_count - 1; index >= 0; index--) {
        int vertex = finish_order[index];
        if (!visited[vertex]) {
            IntSlice component = {0, 0, NULL};
            kosaraju_collect(transposed, vertex, visited, &component);
            list_append(components, component);
        }
    }
    for (int vertex = 0; vertex < vertex_count; vertex++) {
        Node* node = transposed[vertex];
        while (node) {
            Node* next = node->next;
            free(node);
            node = next;
        }
    }
    free(transposed);
    free(visited);
    free(finish_order);
    return 1;
}
```

```python
class TopologicalSCC:
    @staticmethod
    def topological_sort(adjacency: list[list[int]]) -> list[int]:
        vertex_count = len(adjacency)
        in_degree = [0] * vertex_count
        for neighbors in adjacency:
            for neighbor in neighbors:
                in_degree[neighbor] += 1
        queue = [vertex for vertex in range(vertex_count) if in_degree[vertex] == 0]
        order: list[int] = []
        while queue:
            vertex = queue.pop(0)
            order.append(vertex)
            for neighbor in adjacency[vertex]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        return order if len(order) == vertex_count else []

    @staticmethod
    def tarjan(adjacency: list[list[int]]) -> list[list[int]]:
        vertex_count = len(adjacency)
        discovery = [-1] * vertex_count
        low = [0] * vertex_count
        on_stack = [False] * vertex_count
        stack: list[int] = []
        components: list[list[int]] = []
        next_index = 0

        def strong_connect(vertex: int) -> None:
            nonlocal next_index
            discovery[vertex] = low[vertex] = next_index
            next_index += 1
            stack.append(vertex)
            on_stack[vertex] = True
            for neighbor in adjacency[vertex]:
                if discovery[neighbor] == -1:
                    strong_connect(neighbor)
                    low[vertex] = min(low[vertex], low[neighbor])
                elif on_stack[neighbor]:
                    low[vertex] = min(low[vertex], discovery[neighbor])
            if low[vertex] == discovery[vertex]:
                component: list[int] = []
                while True:
                    current = stack.pop()
                    on_stack[current] = False
                    component.append(current)
                    if current == vertex:
                        break
                components.append(component)

        for vertex in range(vertex_count):
            if discovery[vertex] == -1:
                strong_connect(vertex)
        return components

    @staticmethod
    def kosaraju(adjacency: list[list[int]]) -> list[list[int]]:
        vertex_count = len(adjacency)
        visited = [False] * vertex_count
        finish_order: list[int] = []

        def finish(vertex: int) -> None:
            visited[vertex] = True
            for neighbor in adjacency[vertex]:
                if not visited[neighbor]:
                    finish(neighbor)
            finish_order.append(vertex)

        for vertex in range(vertex_count):
            if not visited[vertex]:
                finish(vertex)
        transposed = [[] for _ in range(vertex_count)]
        for vertex in range(vertex_count):
            for neighbor in adjacency[vertex]:
                transposed[neighbor].append(vertex)
        for vertex in range(vertex_count):
            visited[vertex] = False
        components: list[list[int]] = []
        for vertex in reversed(finish_order):
            if not visited[vertex]:
                visited[vertex] = True
                component = [vertex]
                stack = [vertex]
                while stack:
                    current = stack.pop()
                    for neighbor in transposed[current]:
                        if not visited[neighbor]:
                            visited[neighbor] = True
                            component.append(neighbor)
                            stack.append(neighbor)
                components.append(component)
        return components
```

```rust
pub struct TopologicalSCC;

impl TopologicalSCC {
    pub fn topological_sort(adjacency: &[Vec<usize>]) -> Vec<usize> {
        let vertex_count = adjacency.len();
        let mut in_degree = vec![0usize; vertex_count];
        for neighbors in adjacency {
            for &neighbor in neighbors {
                in_degree[neighbor] += 1;
            }
        }
        let mut queue: std::collections::VecDeque<usize> =
            (0..vertex_count).filter(|&vertex| in_degree[vertex] == 0).collect();
        let mut order = Vec::new();
        while let Some(vertex) = queue.pop_front() {
            order.push(vertex);
            for &neighbor in &adjacency[vertex] {
                in_degree[neighbor] -= 1;
                if in_degree[neighbor] == 0 {
                    queue.push_back(neighbor);
                }
            }
        }
        if order.len() == vertex_count { order } else { Vec::new() }
    }

    pub fn tarjan(adjacency: &[Vec<usize>]) -> Vec<Vec<usize>> {
        let vertex_count = adjacency.len();
        let mut discovery = vec![-1i64; vertex_count];
        let mut low = vec![0i64; vertex_count];
        let mut on_stack = vec![false; vertex_count];
        let mut stack = Vec::new();
        let mut components = Vec::new();
        let mut next_index = 0i64;
        for vertex in 0..vertex_count {
            if discovery[vertex] == -1 {
                Self::strong_connect(vertex, adjacency, &mut discovery, &mut low, &mut on_stack, &mut stack, &mut components, &mut next_index);
            }
        }
        components
    }

    fn strong_connect(
        vertex: usize,
        adjacency: &[Vec<usize>],
        discovery: &mut [i64],
        low: &mut [i64],
        on_stack: &mut [bool],
        stack: &mut Vec<usize>,
        components: &mut Vec<Vec<usize>>,
        next_index: &mut i64,
    ) {
        discovery[vertex] = *next_index;
        low[vertex] = *next_index;
        *next_index += 1;
        stack.push(vertex);
        on_stack[vertex] = true;
        for &neighbor in &adjacency[vertex] {
            if discovery[neighbor] == -1 {
                Self::strong_connect(neighbor, adjacency, discovery, low, on_stack, stack, components, next_index);
                low[vertex] = low[vertex].min(low[neighbor]);
            } else if on_stack[neighbor] {
                low[vertex] = low[vertex].min(discovery[neighbor]);
            }
        }
        if low[vertex] == discovery[vertex] {
            let mut component = Vec::new();
            loop {
                let current = stack.pop().unwrap();
                on_stack[current] = false;
                component.push(current);
                if current == vertex {
                    break;
                }
            }
            components.push(component);
        }
    }

    pub fn kosaraju(adjacency: &[Vec<usize>]) -> Vec<Vec<usize>> {
        let vertex_count = adjacency.len();
        let mut visited = vec![false; vertex_count];
        let mut finish_order = Vec::new();
        for vertex in 0..vertex_count {
            if !visited[vertex] {
                Self::finish(vertex, adjacency, &mut visited, &mut finish_order);
            }
        }
        let mut transposed = vec![Vec::new(); vertex_count];
        for (vertex, neighbors) in adjacency.iter().enumerate() {
            for &neighbor in neighbors {
                transposed[neighbor].push(vertex);
            }
        }
        visited.fill(false);
        let mut components = Vec::new();
        for &vertex in finish_order.iter().rev() {
            if visited[vertex] {
                continue;
            }
            let mut component = Vec::new();
            let mut stack = vec![vertex];
            visited[vertex] = true;
            while let Some(current) = stack.pop() {
                component.push(current);
                for &neighbor in &transposed[current] {
                    if !visited[neighbor] {
                        visited[neighbor] = true;
                        stack.push(neighbor);
                    }
                }
            }
            components.push(component);
        }
        components
    }

    fn finish(vertex: usize, adjacency: &[Vec<usize>], visited: &mut [bool], order: &mut Vec<usize>) {
        visited[vertex] = true;
        for &neighbor in &adjacency[vertex] {
            if !visited[neighbor] {
                Self::finish(neighbor, adjacency, visited, order);
            }
        }
        order.push(vertex);
    }
}
```

```typescript
export class TopologicalSCC {
  static topologicalSort(adjacency: number[][]): number[] {
    const vertexCount = adjacency.length;
    const inDegree = new Array<number>(vertexCount).fill(0);
    for (const neighbors of adjacency) {
      for (const neighbor of neighbors) inDegree[neighbor]++;
    }
    const queue: number[] = [];
    for (let vertex = 0; vertex < vertexCount; vertex++) {
      if (inDegree[vertex] === 0) queue.push(vertex);
    }
    const order: number[] = [];
    while (queue.length > 0) {
      const vertex = queue.shift()!;
      order.push(vertex);
      for (const neighbor of adjacency[vertex]) {
        if (--inDegree[neighbor] === 0) queue.push(neighbor);
      }
    }
    return order.length === vertexCount ? order : [];
  }

  static tarjan(adjacency: number[][]): number[][] {
    const discovery = new Array<number>(adjacency.length).fill(-1);
    const low = new Array<number>(adjacency.length).fill(0);
    const onStack = new Array<boolean>(adjacency.length).fill(false);
    const stack: number[] = [];
    const components: number[][] = [];
    let nextIndex = 0;
    const strongConnect = (vertex: number): void => {
      discovery[vertex] = low[vertex] = nextIndex++;
      stack.push(vertex);
      onStack[vertex] = true;
      for (const neighbor of adjacency[vertex]) {
        if (discovery[neighbor] === -1) {
          strongConnect(neighbor);
          low[vertex] = Math.min(low[vertex], low[neighbor]);
        } else if (onStack[neighbor]) {
          low[vertex] = Math.min(low[vertex], discovery[neighbor]);
        }
      }
      if (low[vertex] === discovery[vertex]) {
        const component: number[] = [];
        while (true) {
          const current = stack.pop()!;
          onStack[current] = false;
          component.push(current);
          if (current === vertex) break;
        }
        components.push(component);
      }
    };
    for (let vertex = 0; vertex < adjacency.length; vertex++) {
      if (discovery[vertex] === -1) strongConnect(vertex);
    }
    return components;
  }

  static kosaraju(adjacency: number[][]): number[][] {
    const visited = new Array<boolean>(adjacency.length).fill(false);
    const finishOrder: number[] = [];
    const finish = (vertex: number): void => {
      visited[vertex] = true;
      for (const neighbor of adjacency[vertex]) {
        if (!visited[neighbor]) finish(neighbor);
      }
      finishOrder.push(vertex);
    };
    for (let vertex = 0; vertex < adjacency.length; vertex++) {
      if (!visited[vertex]) finish(vertex);
    }
    const transposed: number[][] = Array.from({ length: adjacency.length }, () => []);
    for (let vertex = 0; vertex < adjacency.length; vertex++) {
      for (const neighbor of adjacency[vertex]) transposed[neighbor].push(vertex);
    }
    visited.fill(false);
    const components: number[][] = [];
    for (let index = finishOrder.length - 1; index >= 0; index--) {
      const start = finishOrder[index];
      if (visited[start]) continue;
      const component: number[] = [];
      const stack = [start];
      visited[start] = true;
      while (stack.length > 0) {
        const vertex = stack.pop()!;
        component.push(vertex);
        for (const neighbor of transposed[vertex]) {
          if (!visited[neighbor]) {
            visited[neighbor] = true;
            stack.push(neighbor);
          }
        }
      }
      components.push(component);
    }
    return components;
  }
}
```

```go
package graph

type TopologicalSCC struct{}

func (TopologicalSCC) TopologicalSort(adjacency [][]int) []int {
	vertexCount := len(adjacency)
	inDegree := make([]int, vertexCount)
	for _, neighbors := range adjacency {
		for _, neighbor := range neighbors {
			inDegree[neighbor]++
		}
	}
	queue := []int{}
	for vertex := 0; vertex < vertexCount; vertex++ {
		if inDegree[vertex] == 0 {
			queue = append(queue, vertex)
		}
	}
	order := []int{}
	for len(queue) > 0 {
		vertex := queue[0]
		queue = queue[1:]
		order = append(order, vertex)
		for _, neighbor := range adjacency[vertex] {
			inDegree[neighbor]--
			if inDegree[neighbor] == 0 {
				queue = append(queue, neighbor)
			}
		}
	}
	if len(order) != vertexCount {
		return nil
	}
	return order
}

func (TopologicalSCC) Tarjan(adjacency [][]int) [][]int {
	discovery := make([]int, len(adjacency))
	for vertex := range discovery {
		discovery[vertex] = -1
	}
	low := make([]int, len(adjacency))
	onStack := make([]bool, len(adjacency))
	stack := []int{}
	components := [][]int{}
	nextIndex := 0
	var strongConnect func(int)
	strongConnect = func(vertex int) {
		discovery[vertex] = nextIndex
		low[vertex] = nextIndex
		nextIndex++
		stack = append(stack, vertex)
		onStack[vertex] = true
		for _, neighbor := range adjacency[vertex] {
			if discovery[neighbor] == -1 {
				strongConnect(neighbor)
				if low[neighbor] < low[vertex] {
					low[vertex] = low[neighbor]
				}
			} else if onStack[neighbor] && discovery[neighbor] < low[vertex] {
				low[vertex] = discovery[neighbor]
			}
		}
		if low[vertex] == discovery[vertex] {
			component := []int{}
			for {
				current := stack[len(stack)-1]
				stack = stack[:len(stack)-1]
				onStack[current] = false
				component = append(component, current)
				if current == vertex {
					break
				}
			}
			components = append(components, component)
		}
	}
	for vertex := range adjacency {
		if discovery[vertex] == -1 {
			strongConnect(vertex)
		}
	}
	return components
}

func (TopologicalSCC) Kosaraju(adjacency [][]int) [][]int {
    visited := make([]bool, len(adjacency))
    finishOrder := []int{}
    var finish func(int)
    finish = func(vertex int) {
        visited[vertex] = true
        for _, neighbor := range adjacency[vertex] {
            if !visited[neighbor] {
                finish(neighbor)
            }
        }
        finishOrder = append(finishOrder, vertex)
    }
    for vertex := range adjacency {
        if !visited[vertex] {
            finish(vertex)
        }
    }
    transposed := make([][]int, len(adjacency))
    for vertex, neighbors := range adjacency {
        for _, neighbor := range neighbors {
            transposed[neighbor] = append(transposed[neighbor], vertex)
        }
    }
    for vertex := range visited {
        visited[vertex] = false
    }
    components := [][]int{}
    for index := len(finishOrder) - 1; index >= 0; index-- {
        start := finishOrder[index]
        if visited[start] {
            continue
        }
        component := []int{}
        stack := []int{start}
        visited[start] = true
        for len(stack) > 0 {
            vertex := stack[len(stack)-1]
            stack = stack[:len(stack)-1]
            component = append(component, vertex)
            for _, neighbor := range transposed[vertex] {
                if !visited[neighbor] {
                    visited[neighbor] = true
                    stack = append(stack, neighbor)
                }
            }
        }
        components = append(components, component)
    }
    return components
}
```

## Complexity
For \(V\) vertices and \(E\) edges:

| Algorithm | Time | Extra space |
| --- | --- | --- |
| Kahn's topological sort | O(V+E) | O(V) |
| Tarjan's SCC | O(V+E) | O(V) |
| Kosaraju's SCC | O(V+E) | O(V+E) |

Tarjan discovers each component without storing the transposed graph. Kosaraju explicitly constructs the transpose in the C example, so that representation adds O(V+E) space.

## When to use
- You need a valid build, package, course, or job dependency order.
- You need to detect a directed cycle in a dependency graph.
- You need to condense SCCs into a DAG for another algorithm.
- You need to reason about mutual reachability or apply the 2-SAT implication graph.

## Alternatives
- **DFS postorder topological sort** — uses one DFS and a finishing stack, but an empty result requires separate cycle reasoning.
- **Kahn's algorithm** — exposes partial orders and easy in-degree updates, but repeated priority ordering can add a heap factor.
- **Gabow's SCC algorithm** — finds SCCs without Tarjan's low-link propagation, but is harder to implement and less commonly exposed by libraries.

## Related
- [Graph Representations (Adjacency Matrix, Adjacency List, Edge List)](01-graph-representations.md)
- [Graph Traversals: Breadth-First Search (BFS) and Depth-First Search (DFS)](02-graph-traversals.md)
- [Shortest Path Algorithms: Single-Source (Dijkstra’s, Bellman-Ford) & All-Pairs (Floyd-Warshall, Johnson’s)](05-shortest-paths.md)
- [Memory Works (Templates)](../../00-essentials/06-memory-works-templates.md)
