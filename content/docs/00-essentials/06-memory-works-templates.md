---
title: "Memory Works (Templates)"
weight: 6
---


Memorize this:

1. Binary search
2. Backtracking
3. BFS (tree and graph)
4. DFS (tree and graph)
5. Topological sort
6. Trie
7. Union-Find

## Backtracking

```java
private static void dfs(state, res) {
    if (isSolution(state)) {
        res.add(state.toString()); // add a copy of the state to the result
        return;
    }
    for (choice : choices) {
        state.append(choice);
        dfs(state, res);
        state.pop();
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
        if (arr.get(mid) == target) return mid;
        if (arr.get(mid) < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    return -1;
}
```

## BFS on Tree

```java
public Node bfs(Node root) {
    ArrayDeque<Node> queue = new ArrayDeque<>();
    while (queue.size() > 0) {
        Node node = queue.poll();
        for (Node child : node.children) {
            if (OK(child)) {
                return FOUND(child);
            }
            queue.add(child);
        }
    }
    return NOT_FOUND;
}
```

## DFS on Tree

```java
public static Node dfs(Node root, int target) {
    if (root == null) {
      return null;
    }
    if (root.val == target) {
      return root;
    }
    Node left = dfs(root.left, target)
    if (left != null) {
      return left;
    }
    return dfs(root.right, target)
}
```

## BFS on Graphs

```java
public void bfs(Node root) {
    ArrayDeque<Node> queue = new ArrayDeque<>();
    queue.add(root);
    Set<Node> visited = new HashSet<>();
    while (queue.size() > 0) {
        Node node = queue.pop();
        for (Node neighbor : getNeighbors(node)) {
            if (visited.contains(neighbor)) {
                continue;
            }
            queue.add(neighbor);
            visited.add(neighbor);
        }
    }
}
```

## DFS on Graphs

```java
public void dfs(Node root, Set<Node> visited) {
    for (Node neighbor : node.neighbors) {
        if (visited.contains(node)) {
            continue;
        }
        visited.add(neighbor);
        dfs(neighbor, visited);
    }
}
```

## Topological sort

```java
public static <T> Map<T, Integer> countParents(Map<T, List<T>> graph) {
    Map<T, Integer> counts = new HashMap<>();
    graph.keySet().forEach(node -> {
        counts.put(node, 0);
    });
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

## Trie

```java
public static class Node {
    char value;
    HashMap<Character, Node> children = new HashMap<>();
    public Node(char value) {
        this.value = value;
    }
    void insert(String s, int idx) {   
        if (idx == s.length()) {
            return;
        }
        if (children.containsKey(s.charAt(idx))) {
            children.get(s.charAt(idx)).insert(s, idx + 1);
        }
        else {
            children.put(s.charAt(idx), new Node(s.charAt(idx)));
            children.get(s.charAt(idx)).insert(s, idx + 1);
        }
    }
}
```

## Union-Find

```java
public static class UnionFind<T> {
    private HashMap<T, T> f = new HashMap<>();

    public T find(T x) {
        T y = f.getOrDefault(x, x);
        if (y != x) {
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
