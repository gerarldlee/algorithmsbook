---
title: "Network Flow & Matching (Ford-Fulkerson, Edmonds-Karp, Dinic’s, Hopcroft-Karp)"
weight: 6
toc: true
---

## What it is
**Network flow** maximizes the amount sent through a directed, capacity-constrained graph from a source to a sink, while **bipartite matching** finds vertex-disjoint left-to-right pairs; Ford-Fulkerson, Edmonds-Karp, Dinic's, and Hopcroft-Karp are the corresponding classic algorithms.

## How it works
A residual graph records unused forward capacity and cancellation capacity in opposite directions. Ford-Fulkerson repeatedly follows any source-to-sink residual path, Edmonds-Karp chooses a shortest such path with BFS, and Dinic's builds a **level graph** and sends a blocking flow before rebuilding levels. Hopcroft-Karp applies layered shortest augmenting paths to a bipartite graph and returns the left-to-right matching.

```java
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Deque;
import java.util.List;

public final class NetworkFlow {
    private static long[][] residualCopy(long[][] capacity) {
        long[][] residual = new long[capacity.length][];
        for (int vertex = 0; vertex < capacity.length; vertex++) residual[vertex] = capacity[vertex].clone();
        return residual;
    }

    private static long fordSend(long[][] residual, boolean[] visited, int vertex, int sink, long limit) {
        if (vertex == sink) return limit;
        visited[vertex] = true;
        for (int neighbor = 0; neighbor < residual.length; neighbor++) {
            if (visited[neighbor] || residual[vertex][neighbor] <= 0) continue;
            long sent = fordSend(residual, visited, neighbor, sink, Math.min(limit, residual[vertex][neighbor]));
            if (sent > 0) {
                residual[vertex][neighbor] -= sent;
                residual[neighbor][vertex] += sent;
                return sent;
            }
        }
        return 0;
    }

    public static long fordFulkerson(long[][] capacity, int source, int sink) {
        long[][] residual = residualCopy(capacity);
        long total = 0;
        while (true) {
            long sent = fordSend(residual, new boolean[capacity.length], source, sink, Long.MAX_VALUE / 4);
            if (sent == 0) return total;
            total += sent;
        }
    }

    public static long edmondsKarp(long[][] capacity, int source, int sink) {
        int vertexCount = capacity.length;
        long[][] residual = residualCopy(capacity);
        long total = 0;
        while (true) {
            int[] parent = new int[vertexCount];
            Arrays.fill(parent, -1);
            Deque<Integer> queue = new ArrayDeque<>();
            parent[source] = source;
            queue.add(source);
            while (!queue.isEmpty() && parent[sink] == -1) {
                int vertex = queue.removeFirst();
                for (int neighbor = 0; neighbor < vertexCount; neighbor++) {
                    if (parent[neighbor] == -1 && residual[vertex][neighbor] > 0) {
                        parent[neighbor] = vertex;
                        queue.add(neighbor);
                    }
                }
            }
            if (parent[sink] == -1) return total;
            long pathFlow = Long.MAX_VALUE;
            for (int vertex = sink; vertex != source; vertex = parent[vertex]) {
                pathFlow = Math.min(pathFlow, residual[parent[vertex]][vertex]);
            }
            for (int vertex = sink; vertex != source; vertex = parent[vertex]) {
                residual[parent[vertex]][vertex] -= pathFlow;
                residual[vertex][parent[vertex]] += pathFlow;
            }
            total += pathFlow;
        }
    }

    public static long dinic(long[][] capacity, int source, int sink) {
        int vertexCount = capacity.length;
        long[][] residual = residualCopy(capacity);
        long total = 0;
        while (true) {
            int[] level = new int[vertexCount];
            Arrays.fill(level, -1);
            Deque<Integer> queue = new ArrayDeque<>();
            level[source] = 0;
            queue.add(source);
            while (!queue.isEmpty()) {
                int vertex = queue.removeFirst();
                for (int neighbor = 0; neighbor < vertexCount; neighbor++) {
                    if (residual[vertex][neighbor] > 0 && level[neighbor] == -1) {
                        level[neighbor] = level[vertex] + 1;
                        queue.add(neighbor);
                    }
                }
            }
            if (level[sink] == -1) return total;
            int[] nextEdge = new int[vertexCount];
            while (true) {
                long sent = dinicSend(residual, nextEdge, level, source, sink, Long.MAX_VALUE / 4);
                if (sent == 0) break;
                total += sent;
            }
        }
    }

    private static long dinicSend(long[][] residual, int[] nextEdge, int[] level, int vertex, int sink, long limit) {
        if (vertex == sink) return limit;
        while (nextEdge[vertex] < residual.length) {
            int neighbor = (int) nextEdge[vertex];
            if (residual[vertex][neighbor] > 0 && level[neighbor] == level[vertex] + 1) {
                long sent = dinicSend(residual, nextEdge, level, neighbor, sink, Math.min(limit, residual[vertex][neighbor]));
                if (sent > 0) {
                    residual[vertex][neighbor] -= sent;
                    residual[neighbor][vertex] += sent;
                    return sent;
                }
            }
            nextEdge[vertex]++;
        }
        return 0;
    }

    public static int[] hopcroftKarp(List<List<Integer>> adjacency, int rightCount) {
        int leftCount = adjacency.size();
        int[] leftMatch = new int[leftCount];
        int[] rightMatch = new int[rightCount];
        Arrays.fill(leftMatch, -1);
        Arrays.fill(rightMatch, -1);
        int[] distance = new int[leftCount];
        int shortest;
        while ((shortest = hopcroftLayers(adjacency, leftMatch, rightMatch, distance)) != -1) {
            for (int left = 0; left < leftCount; left++) {
                if (leftMatch[left] == -1) hopcroftAugment(adjacency, left, shortest, distance, leftMatch, rightMatch);
            }
        }
        return leftMatch;
    }

    private static int hopcroftLayers(List<List<Integer>> adjacency, int[] leftMatch, int[] rightMatch, int[] distance) {
        Deque<Integer> queue = new ArrayDeque<>();
        Arrays.fill(distance, -1);
        for (int left = 0; left < adjacency.size(); left++) {
            if (leftMatch[left] == -1) {
                distance[left] = 0;
                queue.add(left);
            }
        }
        int shortest = Integer.MAX_VALUE;
        while (!queue.isEmpty()) {
            int left = queue.removeFirst();
            if (distance[left] >= shortest) continue;
            for (int right : adjacency.get(left)) {
                int matched = rightMatch[right];
                if (matched == -1) {
                    shortest = distance[left] + 1;
                } else if (distance[matched] == -1) {
                    distance[matched] = distance[left] + 1;
                    queue.add(matched);
                }
            }
        }
        if (shortest == Integer.MAX_VALUE) return -1;
        for (int left = 0; left < distance.length; left++) {
            if (distance[left] > shortest) distance[left] = -1;
        }
        return shortest;
    }

    private static boolean hopcroftAugment(List<List<Integer>> adjacency, int left, int shortest, int[] distance, int[] leftMatch, int[] rightMatch) {
        for (int right : adjacency.get(left)) {
            int matched = rightMatch[right];
            if (matched == -1) {
                if (distance[left] + 1 != shortest) continue;
            } else if (distance[matched] != distance[left] + 1 || !hopcroftAugment(adjacency, matched, shortest, distance, leftMatch, rightMatch)) {
                continue;
            }
            leftMatch[left] = right;
            rightMatch[right] = left;
            return true;
        }
        distance[left] = -1;
        return false;
    }
}
```

```c
#include <limits.h>
#include <stdbool.h>
#include <stdlib.h>

typedef long long Flow;

typedef struct Node {
    int vertex;
    struct Node* next;
} Node;

static Flow** network_flow_copy(Flow** capacity, int vertex_count) {
    Flow** residual = malloc(vertex_count * sizeof(Flow*));
    for (int vertex = 0; vertex < vertex_count; vertex++) {
        residual[vertex] = malloc(vertex_count * sizeof(Flow));
        for (int neighbor = 0; neighbor < vertex_count; neighbor++) residual[vertex][neighbor] = capacity[vertex][neighbor];
    }
    return residual;
}

static void network_flow_destroy(Flow** matrix, int vertex_count) {
    for (int vertex = 0; vertex < vertex_count; vertex++) free(matrix[vertex]);
    free(matrix);
}

static Flow network_flow_ford_send(Flow** residual, int vertex_count, bool* visited, int vertex, int sink, Flow limit) {
    if (vertex == sink) return limit;
    visited[vertex] = true;
    for (int neighbor = 0; neighbor < vertex_count; neighbor++) {
        if (visited[neighbor] || residual[vertex][neighbor] <= 0) continue;
        Flow remaining = residual[vertex][neighbor] < limit ? residual[vertex][neighbor] : limit;
        Flow sent = network_flow_ford_send(residual, vertex_count, visited, neighbor, sink, remaining);
        if (sent > 0) {
            residual[vertex][neighbor] -= sent;
            residual[neighbor][vertex] += sent;
            return sent;
        }
    }
    return 0;
}

Flow network_flow_ford_fulkerson(Flow** capacity, int vertex_count, int source, int sink) {
    Flow** residual = network_flow_copy(capacity, vertex_count);
    Flow total = 0;
    while (1) {
        bool* visited = calloc(vertex_count, sizeof(bool));
        Flow sent = network_flow_ford_send(residual, vertex_count, visited, source, sink, LLONG_MAX / 4);
        free(visited);
        if (sent == 0) break;
        total += sent;
    }
    network_flow_destroy(residual, vertex_count);
    return total;
}

Flow network_flow_edmonds_karp(Flow** capacity, int vertex_count, int source, int sink) {
    Flow** residual = network_flow_copy(capacity, vertex_count);
    int* parent = malloc(vertex_count * sizeof(int));
    int* queue = malloc(vertex_count * sizeof(int));
    Flow total = 0;
    while (1) {
        for (int vertex = 0; vertex < vertex_count; vertex++) parent[vertex] = -1;
        int head = 0;
        int tail = 0;
        parent[source] = source;
        queue[tail++] = source;
        while (head < tail && parent[sink] == -1) {
            int vertex = queue[head++];
            for (int neighbor = 0; neighbor < vertex_count; neighbor++) {
                if (parent[neighbor] == -1 && residual[vertex][neighbor] > 0) {
                    parent[neighbor] = vertex;
                    queue[tail++] = neighbor;
                }
            }
        }
        if (parent[sink] == -1) break;
        Flow path_flow = LLONG_MAX;
        for (int vertex = sink; vertex != source; vertex = parent[vertex]) {
            Flow capacity_value = residual[parent[vertex]][vertex];
            if (capacity_value < path_flow) path_flow = capacity_value;
        }
        for (int vertex = sink; vertex != source; vertex = parent[vertex]) {
            residual[parent[vertex]][vertex] -= path_flow;
            residual[vertex][parent[vertex]] += path_flow;
        }
        total += path_flow;
    }
    free(parent);
    free(queue);
    network_flow_destroy(residual, vertex_count);
    return total;
}

static bool network_flow_levels(Flow** residual, int vertex_count, int source, int sink, int* level, int* queue) {
    for (int vertex = 0; vertex < vertex_count; vertex++) level[vertex] = -1;
    int head = 0;
    int tail = 0;
    level[source] = 0;
    queue[tail++] = source;
    while (head < tail) {
        int vertex = queue[head++];
        for (int neighbor = 0; neighbor < vertex_count; neighbor++) {
            if (residual[vertex][neighbor] > 0 && level[neighbor] == -1) {
                level[neighbor] = level[vertex] + 1;
                queue[tail++] = neighbor;
            }
        }
    }
    return level[sink] != -1;
}

static Flow network_flow_dinic_send(Flow** residual, int vertex_count, long long* next_edge, int* level, int vertex, int sink, Flow limit) {
    if (vertex == sink) return limit;
    while (next_edge[vertex] < vertex_count) {
        int neighbor = (int)next_edge[vertex];
        if (residual[vertex][neighbor] > 0 && level[neighbor] == level[vertex] + 1) {
            Flow remaining = residual[vertex][neighbor] < limit ? residual[vertex][neighbor] : limit;
            Flow sent = network_flow_dinic_send(residual, vertex_count, next_edge, level, neighbor, sink, remaining);
            if (sent > 0) {
                residual[vertex][neighbor] -= sent;
                residual[neighbor][vertex] += sent;
                return sent;
            }
        }
        next_edge[vertex]++;
    }
    return 0;
}

Flow network_flow_dinic(Flow** capacity, int vertex_count, int source, int sink) {
    Flow** residual = network_flow_copy(capacity, vertex_count);
    int* level = malloc(vertex_count * sizeof(int));
    int* queue = malloc(vertex_count * sizeof(int));
    long long* next_edge = calloc(vertex_count, sizeof(long long));
    Flow total = 0;
    while (network_flow_levels(residual, vertex_count, source, sink, level, queue)) {
        for (int vertex = 0; vertex < vertex_count; vertex++) next_edge[vertex] = 0;
        while (1) {
            Flow sent = network_flow_dinic_send(residual, vertex_count, next_edge, level, source, sink, LLONG_MAX / 4);
            if (sent == 0) break;
            total += sent;
        }
    }
    free(level);
    free(queue);
    free(next_edge);
    network_flow_destroy(residual, vertex_count);
    return total;
}

typedef struct {
    Node** adjacency;
    int left_count;
    int right_count;
    int* left_match;
    int* right_match;
    int* distance;
} HopcroftState;

static bool network_flow_hopcroft_layers(HopcroftState* state) {
    int* queue = malloc(state->left_count * sizeof(int));
    int head = 0;
    int tail = 0;
    for (int left = 0; left < state->left_count; left++) {
        if (state->left_match[left] == -1) {
            state->distance[left] = 0;
            queue[tail++] = left;
        } else {
            state->distance[left] = -1;
        }
    }
    int nil = state->left_count;
    state->distance[nil] = -1;
    bool found = false;
    while (head < tail) {
        int left = queue[head++];
        if (state->distance[nil] != -1 && state->distance[left] >= state->distance[nil]) continue;
        for (Node* node = state->adjacency[left]; node; node = node->next) {
            int matched = state->right_match[node->vertex];
            if (matched == -1) {
                state->distance[nil] = state->distance[left] + 1;
                found = true;
            } else if (state->distance[matched] == -1) {
                state->distance[matched] = state->distance[left] + 1;
                queue[tail++] = matched;
            }
        }
    }
    free(queue);
    return found;
}

static bool network_flow_hopcroft_augment(HopcroftState* state, int left) {
    int nil = state->left_count;
    for (Node* node = state->adjacency[left]; node; node = node->next) {
        int right = node->vertex;
        int matched = state->right_match[right];
        if (matched == -1) {
            if (state->distance[left] + 1 != state->distance[nil]) continue;
        } else if (state->distance[matched] != state->distance[left] + 1 || !network_flow_hopcroft_augment(state, matched)) {
            continue;
        }
        state->left_match[left] = right;
        state->right_match[right] = left;
        return true;
    }
    state->distance[left] = -1;
    return false;
}

int network_flow_hopcroft_karp(Node** adjacency, int left_count, int right_count, int* left_match) {
    HopcroftState state;
    state.adjacency = adjacency;
    state.left_count = left_count;
    state.right_count = right_count;
    state.left_match = left_match;
    state.right_match = malloc(right_count * sizeof(int));
    state.distance = malloc((left_count + 1) * sizeof(int));
    for (int left = 0; left < left_count; left++) state.left_match[left] = -1;
    for (int right = 0; right < right_count; right++) state.right_match[right] = -1;
    while (network_flow_hopcroft_layers(&state)) {
        for (int left = 0; left < left_count; left++) {
            if (state.left_match[left] == -1) network_flow_hopcroft_augment(&state, left);
        }
    }
    int matching = 0;
    for (int left = 0; left < left_count; left++) matching += state.left_match[left] != -1;
    free(state.right_match);
    free(state.distance);
    return matching;
}
```

```python
from collections import deque


class NetworkFlow:
    @staticmethod
    def ford_fulkerson(capacity: list[list[int]], source: int, sink: int) -> int:
        residual = [row.copy() for row in capacity]

        def send(vertex: int, limit: int, visited: list[bool]) -> int:
            if vertex == sink:
                return limit
            visited[vertex] = True
            for neighbor in range(len(residual)):
                if visited[neighbor] or residual[vertex][neighbor] <= 0:
                    continue
                sent = send(neighbor, min(limit, residual[vertex][neighbor]), visited)
                if sent > 0:
                    residual[vertex][neighbor] -= sent
                    residual[neighbor][vertex] += sent
                    return sent
            return 0

        total = 0
        while sent := send(source, float("inf"), [False] * len(residual)):
            total += sent
        return total

    @staticmethod
    def edmonds_karp(capacity: list[list[int]], source: int, sink: int) -> int:
        residual = [row.copy() for row in capacity]
        total = 0
        while True:
            parent = [-1] * len(residual)
            parent[source] = source
            queue = deque([source])
            while queue and parent[sink] == -1:
                vertex = queue.popleft()
                for neighbor in range(len(residual)):
                    if parent[neighbor] == -1 and residual[vertex][neighbor] > 0:
                        parent[neighbor] = vertex
                        queue.append(neighbor)
            if parent[sink] == -1:
                return total
            path_flow = float("inf")
            vertex = sink
            while vertex != source:
                path_flow = min(path_flow, residual[parent[vertex]][vertex])
                vertex = parent[vertex]
            vertex = sink
            while vertex != source:
                residual[parent[vertex]][vertex] -= path_flow
                residual[vertex][parent[vertex]] += path_flow
                vertex = parent[vertex]
            total += path_flow

    @staticmethod
    def dinic(capacity: list[list[int]], source: int, sink: int) -> int:
        residual = [row.copy() for row in capacity]
        total = 0
        while True:
            level = [-1] * len(residual)
            level[source] = 0
            queue = deque([source])
            while queue:
                vertex = queue.popleft()
                for neighbor in range(len(residual)):
                    if residual[vertex][neighbor] > 0 and level[neighbor] == -1:
                        level[neighbor] = level[vertex] + 1
                        queue.append(neighbor)
            if level[sink] == -1:
                return total
            next_edge = [0] * len(residual)

            def send(vertex: int, limit: int) -> int:
                if vertex == sink:
                    return limit
                while next_edge[vertex] < len(residual):
                    neighbor = next_edge[vertex]
                    if residual[vertex][neighbor] > 0 and level[neighbor] == level[vertex] + 1:
                        sent = send(neighbor, min(limit, residual[vertex][neighbor]))
                        if sent > 0:
                            residual[vertex][neighbor] -= sent
                            residual[neighbor][vertex] += sent
                            return sent
                    next_edge[vertex] += 1
                return 0

            while sent := send(source, float("inf")):
                total += sent

    @staticmethod
    def hopcroft_karp(adjacency: list[list[int]], right_count: int) -> list[int]:
        left_count = len(adjacency)
        left_match = [-1] * left_count
        right_match = [-1] * right_count
        while True:
            distance = [-1] * left_count
            queue = deque(left for left in range(left_count) if left_match[left] == -1)
            for left in queue:
                distance[left] = 0
            shortest = float("inf")
            while queue:
                left = queue.popleft()
                if distance[left] >= shortest:
                    continue
                for right in adjacency[left]:
                    matched = right_match[right]
                    if matched == -1:
                        shortest = distance[left] + 1
                    elif distance[matched] == -1:
                        distance[matched] = distance[left] + 1
                        queue.append(matched)

            def augment(left: int) -> bool:
                for right in adjacency[left]:
                    matched = right_match[right]
                    if matched == -1:
                        if distance[left] + 1 != shortest:
                            continue
                    elif distance[matched] != distance[left] + 1 or not augment(matched):
                        continue
                    left_match[left] = right
                    right_match[right] = left
                    return True
                distance[left] = -1
                return False

            if shortest == float("inf"):
                return left_match
            for left in range(left_count):
                if left_match[left] == -1:
                    augment(left)
```

```rust
use std::collections::VecDeque;

pub struct NetworkFlow;

impl NetworkFlow {
    fn residual_copy(capacity: &[Vec<i64>]) -> Vec<Vec<i64>> {
        capacity.to_vec()
    }

    fn ford_send(residual: &mut [Vec<i64>], visited: &mut [bool], vertex: usize, sink: usize, limit: i64) -> i64 {
        if vertex == sink {
            return limit;
        }
        visited[vertex] = true;
        for neighbor in 0..residual.len() {
            if visited[neighbor] || residual[vertex][neighbor] <= 0 {
                continue;
            }
            let sent = Self::ford_send(residual, visited, neighbor, sink, limit.min(residual[vertex][neighbor]));
            if sent > 0 {
                residual[vertex][neighbor] -= sent;
                residual[neighbor][vertex] += sent;
                return sent;
            }
        }
        0
    }

    pub fn ford_fulkerson(capacity: &[Vec<i64>], source: usize, sink: usize) -> i64 {
        let mut residual = Self::residual_copy(capacity);
        let mut total = 0;
        loop {
            let mut visited = vec![false; residual.len()];
            let sent = Self::ford_send(&mut residual, &mut visited, source, sink, i64::MAX / 4);
            if sent == 0 {
                return total;
            }
            total += sent;
        }
    }

    pub fn edmonds_karp(capacity: &[Vec<i64>], source: usize, sink: usize) -> i64 {
        let vertex_count = capacity.len();
        let mut residual = Self::residual_copy(capacity);
        let mut total = 0;
        loop {
            let mut parent = vec![usize::MAX; vertex_count];
            let mut queue = VecDeque::new();
            parent[source] = source;
            queue.push_back(source);
            while let Some(vertex) = queue.pop_front() {
                if parent[sink] != usize::MAX {
                    break;
                }
                for neighbor in 0..vertex_count {
                    if parent[neighbor] == usize::MAX && residual[vertex][neighbor] > 0 {
                        parent[neighbor] = vertex;
                        queue.push_back(neighbor);
                    }
                }
            }
            if parent[sink] == usize::MAX {
                return total;
            }
            let mut path_flow = i64::MAX;
            let mut vertex = sink;
            while vertex != source {
                path_flow = path_flow.min(residual[parent[vertex]][vertex]);
                vertex = parent[vertex];
            }
            vertex = sink;
            while vertex != source {
                residual[parent[vertex]][vertex] -= path_flow;
                residual[vertex][parent[vertex]] += path_flow;
                vertex = parent[vertex];
            }
            total += path_flow;
        }
    }

    pub fn dinic(capacity: &[Vec<i64>], source: usize, sink: usize) -> i64 {
        let vertex_count = capacity.len();
        let mut residual = Self::residual_copy(capacity);
        let mut total = 0;
        loop {
            let mut level = vec![-1i64; vertex_count];
            let mut queue = VecDeque::new();
            level[source] = 0;
            queue.push_back(source);
            while let Some(vertex) = queue.pop_front() {
                for neighbor in 0..vertex_count {
                    if residual[vertex][neighbor] > 0 && level[neighbor] == -1 {
                        level[neighbor] = level[vertex] + 1;
                        queue.push_back(neighbor);
                    }
                }
            }
            if level[sink] == -1 {
                return total;
            }
            let mut next_edge = vec![0usize; vertex_count];
            loop {
                let sent = Self::dinic_send(&mut residual, &mut next_edge, &level, source, sink, i64::MAX / 4);
                if sent == 0 {
                    break;
                }
                total += sent;
            }
        }
    }

    fn dinic_send(
        residual: &mut [Vec<i64>],
        next_edge: &mut [usize],
        level: &[i64],
        vertex: usize,
        sink: usize,
        limit: i64,
    ) -> i64 {
        if vertex == sink {
            return limit;
        }
        while next_edge[vertex] < residual.len() {
            let neighbor = next_edge[vertex];
            if residual[vertex][neighbor] > 0 && level[neighbor] == level[vertex] + 1 {
                let sent = Self::dinic_send(residual, next_edge, level, neighbor, sink, limit.min(residual[vertex][neighbor]));
                if sent > 0 {
                    residual[vertex][neighbor] -= sent;
                    residual[neighbor][vertex] += sent;
                    return sent;
                }
            }
            next_edge[vertex] += 1;
        }
        0
    }

    pub fn hopcroft_karp(adjacency: &[Vec<usize>], right_count: usize) -> Vec<isize> {
        let left_count = adjacency.len();
        let mut left_match = vec![-1isize; left_count];
        let mut right_match = vec![-1isize; right_count];
        loop {
            let mut distance = vec![usize::MAX; left_count];
            let mut queue = VecDeque::new();
            for left in 0..left_count {
                if left_match[left] == -1 {
                    distance[left] = 0;
                    queue.push_back(left);
                }
            }
            let mut shortest = usize::MAX;
            while let Some(left) = queue.pop_front() {
                if distance[left] >= shortest {
                    continue;
                }
                for &right in &adjacency[left] {
                    let matched = right_match[right];
                    if matched == -1 {
                        shortest = distance[left] + 1;
                    } else {
                        let next = matched as usize;
                        if distance[next] == usize::MAX {
                            distance[next] = distance[left] + 1;
                            queue.push_back(next);
                        }
                    }
                }
            }
            if shortest == usize::MAX {
                return left_match;
            }
            for left in 0..left_count {
                if left_match[left] == -1 {
                    Self::hopcroft_augment(left, adjacency, shortest, &mut distance, &mut left_match, &mut right_match);
                }
            }
        }
    }

    fn hopcroft_augment(
        left: usize,
        adjacency: &[Vec<usize>],
        shortest: usize,
        distance: &mut [usize],
        left_match: &mut [isize],
        right_match: &mut [isize],
    ) -> bool {
        for &right in &adjacency[left] {
            let matched = right_match[right];
            if matched == -1 {
                if distance[left] + 1 != shortest {
                    continue;
                }
            } else {
                let next = matched as usize;
                if distance[next] != distance[left] + 1 || !Self::hopcroft_augment(next, adjacency, shortest, distance, left_match, right_match) {
                    continue;
                }
            }
            left_match[left] = right as isize;
            right_match[right] = left as isize;
            return true;
        }
        distance[left] = usize::MAX;
        false
    }
}
```

```typescript
export class NetworkFlow {
  private static fordSend(residual: number[][], visited: boolean[], vertex: number, sink: number, limit: number): number {
    if (vertex === sink) return limit;
    visited[vertex] = true;
    for (let neighbor = 0; neighbor < residual.length; neighbor++) {
      if (visited[neighbor] || residual[vertex][neighbor] <= 0) continue;
      const sent = NetworkFlow.fordSend(residual, visited, neighbor, sink, Math.min(limit, residual[vertex][neighbor]));
      if (sent > 0) {
        residual[vertex][neighbor] -= sent;
        residual[neighbor][vertex] += sent;
        return sent;
      }
    }
    return 0;
  }

  static fordFulkerson(capacity: number[][], source: number, sink: number): number {
    const residual = capacity.map((row) => row.slice());
    let total = 0;
    let sent: number;
    while ((sent = NetworkFlow.fordSend(residual, new Array<boolean>(residual.length).fill(false), source, sink, Number.MAX_SAFE_INTEGER / 4)) > 0) total += sent;
    return total;
  }

  static edmondsKarp(capacity: number[][], source: number, sink: number): number {
    const residual = capacity.map((row) => row.slice());
    let total = 0;
    while (true) {
      const parent = new Array<number>(residual.length).fill(-1);
      const queue = [source];
      parent[source] = source;
      while (queue.length > 0 && parent[sink] === -1) {
        const vertex = queue.shift()!;
        for (let neighbor = 0; neighbor < residual.length; neighbor++) {
          if (parent[neighbor] === -1 && residual[vertex][neighbor] > 0) {
            parent[neighbor] = vertex;
            queue.push(neighbor);
          }
        }
      }
      if (parent[sink] === -1) return total;
      let pathFlow = Number.MAX_SAFE_INTEGER;
      for (let vertex = sink; vertex !== source; vertex = parent[vertex]) {
        pathFlow = Math.min(pathFlow, residual[parent[vertex]][vertex]);
      }
      for (let vertex = sink; vertex !== source; vertex = parent[vertex]) {
        residual[parent[vertex]][vertex] -= pathFlow;
        residual[vertex][parent[vertex]] += pathFlow;
      }
      total += pathFlow;
    }
  }

  private static dinicSend(residual: number[][], nextEdge: number[], level: number[], vertex: number, sink: number, limit: number): number {
    if (vertex === sink) return limit;
    while (nextEdge[vertex] < residual.length) {
      const neighbor = nextEdge[vertex];
      if (residual[vertex][neighbor] > 0 && level[neighbor] === level[vertex] + 1) {
        const sent = NetworkFlow.dinicSend(residual, nextEdge, level, neighbor, sink, Math.min(limit, residual[vertex][neighbor]));
        if (sent > 0) {
          residual[vertex][neighbor] -= sent;
          residual[neighbor][vertex] += sent;
          return sent;
        }
      }
      nextEdge[vertex]++;
    }
    return 0;
  }

  static dinic(capacity: number[][], source: number, sink: number): number {
    const residual = capacity.map((row) => row.slice());
    let total = 0;
    while (true) {
      const level = new Array<number>(residual.length).fill(-1);
      const queue = [source];
      level[source] = 0;
      while (queue.length > 0) {
        const vertex = queue.shift()!;
        for (let neighbor = 0; neighbor < residual.length; neighbor++) {
          if (residual[vertex][neighbor] > 0 && level[neighbor] === -1) {
            level[neighbor] = level[vertex] + 1;
            queue.push(neighbor);
          }
        }
      }
      if (level[sink] === -1) return total;
      const nextEdge = new Array<number>(residual.length).fill(0);
      let sent: number;
      while ((sent = NetworkFlow.dinicSend(residual, nextEdge, level, source, sink, Number.MAX_SAFE_INTEGER / 4)) > 0) total += sent;
    }
  }

  static hopcroftKarp(adjacency: number[][], rightCount: number): number[] {
    const leftMatch = new Array<number>(adjacency.length).fill(-1);
    const rightMatch = new Array<number>(rightCount).fill(-1);
    while (true) {
      const distance = new Array<number>(adjacency.length).fill(-1);
      const queue: number[] = [];
      for (let left = 0; left < adjacency.length; left++) {
        if (leftMatch[left] === -1) {
          distance[left] = 0;
          queue.push(left);
        }
      }
      let shortest = -1;
      while (queue.length > 0) {
        const left = queue.shift()!;
        if (shortest !== -1 && distance[left] >= shortest) continue;
        for (const right of adjacency[left]) {
          const matched = rightMatch[right];
          if (matched === -1) {
            shortest = distance[left] + 1;
          } else if (distance[matched] === -1) {
            distance[matched] = distance[left] + 1;
            queue.push(matched);
          }
        }
      }
      if (shortest === -1) return leftMatch;
      const augment = (left: number): boolean => {
        for (const right of adjacency[left]) {
          const matched = rightMatch[right];
          if (matched === -1) {
            if (distance[left] + 1 !== shortest) continue;
          } else if (distance[matched] !== distance[left] + 1 || !augment(matched)) {
            continue;
          }
          leftMatch[left] = right;
          rightMatch[right] = left;
          return true;
        }
        distance[left] = -1;
        return false;
      };
      for (let left = 0; left < adjacency.length; left++) {
        if (leftMatch[left] === -1) augment(left);
      }
    }
  }
}
```

```go
package graph

type NetworkFlow struct{}

func (NetworkFlow) FordFulkerson(capacity [][]int64, source, sink int) int64 {
	residual := make([][]int64, len(capacity))
	for vertex := range capacity {
		residual[vertex] = append([]int64(nil), capacity[vertex]...)
	}
	visited := make([]bool, len(residual))
	var send func(int, int64) int64
	send = func(vertex int, limit int64) int64 {
		if vertex == sink {
			return limit
		}
		visited[vertex] = true
		for neighbor := range residual {
			if visited[neighbor] || residual[vertex][neighbor] <= 0 {
				continue
			}
			limitValue := limit
			if residual[vertex][neighbor] < limitValue {
				limitValue = residual[vertex][neighbor]
			}
			sent := send(neighbor, limitValue)
			if sent > 0 {
				residual[vertex][neighbor] -= sent
				residual[neighbor][vertex] += sent
				return sent
			}
		}
		return 0
	}
	var total int64
	for {
		for vertex := range visited {
			visited[vertex] = false
		}
		sent := send(source, int64(1<<62))
		if sent == 0 {
			return total
		}
		total += sent
	}
}

func (NetworkFlow) EdmondsKarp(capacity [][]int64, source, sink int) int64 {
	residual := make([][]int64, len(capacity))
	for vertex := range capacity {
		residual[vertex] = append([]int64(nil), capacity[vertex]...)
	}
	var total int64
	for {
		parent := make([]int, len(residual))
		for vertex := range parent {
			parent[vertex] = -1
		}
		queue := []int{source}
		parent[source] = source
		for len(queue) > 0 && parent[sink] == -1 {
			vertex := queue[0]
			queue = queue[1:]
			for neighbor := range residual {
				if parent[neighbor] == -1 && residual[vertex][neighbor] > 0 {
					parent[neighbor] = vertex
					queue = append(queue, neighbor)
				}
			}
		}
		if parent[sink] == -1 {
			return total
		}
		pathFlow := int64(1<<62 - 1)
		for vertex := sink; vertex != source; vertex = parent[vertex] {
			if residual[parent[vertex]][vertex] < pathFlow {
				pathFlow = residual[parent[vertex]][vertex]
			}
		}
		for vertex := sink; vertex != source; vertex = parent[vertex] {
			residual[parent[vertex]][vertex] -= pathFlow
			residual[vertex][parent[vertex]] += pathFlow
		}
		total += pathFlow
	}
}

func (NetworkFlow) Dinic(capacity [][]int64, source, sink int) int64 {
	residual := make([][]int64, len(capacity))
	for vertex := range capacity {
		residual[vertex] = append([]int64(nil), capacity[vertex]...)
	}
	var send func([]int, []int, int, int64) int64
	send = func(level, nextEdge []int, vertex int, limit int64) int64 {
		if vertex == sink {
			return limit
		}
		for nextEdge[vertex] < len(residual) {
			neighbor := nextEdge[vertex]
			if residual[vertex][neighbor] > 0 && level[neighbor] == level[vertex]+1 {
				limitValue := limit
				if residual[vertex][neighbor] < limitValue {
					limitValue = residual[vertex][neighbor]
				}
				sent := send(level, nextEdge, neighbor, limitValue)
				if sent > 0 {
					residual[vertex][neighbor] -= sent
					residual[neighbor][vertex] += sent
					return sent
				}
			}
			nextEdge[vertex]++
		}
		return 0
	}
	var total int64
	for {
		level := make([]int, len(residual))
		for vertex := range level {
			level[vertex] = -1
		}
		queue := []int{source}
		level[source] = 0
		for len(queue) > 0 {
			vertex := queue[0]
			queue = queue[1:]
			for neighbor := range residual {
				if residual[vertex][neighbor] > 0 && level[neighbor] == -1 {
					level[neighbor] = level[vertex] + 1
					queue = append(queue, neighbor)
				}
			}
		}
		if level[sink] == -1 {
			return total
		}
		nextEdge := make([]int, len(residual))
		for {
			sent := send(level, nextEdge, source, int64(1<<62))
			if sent == 0 {
				break
			}
			total += sent
		}
	}
}

func (NetworkFlow) HopcroftKarp(adjacency [][]int, rightCount int) []int {
    leftMatch := make([]int, len(adjacency))
    rightMatch := make([]int, rightCount)
    for left := range leftMatch {
        leftMatch[left] = -1
    }
    for right := range rightMatch {
        rightMatch[right] = -1
    }
    for {
        distance := make([]int, len(adjacency))
        queue := []int{}
        for left := range adjacency {
            if leftMatch[left] == -1 {
                distance[left] = 0
                queue = append(queue, left)
            } else {
                distance[left] = -1
            }
        }
        shortest := -1
        for len(queue) > 0 {
            left := queue[0]
            queue = queue[1:]
            if shortest != -1 && distance[left] >= shortest {
                continue
            }
            for _, right := range adjacency[left] {
                matched := rightMatch[right]
                if matched == -1 {
                    shortest = distance[left] + 1
                } else if distance[matched] == -1 {
                    distance[matched] = distance[left] + 1
                    queue = append(queue, matched)
                }
            }
        }
        if shortest == -1 {
            return leftMatch
        }
        var augment func(int) bool
        augment = func(left int) bool {
            for _, right := range adjacency[left] {
                matched := rightMatch[right]
                if matched == -1 {
                    if distance[left]+1 != shortest {
                        continue
                    }
                } else if distance[matched] != distance[left]+1 || !augment(matched) {
                    continue
                }
                leftMatch[left] = right
                rightMatch[right] = left
                return true
            }
            distance[left] = -1
            return false
        }
        for left := range adjacency {
            if leftMatch[left] == -1 {
                augment(left)
            }
        }
    }
}
```

## Complexity
For \(V\) vertices and \(E\) edges, with maximum flow \(F\):

| Algorithm | Time | Extra space |
| --- | --- | --- |
| Ford-Fulkerson with integer capacities | O(EF) | O(V+E) |
| Edmonds-Karp | O(VE²) | O(V²) with the matrix example |
| Dinic's algorithm | O(V²E) | O(V+E) |
| Hopcroft-Karp | O(E√V) | O(V+E) |

Ford-Fulkerson's bound is pseudo-polynomial in encoded capacities. The C, Java, Python, Rust, TypeScript, and Go flow examples use capacity matrices, so their residual space is O(V²); adjacency-list implementations reduce the structural overhead to O(V+E) while retaining the same algorithmic methods.

## When to use
- You need maximum throughput through a network with capacity constraints.
- You need to expose a minimum cut that identifies bottlenecks.
- You need to model assignment, transportation, or unit-capacity matching as flow.
- You need a maximum bipartite matching in a large graph.

## Alternatives
- **Push-relabel** — works with preflows and height labels and can outperform Dinic on some practical families, but has more complex invariants.
- **Orlin's algorithm** — has stronger all-pairs bounds for minimum-cost flow, which is a different optimization problem.
- **Hungarian algorithm** — solves minimum-cost assignment directly and can be preferable when a full cost matrix and optimal cost are required.

## Related
- [Graph Representations (Adjacency Matrix, Adjacency List, Edge List)](01-graph-representations.md)
- [Graph Traversals: Breadth-First Search (BFS) and Depth-First Search (DFS)](02-graph-traversals.md)
- [Shortest Path Algorithms: Single-Source (Dijkstra's, Bellman-Ford) & All-Pairs (Floyd-Warshall, Johnson's)](05-shortest-paths.md)
