---
title: "Spatial Indexing & Geospatial Data Structures: Quadtrees, R-Trees, KD-Trees, and Geohashing"
weight: 7
toc: true
tabs: {sync: true}
---

## What it is
**Spatial indexing** stores points or regions so a query can discard most of the dataset before checking candidates. A **quadtree** recursively divides a region into four quadrants, an **R-tree** stores bounding rectangles that can overlap, a **KD-tree** splits space by one coordinate at each level, and a **geohash** encodes a latitude-longitude location as a short string whose nearby locations share a prefix.

## How it works
A spatial query has a location and a shape, such as a point, rectangle, radius, or map viewport. Instead of scanning every record, an index follows a hierarchy of regions and examines only records whose stored region may intersect the query.

A **quadtree** works like filing papers into progressively smaller folders. Each node represents a square region. A leaf stores a small list of points; when the list exceeds a threshold, the region splits into four children. A range query rejects a node when its square does not intersect the query rectangle. A nearest-neighbor query rejects a node when the closest possible point in its square is farther away than the best answer found so far. The implementation caps depth at 32 levels. A leaf at that depth accepts additional points, so collocated coordinates and precision limits cannot trigger endless subdivision.

An **R-tree** stores rectangles rather than quadrants. Objects are grouped when their bounding rectangles fit in a larger rectangle, so child rectangles may overlap. This makes R-trees natural for rectangles, polygons, and mixed dimensions, but updates can require a split or a parent adjustment. A **KD-tree** alternates or chooses a coordinate for each split and is efficient for point data, especially with a balanced build. A **geohash** interleaves longitude and latitude bits and encodes the result in base 32. It is excellent for prefix filtering and cache keys, but nearby points can fall on opposite sides of a cell boundary, so production systems use bounding boxes or multiple neighboring cells.

The implementation below uses one equivalent operation set in all six languages: `insert`, `query`, `nearest`, and `geohash`. Its concrete index is a quadtree over normalized coordinates from 0 to 1, and every implementation returns exactly the requested number of geohash characters. C reports an invalid insert with `false` and returns `NULL` for an invalid geohash request; the other languages throw or panic on the same normalized-coordinate and nonnegative-precision requirements. The same algorithm makes the comparison concrete; databases such as PostGIS, Elasticsearch, and MongoDB choose among these structures according to object shape, update rate, and query mix.

{{< tabs >}}
{{< tab name="Java" >}}
```java
import java.util.ArrayList;
import java.util.List;

public class SpatialIndex {
    private static final int MAX_POINTS = 4;
    private static final int MAX_DEPTH = 32;

    public static class Point {
        public final double x;
        public final double y;

        public Point(double x, double y) {
            this.x = x;
            this.y = y;
        }
    }

    public static class Rect {
        public final double minX;
        public final double minY;
        public final double maxX;
        public final double maxY;

        public Rect(double minX, double minY, double maxX, double maxY) {
            this.minX = minX;
            this.minY = minY;
            this.maxX = maxX;
            this.maxY = maxY;
        }
    }

    private static class Node {
        final double x;
        final double y;
        final double size;
        final List<Point> points = new ArrayList<>();
        Node[] children;
        int count;

        Node(double x, double y, double size) {
            this.x = x;
            this.y = y;
            this.size = size;
        }
    }

    private final Node root = new Node(0, 0, 1);

    public void insert(Point point) {
        if (point.x < 0 || point.x > 1 || point.y < 0 || point.y > 1) {
            throw new IllegalArgumentException("point must be normalized");
        }
        insert(root, point, 0);
    }

    private void insert(Node node, Point point, int depth) {
        if (node.children != null) {
            insert(node.children[quadrant(node, point)], point, depth + 1);
            node.count++;
            return;
        }
        if (node.points.size() < MAX_POINTS || depth >= MAX_DEPTH) {
            node.points.add(point);
            node.count++;
            return;
        }
        node.children = new Node[4];
        for (int index = 0; index < 4; index++) {
            double offset = (index & 1) == 0 ? 0 : node.size / 2;
            double yOffset = (index & 2) == 0 ? 0 : node.size / 2;
            node.children[index] = new Node(node.x + offset, node.y + yOffset, node.size / 2);
        }
        for (Point existing : node.points) {
            insert(node.children[quadrant(node, existing)], existing, depth + 1);
        }
        node.points.clear();
        insert(node.children[quadrant(node, point)], point, depth + 1);
        node.count++;
    }

    private int quadrant(Node node, Point point) {
        int xBit = point.x >= node.x + node.size / 2 ? 1 : 0;
        int yBit = point.y >= node.y + node.size / 2 ? 2 : 0;
        return xBit | yBit;
    }

    public List<Point> query(Rect rectangle) {
        List<Point> result = new ArrayList<>();
        query(root, rectangle, result);
        return result;
    }

    private void query(Node node, Rect rectangle, List<Point> result) {
        if (!intersects(node.x, node.y, node.size, rectangle)) return;
        if (node.children == null) {
            for (Point point : node.points) {
                if (rectangle.minX <= point.x && point.x <= rectangle.maxX &&
                    rectangle.minY <= point.y && point.y <= rectangle.maxY) {
                    result.add(point);
                }
            }
            return;
        }
        for (Node child : node.children) query(child, rectangle, result);
    }

    public Point nearest(Point queryPoint) {
        double[] best = {Double.POSITIVE_INFINITY};
        Point[] result = {null};
        nearest(root, queryPoint, best, result);
        return result[0];
    }

    private void nearest(Node node, Point queryPoint, double[] best, Point[] result) {
        if (boundDistance(node, queryPoint) > best[0]) return;
        if (node.children == null) {
            for (Point point : node.points) {
                double distance = distanceSquared(point, queryPoint);
                if (distance < best[0]) {
                    best[0] = distance;
                    result[0] = point;
                }
            }
            return;
        }
        for (Node child : node.children) nearest(child, queryPoint, best, result);
    }

    public String geohash(Point point, int precision) {
        if (precision < 0 || point.x < 0 || point.x > 1 || point.y < 0 || point.y > 1) {
            throw new IllegalArgumentException("point must be normalized and precision nonnegative");
        }
        double x = point.x;
        double y = point.y;
        int hash = 0;
        int bits = 0;
        boolean even = true;
        String result = "";
        for (long index = 0; index < (long) precision * 5; index++) {
            int bit;
            if (even) {
                bit = x >= 0.5 ? 1 : 0;
                x = x * 2 - bit;
            } else {
                bit = y >= 0.5 ? 1 : 0;
                y = y * 2 - bit;
            }
            hash = (hash << 1) | bit;
            bits++;
            if (bits == 5) {
                result += "0123456789bcdefghjkmnpqrstuvwxyz"[hash];
                hash = 0;
                bits = 0;
            }
            even = !even;
        }
        return result;
    }

    private boolean intersects(double x, double y, double size, Rect rectangle) {
        return x <= rectangle.maxX && x + size >= rectangle.minX &&
               y <= rectangle.maxY && y + size >= rectangle.minY;
    }

    private double boundDistance(Node node, Point point) {
        double dx = Math.max(Math.max(node.x - point.x, 0), point.x - (node.x + node.size));
        double dy = Math.max(Math.max(node.y - point.y, 0), point.y - (node.y + node.size));
        return dx * dx + dy * dy;
    }

    private double distanceSquared(Point first, Point second) {
        double dx = first.x - second.x;
        double dy = first.y - second.y;
        return dx * dx + dy * dy;
    }
}
```

{{< /tab >}}
{{< tab name="C" >}}
```c
#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

#define SPATIAL_INDEX_MAX_POINTS 4
#define SPATIAL_INDEX_MAX_DEPTH 32

typedef struct { double x; double y; } Point;
typedef struct { double min_x; double min_y; double max_x; double max_y; } Rect;
typedef struct SpatialNode SpatialNode;

struct SpatialNode {
    double x;
    double y;
    double size;
    Point *points;
    int point_count;
    int point_capacity;
    SpatialNode *children[4];
    int count;
};

typedef struct { SpatialNode *root; } SpatialIndex;

static SpatialNode *spatial_node_new(double x, double y, double size) {
    SpatialNode *node = calloc(1, sizeof(SpatialNode));
    node->x = x;
    node->y = y;
    node->size = size;
    return node;
}

static void spatial_node_destroy(SpatialNode *node) {
    for (int index = 0; index < 4; index++) {
        if (node->children[index] != NULL) spatial_node_destroy(node->children[index]);
    }
    free(node->points);
    free(node);
}

static int quadrant(SpatialNode *node, Point point) {
    return (point.x >= node->x + node->size / 2 ? 1 : 0) |
           (point.y >= node->y + node->size / 2 ? 2 : 0);
}

static void spatial_insert(SpatialNode *node, Point point, int depth) {
    if (node->children[0]) {
        spatial_insert(node->children[quadrant(node, point)], point, depth + 1);
        node->count++;
        return;
    }
    if (node->point_count < SPATIAL_INDEX_MAX_POINTS || depth >= SPATIAL_INDEX_MAX_DEPTH) {
        if (node->point_count == node->point_capacity) {
            node->point_capacity = node->point_capacity == 0 ? SPATIAL_INDEX_MAX_POINTS : node->point_capacity * 2;
            node->points = realloc(node->points, (size_t)node->point_capacity * sizeof(Point));
        }
        node->points[node->point_count++] = point;
        node->count++;
        return;
    }
    for (int index = 0; index < 4; index++) {
        double x = node->x + ((index & 1) ? node->size / 2 : 0);
        double y = node->y + ((index & 2) ? node->size / 2 : 0);
        node->children[index] = spatial_node_new(x, y, node->size / 2);
    }
    for (int index = 0; index < node->point_count; index++) {
        spatial_insert(node->children[quadrant(node, node->points[index])], node->points[index], depth + 1);
    }
    free(node->points);
    node->points = NULL;
    node->point_count = 0;
    node->point_capacity = 0;
    spatial_insert(node->children[quadrant(node, point)], point, depth + 1);
    node->count++;
}

static SpatialIndex *spatial_index_new(void) {
    SpatialIndex *index = malloc(sizeof(SpatialIndex));
    index->root = spatial_node_new(0, 0, 1);
    return index;
}

bool spatial_index_insert(SpatialIndex *index, Point point) {
    if (point.x < 0 || point.x > 1 || point.y < 0 || point.y > 1) return false;
    spatial_insert(index->root, point, 0);
    return true;
}

static void spatial_index_free(SpatialIndex *index) {
    spatial_node_destroy(index->root);
    free(index);
}

static void spatial_query_node(SpatialNode *node, Rect rectangle, Point *output, int *count, int capacity) {
    if (node->x > rectangle.max_x || node->x + node->size < rectangle.min_x ||
        node->y > rectangle.max_y || node->y + node->size < rectangle.min_y) return;
    if (!node->children[0]) {
        for (int index = 0; index < node->point_count; index++) {
            Point point = node->points[index];
            if (point.x >= rectangle.min_x && point.x <= rectangle.max_x &&
                point.y >= rectangle.min_y && point.y <= rectangle.max_y && *count < capacity) {
                output[(*count)++] = point;
            }
        }
        return;
    }
    for (int index = 0; index < 4; index++) spatial_query_node(node->children[index], rectangle, output, count, capacity);
}

static int spatial_query(SpatialIndex *index, Rect rectangle, Point *output, int capacity) {
    int count = 0;
    spatial_query_node(index->root, rectangle, output, &count, capacity);
    return count;
}

static double distance_squared(Point first, Point second) {
    double dx = first.x - second.x;
    double dy = first.y - second.y;
    return dx * dx + dy * dy;
}

static void spatial_nearest_node(SpatialNode *node, Point query, double *best, Point *result) {
    double dx = fmax(fmax(node->x - query.x, 0), query.x - (node->x + node->size));
    double dy = fmax(fmax(node->y - query.y, 0), query.y - (node->y + node->size));
    if (dx * dx + dy * dy > *best) return;
    if (!node->children[0]) {
        for (int index = 0; index < node->point_count; index++) {
            double distance = distance_squared(node->points[index], query);
            if (distance < *best) {
                *best = distance;
                *result = node->points[index];
            }
        }
        return;
    }
    for (int index = 0; index < 4; index++) spatial_nearest_node(node->children[index], query, best, result);
}

static bool spatial_nearest(SpatialIndex *index, Point query, Point *result) {
    double best = INFINITY;
    *result = (Point){0, 0};
    spatial_nearest_node(index->root, query, &best, result);
    return isfinite(best);
}

static char *spatial_geohash(Point point, int precision) {
    if (precision < 0 || point.x < 0 || point.x > 1 || point.y < 0 || point.y > 1) return NULL;
    char alphabet[] = "0123456789bcdefghjkmnpqrstuvwxyz";
    char *result = malloc((size_t)precision + 1);
    if (result == NULL) return NULL;
    double x = point.x;
    double y = point.y;
    int hash = 0;
    int bits = 0;
    bool even = true;
    for (int64_t index = 0; index < (int64_t)precision * 5; index++) {
        int bit;
        if (even) {
            bit = x >= 0.5;
            x = x * 2 - bit;
        } else {
            bit = y >= 0.5;
            y = y * 2 - bit;
        }
        hash = (hash << 1) | bit;
        bits++;
        if (bits == 5) {
            result[index / 5] = alphabet[hash];
            hash = 0;
            bits = 0;
        }
        even = !even;
    }
    result[precision] = '\0';
    return result;
}
```

{{< /tab >}}
{{< tab name="Python" >}}
```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Rect:
    def __init__(self, min_x, min_y, max_x, max_y):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y


class SpatialIndex:
    max_points = 4
    max_depth = 32

    def __init__(self):
        self.root = self._node(0, 0, 1)

    @staticmethod
    def _node(x, y, size):
        return {"x": x, "y": y, "size": size, "points": [], "children": None, "count": 0}

    @staticmethod
    def _quadrant(node, point):
        return (1 if point.x >= node["x"] + node["size"] / 2 else 0) | (2 if point.y >= node["y"] + node["size"] / 2 else 0)

    def insert(self, point):
        if not 0 <= point.x <= 1 or not 0 <= point.y <= 1:
            raise ValueError("point must be normalized")
        self._insert(self.root, point, 0)

    def _insert(self, node, point, depth):
        if node["children"] is not None:
            self._insert(node["children"][self._quadrant(node, point)], point, depth + 1)
            node["count"] += 1
            return
        if len(node["points"]) < self.max_points or depth >= self.max_depth:
            node["points"].append(point)
            node["count"] += 1
            return
        node["children"] = [
            self._node(node["x"] + (index & 1) * node["size"] / 2,
                       node["y"] + (index & 2) * node["size"] / 2, node["size"] / 2)
            for index in range(4)
        ]
        existing = node["points"]
        node["points"] = []
        for old_point in existing:
            self._insert(node["children"][self._quadrant(node, old_point)], old_point, depth + 1)
        self._insert(node["children"][self._quadrant(node, point)], point, depth + 1)
        node["count"] += 1

    def query(self, rectangle):
        result = []
        self._query(self.root, rectangle, result)
        return result

    def _query(self, node, rectangle, result):
        if (node["x"] > rectangle.max_x or node["x"] + node["size"] < rectangle.min_x or
            node["y"] > rectangle.max_y or node["y"] + node["size"] < rectangle.min_y):
            return
        if node["children"] is None:
            result.extend(point for point in node["points"]
                          if rectangle.min_x <= point.x <= rectangle.max_x
                          and rectangle.min_y <= point.y <= rectangle.max_y)
            return
        for child in node["children"]:
            self._query(child, rectangle, result)

    def nearest(self, query):
        best = float("inf")
        result = None
        self._nearest(self.root, query, [best, result])
        return result

    def _nearest(self, node, query, state):
        dx = max(node["x"] - query.x, 0, query.x - node["x"] - node["size"])
        dy = max(node["y"] - query.y, 0, query.y - node["y"] - node["size"])
        if dx * dx + dy * dy > state[0]:
            return
        if node["children"] is None:
            for point in node["points"]:
                distance = (point.x - query.x) ** 2 + (point.y - query.y) ** 2
                if distance < state[0]:
                    state[0] = distance
                    state[1] = point
            return
        for child in node["children"]:
            self._nearest(child, query, state)

    def geohash(self, point, precision):
        if precision < 0 or not 0 <= point.x <= 1 or not 0 <= point.y <= 1:
            raise ValueError("point must be normalized and precision nonnegative")
        alphabet = "0123456789bcdefghjkmnpqrstuvwxyz"
        x, y = point.x, point.y
        hash_value = 0
        bits = 0
        even = True
        result = []
        for _ in range(precision * 5):
            if even:
                bit = int(x >= 0.5)
                x = x * 2 - bit
            else:
                bit = int(y >= 0.5)
                y = y * 2 - bit
            hash_value = (hash_value << 1) | bit
            bits += 1
            if bits == 5:
                result.append(alphabet[hash_value])
                hash_value = 0
                bits = 0
            even = not even
        return "".join(result)
```

{{< /tab >}}
{{< tab name="Rust" >}}
```rust
const MAX_DEPTH: u32 = 32;

#[derive(Clone, Copy)]
pub struct Point {
    pub x: f64,
    pub y: f64,
}

#[derive(Clone, Copy)]
pub struct Rect {
    pub min_x: f64,
    pub min_y: f64,
    pub max_x: f64,
    pub max_y: f64,
}

struct Node {
    x: f64,
    y: f64,
    size: f64,
    points: Vec<Point>,
    children: Option<Vec<Option<Node>>>,
    count: usize,
}

pub struct SpatialIndex {
    root: Node,
}

impl Node {
    fn new(x: f64, y: f64, size: f64) -> Self {
        Self { x, y, size, points: Vec::new(), children: None, count: 0 }
    }

    fn quadrant(&self, point: Point) -> usize {
        (if point.x >= self.x + self.size / 2.0 { 1 } else { 0 })
            | (if point.y >= self.y + self.size / 2.0 { 2 } else { 0 })
    }

    fn insert(&mut self, point: Point, depth: u32) {
        if self.children.is_some() {
            let quadrant = self.quadrant(point);
            self.children.as_mut().unwrap()[quadrant].as_mut().unwrap().insert(point, depth + 1);
            self.count += 1;
            return;
        }
        if self.points.len() < 4 || depth >= MAX_DEPTH {
            self.points.push(point);
            self.count += 1;
            return;
        }
        let existing = std::mem::take(&mut self.points);
        self.children = Some((0..4).map(|index| {
            Some(Node::new(
                self.x + if index & 1 == 1 { self.size / 2.0 } else { 0.0 },
                self.y + if index & 2 == 2 { self.size / 2.0 } else { 0.0 },
                self.size / 2.0,
            ))
        }).collect());
        for old_point in existing {
            let quadrant = self.quadrant(old_point);
            self.children.as_mut().unwrap()[quadrant].as_mut().unwrap().insert(old_point, depth + 1);
        }
        let quadrant = self.quadrant(point);
        self.children.as_mut().unwrap()[quadrant].as_mut().unwrap().insert(point, depth + 1);
        self.count += 1;
    }
}

impl SpatialIndex {
    pub fn new() -> Self {
        Self { root: Node::new(0.0, 0.0, 1.0) }
    }

    pub fn insert(&mut self, point: Point) {
        assert!((0.0..=1.0).contains(&point.x) && (0.0..=1.0).contains(&point.y));
        self.root.insert(point, 0);
    }

    pub fn query(&self, rectangle: Rect) -> Vec<Point> {
        let mut result = Vec::new();
        self.query_node(&self.root, rectangle, &mut result);
        result
    }

    fn query_node(&self, node: &Node, rectangle: Rect, result: &mut Vec<Point>) {
        if node.x > rectangle.max_x || node.x + node.size < rectangle.min_x ||
           node.y > rectangle.max_y || node.y + node.size < rectangle.min_y {
            return;
        }
        if let Some(children) = &node.children {
            for child in children.iter().flatten() {
                self.query_node(child, rectangle, result);
            }
            return;
        }
        result.extend(node.points.iter().copied().filter(|point| {
            point.x >= rectangle.min_x && point.x <= rectangle.max_x &&
            point.y >= rectangle.min_y && point.y <= rectangle.max_y
        }));
    }

    pub fn nearest(&self, query: Point) -> Option<Point> {
        self.nearest_node(&self.root, query, f64::INFINITY).0
    }

    fn nearest_node(&self, node: &Node, query: Point, best: f64) -> (Option<Point>, f64) {
        let dx = (node.x - query.x).max(0.0).max(query.x - node.x - node.size);
        let dy = (node.y - query.y).max(0.0).max(query.y - node.y - node.size);
        if dx * dx + dy * dy > best {
            return (None, best);
        }
        if let Some(children) = &node.children {
            let mut result = None;
            let mut distance = best;
            for child in children.iter().flatten() {
                let found = self.nearest_node(child, query, distance);
                if found.0.is_some() {
                    result = found.0;
                    distance = found.1;
                }
            }
            return (result, distance);
        }
        let mut result = None;
        let mut distance = best;
        for point in &node.points {
            let candidate = (point.x - query.x).powi(2) + (point.y - query.y).powi(2);
            if candidate < distance {
                result = Some(*point);
                distance = candidate;
            }
        }
        (result, distance)
    }

    pub fn geohash(&self, point: Point, precision: usize) -> String {
        assert!((0.0..=1.0).contains(&point.x) && (0.0..=1.0).contains(&point.y));
        let alphabet = b"0123456789bcdefghjkmnpqrstuvwxyz";
        let mut x = point.x;
        let mut y = point.y;
        let mut result = String::new();
        let mut hash_value = 0;
        let mut even = true;
        for bit_index in 0..precision * 5 {
            let bit = if even { usize::from(x >= 0.5) } else { usize::from(y >= 0.5) };
            if even {
                x = x * 2.0 - bit as f64;
            } else {
                y = y * 2.0 - bit as f64;
            }
            hash_value = (hash_value << 1) | bit;
            if bit_index % 5 == 4 {
                result.push(alphabet[hash_value] as char);
                hash_value = 0;
            }
            even = !even;
        }
        result
    }
}
```

{{< /tab >}}
{{< tab name="TypeScript" >}}
```typescript
export interface Point {
  x: number;
  y: number;
}

export interface Rect {
  minX: number;
  minY: number;
  maxX: number;
  maxY: number;
}

interface Node {
  x: number;
  y: number;
  size: number;
  points: Point[];
  children: Node[] | null;
  count: number;
}

export class SpatialIndex {
  private static readonly maxPoints = 4;
  private static readonly maxDepth = 32;
  private root: Node = { x: 0, y: 0, size: 1, points: [], children: null, count: 0 };

  insert(point: Point): void {
    if (point.x < 0 || point.x > 1 || point.y < 0 || point.y > 1) throw new Error("point must be normalized");
    this.insertNode(this.root, point, 0);
  }

  private quadrant(node: Node, point: Point): number {
    return (point.x >= node.x + node.size / 2 ? 1 : 0) | (point.y >= node.y + node.size / 2 ? 2 : 0);
  }

  private insertNode(node: Node, point: Point, depth: number): void {
    if (node.children) {
      this.insertNode(node.children[this.quadrant(node, point)], point, depth + 1);
      node.count++;
      return;
    }
    if (node.points.length < SpatialIndex.maxPoints || depth >= SpatialIndex.maxDepth) {
      node.points.push(point);
      node.count++;
      return;
    }
    node.children = Array.from({ length: 4 }, (_, index) => ({
      x: node.x + (index & 1) * node.size / 2,
      y: node.y + (index & 2) * node.size / 2,
      size: node.size / 2,
      points: [],
      children: null,
      count: 0,
    }));
    const existing = node.points;
    node.points = [];
    for (const oldPoint of existing) this.insertNode(node.children[this.quadrant(node, oldPoint)], oldPoint, depth + 1);
    this.insertNode(node.children[this.quadrant(node, point)], point, depth + 1);
    node.count++;
  }

  query(rectangle: Rect): Point[] {
    const result: Point[] = [];
    this.queryNode(this.root, rectangle, result);
    return result;
  }

  private queryNode(node: Node, rectangle: Rect, result: Point[]): void {
    if (node.x > rectangle.maxX || node.x + node.size < rectangle.minX || node.y > rectangle.maxY || node.y + node.size < rectangle.minY) return;
    if (!node.children) {
      result.push(...node.points.filter((point) => rectangle.minX <= point.x && point.x <= rectangle.maxX && rectangle.minY <= point.y && point.y <= rectangle.maxY));
      return;
    }
    node.children.forEach((child) => this.queryNode(child, rectangle, result));
  }

  nearest(query: Point): Point | undefined {
    let best = Infinity;
    let result: Point | undefined;
    const visit = (node: Node): void => {
      const dx = Math.max(node.x - query.x, 0, query.x - node.x - node.size);
      const dy = Math.max(node.y - query.y, 0, query.y - node.y - node.size);
      if (dx * dx + dy * dy > best) return;
      if (!node.children) {
        node.points.forEach((point) => {
          const distance = (point.x - query.x) ** 2 + (point.y - query.y) ** 2;
          if (distance < best) { best = distance; result = point; }
        });
        return;
      }
      node.children.forEach(visit);
    };
    visit(this.root);
    return result;
  }

  geohash(point: Point, precision: number): string {
    if (!Number.isInteger(precision) || precision < 0 || point.x < 0 || point.x > 1 || point.y < 0 || point.y > 1) {
      throw new Error("point must be normalized and precision must be a nonnegative integer");
    }
    const alphabet = "0123456789bcdefghjkmnpqrstuvwxyz";
    let x = point.x;
    let y = point.y;
    const result: string[] = [];
    let hashValue = 0;
    let even = true;
    for (let bitIndex = 0; bitIndex < precision * 5; bitIndex++) {
      const bit = even ? Number(x >= 0.5) : Number(y >= 0.5);
      if (even) x = x * 2 - bit;
      else y = y * 2 - bit;
      hashValue = (hashValue << 1) | bit;
      if (bitIndex % 5 === 4) {
        result.push(alphabet[hashValue]);
        hashValue = 0;
      }
      even = !even;
    }
    return result.join("");
  }
}
```

{{< /tab >}}
{{< tab name="Go" >}}
```go
package spatialindex

import "math"

const (
    maxPoints = 4
    maxDepth  = 32
)

type Point struct { X, Y float64 }
type Rect struct { MinX, MinY, MaxX, MaxY float64 }
type node struct { x, y, size float64; points []Point; children [4]*node; count int }

type SpatialIndex struct { root *node }

func newNode(x, y, size float64) *node { return &node{x: x, y: y, size: size} }
func quadrant(node *node, point Point) int {
    result := 0
    if point.X >= node.x+node.size/2 { result |= 1 }
    if point.Y >= node.y+node.size/2 { result |= 2 }
    return result
}

func (node *node) insert(point Point, depth int) {
    if node.children[0] != nil {
        node.children[quadrant(node, point)].insert(point, depth+1)
        node.count++
        return
    }
    if len(node.points) < maxPoints || depth >= maxDepth {
        node.points = append(node.points, point)
        node.count++
        return
    }
    for index := 0; index < 4; index++ {
        x := node.x + float64(index&1)*node.size/2
        y := node.y + float64(index&2)*node.size/2
        node.children[index] = newNode(x, y, node.size/2)
    }
    existing := node.points
    node.points = nil
    for _, oldPoint := range existing { node.children[quadrant(node, oldPoint)].insert(oldPoint, depth+1) }
    node.children[quadrant(node, point)].insert(point, depth+1)
    node.count++
}

func NewSpatialIndex() *SpatialIndex { return &SpatialIndex{root: newNode(0, 0, 1)} }
func (index *SpatialIndex) Insert(point Point) {
    if point.X < 0 || point.X > 1 || point.Y < 0 || point.Y > 1 { panic("point must be normalized") }
    index.root.insert(point, 0)
}

func (index *SpatialIndex) Query(rectangle Rect) []Point {
    var result []Point
    index.queryNode(index.root, rectangle, &result)
    return result
}
func (index *SpatialIndex) queryNode(current *node, rectangle Rect, result *[]Point) {
    if current.x > rectangle.MaxX || current.x+current.size < rectangle.MinX || current.y > rectangle.MaxY || current.y+current.size < rectangle.MinY { return }
    if current.children[0] == nil {
        for _, point := range current.points {
            if rectangle.MinX <= point.X && point.X <= rectangle.MaxX && rectangle.MinY <= point.Y && point.Y <= rectangle.MaxY { *result = append(*result, point) }
        }
        return
    }
    for _, child := range current.children { index.queryNode(child, rectangle, result) }
}

func (index *SpatialIndex) Nearest(query Point) (Point, bool) {
    best := math.Inf(1)
    result := Point{}
    found := false
    var visit func(*node)
    visit = func(current *node) {
        dx := math.Max(math.Max(current.x-query.X, 0), query.X-(current.x+current.size))
        dy := math.Max(math.Max(current.y-query.Y, 0), query.Y-(current.y+current.size))
        if dx*dx+dy*dy > best { return }
        if current.children[0] == nil {
            for _, point := range current.points {
                distance := (point.X-query.X)*(point.X-query.X) + (point.Y-query.Y)*(point.Y-query.Y)
                if distance < best { best, result, found = distance, point, true }
            }
            return
        }
        for _, child := range current.children { visit(child) }
    }
    visit(index.root)
    return result, found
}

func (index *SpatialIndex) Geohash(point Point, precision int) string {
    if precision < 0 || point.X < 0 || point.X > 1 || point.Y < 0 || point.Y > 1 { panic("point must be normalized and precision nonnegative") }
    alphabet := "0123456789bcdefghjkmnpqrstuvwxyz"
    x, y := point.X, point.Y
    result := make([]byte, 0, precision)
    hashValue := 0
    even := true
    for bitIndex := 0; bitIndex < precision*5; bitIndex++ {
        var bit int
        if even {
            if x >= 0.5 { bit = 1 }
            x = x*2 - float64(bit)
        } else {
            if y >= 0.5 { bit = 1 }
            y = y*2 - float64(bit)
        }
        hashValue = hashValue<<1 | bit
        if bitIndex%5 == 4 {
            result = append(result, alphabet[hashValue])
            hashValue = 0
        }
        even = !even
    }
    return string(result)
}
{{< /tab >}}
{{< /tabs >}}

## Complexity
For \(n\) points, \(d\) dimensions, and a well-distributed spatial tree, the following are typical bounds. Exact constants depend on the object shape, fanout, depth cap, and query selectivity; clustered or collocated data can force a traversal to visit most nodes.

| Operation or structure | Time | Space or result |
| --- | --- | --- |
| Quadtree range query | O(sqrt(n) + k) for well-distributed two-dimensional points; O(n) worst case | O(n), O(k) output |
| KD-tree range query | O(n^(1 - 1/d) + k) | O(n), O(k) output |
| R-tree range query | O(log n + k) under a balanced, selective query | O(n) or O(n log n) with stored object data |
| Quadtree or KD-tree nearest query | O(log n) expected for balanced, well-distributed points; O(n) worst case | O(log n) search stack |
| Geohash with precision p | O(p) | O(p) characters |
| Insert into a point quadtree | O(h) with O(1) amortized leaf append, where the implementation caps h at 32 | O(n) index data |

A geohash is a filter, not a precise geometry. Increasing precision makes cells smaller, but a point near a cell edge may require checking neighboring cells to avoid a false negative.

## When to use
- You need point, rectangle, radius, or map-viewport queries and cannot scan every record.
- You need nearest-neighbor search for locations, stores, sensors, or points of interest.
- Your objects are points and a balanced KD-tree or quadtree is a good fit.
- Your objects are rectangles or polygons and an R-tree avoids recomputing complex geometry.
- You need a compact prefix key for coarse geospatial filtering and cache partitioning.

## Alternatives
- **Linear scan** — is simple and sometimes fastest for small data, but costs O(n) per query.
- **R-tree** — handles rectangles and overlapping object extents well, but uses more storage and has update rebalancing costs.
- **KD-tree** — gives strong point-query performance in low dimensions, but degrades when points cluster or dimensionality grows.
- **Geohash prefix index** — is compact and easy to shard, but boundary effects require neighboring-cell checks.
- **Database spatial index** — PostGIS GiST, Elasticsearch geo queries, or MongoDB 2dsphere indexes provide maintained spatial services, with a query language and storage format chosen by the database.

## Related
- [Graph Representations and Graph Neural Network Data Structures](../04-graphs/01-graph-representations.md)
- [Range Queries: Segment Trees, Fenwick Trees, and Interval Trees](04-range-query-trees.md)
- [B-Trees, B+ Trees, and LSM-Trees](03-storage-engine-trees.md)
- [Computational Geometry Algorithms](../04a-computational-theory/04-computational-geometry.md)
