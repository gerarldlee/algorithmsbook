---
title: "Computational Geometry Algorithms: Convex Hull (Graham Scan, Jarvis March), Closest-Pair of Points, Line Segment Intersection"
weight: 4
toc: true
tabs: {sync: true}
---

## What it is
**Computational geometry** designs algorithms for points, lines, polygons, and related shapes. The core tasks here are wrapping points in a convex hull, finding the two nearest points, and deciding whether two line segments cross.

## How it works
The **convex hull** is the smallest convex set containing every point; for a finite point set that is the convex polygon formed by its outermost points. Graham scan chooses a lowest point as a pivot, sorts the others by angle around it, and removes clockwise turns. Jarvis March repeatedly chooses the most counterclockwise remaining point, which is a gift-wrapping walk.

The closest-pair algorithm sorts by x-coordinate, splits the set into two halves, recursively finds each half's closest pair, and keeps the better distance. Only points within that distance of the dividing line can form a better cross-half pair. Sorting each half by y-coordinate after recursion lets the merge and strip checks take linear time at that level. Comparing the next seven strip points is safe because a packing argument limits how many close points fit in a \(2\delta\)-wide region.

Two segments intersect when their endpoints alternate across the other segment's supporting line. Collinear endpoints and shared endpoints require a separate point-on-segment test using orientation and bounding boxes. A double-precision test also needs an application-level tolerance when measurements contain noise.

{{< tabs >}}
{{< tab name="Java" >}}
```java
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

public final class GeometryAlgorithms {
    private static double cross(double[] points, int a, int b, int c) {
        return (points[2 * b] - points[2 * a]) * (points[2 * c + 1] - points[2 * a + 1])
             - (points[2 * b + 1] - points[2 * a + 1]) * (points[2 * c] - points[2 * a]);
    }

    private static double distanceSquared(double[] points, int a, int b) {
        double x = points[2 * a] - points[2 * b];
        double y = points[2 * a + 1] - points[2 * b + 1];
        return x * x + y * y;
    }

    public static int[] grahamScan(double[] points) {
        int count = points.length / 2;
        if (count <= 2) {
            int[] identity = new int[count];
            for (int index = 0; index < count; index++) identity[index] = index;
            return identity;
        }
        Integer[] order = new Integer[count];
        for (int index = 0; index < count; index++) order[index] = index;
        Arrays.sort(order, Comparator.comparingDouble((int index) -> points[2 * index + 1]).thenComparingDouble(index -> points[2 * index]));
        int pivot = order[0];
        List<Integer> remaining = new ArrayList<>(Arrays.asList(order).subList(1, count));
        remaining.sort((left, right) -> {
            double turn = cross(points, pivot, left, right);
            if (turn != 0) return turn > 0 ? -1 : 1;
            return Double.compare(distanceSquared(points, pivot, left), distanceSquared(points, pivot, right));
        });
        int[] stack = new int[count];
        int size = 0;
        stack[size++] = pivot;
        for (int point : remaining) {
            while (size >= 2 && cross(points, stack[size - 2], stack[size - 1], point) <= 0) size--;
            stack[size++] = point;
        }
        return Arrays.copyOf(stack, size);
    }

    public static int[] jarvisMarch(double[] points) {
        int count = points.length / 2;
        if (count <= 2) return Arrays.copyOf(new int[count], count);
        int lowest = 0;
        for (int index = 1; index < count; index++) {
            if (points[2 * index + 1] < points[2 * lowest + 1] || (points[2 * index + 1] == points[2 * lowest + 1] && points[2 * index] < points[2 * lowest])) lowest = index;
        }
        int other = -1;
        boolean collinear = true;
        int farthest = lowest;
        double farthestDistance = 0;
        for (int index = 0; index < count; index++) {
            if (index != lowest) {
                if (other < 0) other = index;
                else if (cross(points, lowest, other, index) != 0) collinear = false;
                double distance = distanceSquared(points, lowest, index);
                if (distance > farthestDistance) {
                    farthestDistance = distance;
                    farthest = index;
                }
            }
        }
        if (collinear) return new int[] {lowest, farthest};
        int[] hull = new int[count];
        int current = lowest;
        int position;
        for (position = 0; position < count; position++) {
            hull[position] = current;
            int next = (current + 1) % count;
            for (int candidate = 0; candidate < count; candidate++) {
                if (cross(points, current, next, candidate) < 0) next = candidate;
            }
            current = next;
            if (current == lowest) break;
        }
        return Arrays.copyOf(hull, position + 1);
    }

    private static double closestRange(double[] points, int[] order, int low, int high, int[] best) {
        if (high - low <= 3) {
            double result = Double.POSITIVE_INFINITY;
            for (int left = low; left < high; left++) {
                for (int right = left + 1; right < high; right++) {
                    double value = distanceSquared(points, order[left], order[right]);
                    if (value < result) {
                        result = value;
                        best[0] = order[left];
                        best[1] = order[right];
                    }
                }
            }
            for (int index = low + 1; index < high; index++) {
                for (int other = low; other < index; other++) {
                    if (points[2 * order[other] + 1] > points[2 * order[index] + 1]) {
                        int value = order[other];
                        order[other] = order[index];
                        order[index] = value;
                    }
                }
            }
            return result;
        }
        int middle = (low + high) / 2;
        double dividingX = points[2 * order[middle]];
        int[] leftBest = {-1, -1};
        int[] rightBest = {-1, -1};
        double leftDistance = closestRange(points, order, low, middle, leftBest);
        double rightDistance = closestRange(points, order, middle, high, rightBest);
        int leftWinner = leftDistance <= rightDistance ? 0 : 1;
        double result = Math.min(leftDistance, rightDistance);
        int[] bestPair = leftWinner == 0 ? leftBest : rightBest;
        int[] merged = new int[high - low];
        int left = low;
        int right = middle;
        int output = low;
        while (left < middle || right < high) {
            if (right == high || (left < middle && points[2 * order[left] + 1] <= points[2 * order[right] + 1])) merged[output++] = order[left++];
            else merged[output++] = order[right++];
        }
        System.arraycopy(merged, 0, order, low, high - low);
        int[] strip = new int[high - low];
        int stripSize = 0;
        for (int index = low; index < high; index++) {
            if (Math.pow(points[2 * order[index]] - dividingX, 2) < result) strip[stripSize++] = order[index];
        }
        for (int leftIndex = 0; leftIndex < stripSize; leftIndex++) {
            for (int rightIndex = leftIndex + 1; rightIndex < stripSize && rightIndex <= leftIndex + 7; rightIndex++) {
                double value = distanceSquared(points, strip[leftIndex], strip[rightIndex]);
                if (value < result) {
                    result = value;
                    bestPair[0] = strip[leftIndex];
                    bestPair[1] = strip[rightIndex];
                }
            }
        }
        best[0] = bestPair[0];
        best[1] = bestPair[1];
        return result;
    }

    public static int[] closestPair(double[] points) {
        int count = points.length / 2;
        if (count < 2) return new int[0];
        int[] order = new int[count];
        for (int index = 0; index < count; index++) order[index] = index;
        Arrays.sort(order, Comparator.comparingDouble(index -> points[2 * index]).thenComparingDouble(index -> points[2 * index + 1]));
        int[] best = {-1, -1};
        closestRange(points, order, 0, count, best);
        return best;
    }

    private static boolean onSegment(double[] points, int point, int start, int end) {
        return cross(points, start, end, point) == 0
            && Math.min(points[2 * start], points[2 * end]) <= points[2 * point] && points[2 * point] <= Math.max(points[2 * start], points[2 * end])
            && Math.min(points[2 * start + 1], points[2 * end + 1]) <= points[2 * point + 1] && points[2 * point + 1] <= Math.max(points[2 * start + 1], points[2 * end + 1]);
    }

    public static boolean segmentsIntersect(double[] points, int a, int b, int c, int d) {
        double first = cross(points, a, b, c);
        double second = cross(points, a, b, d);
        double third = cross(points, c, d, a);
        double fourth = cross(points, c, d, b);
        if (((first > 0 && second < 0) || (first < 0 && second > 0)) && ((third > 0 && fourth < 0) || (third < 0 && fourth > 0))) return true;
        return (first == 0 && onSegment(points, c, a, b)) || (second == 0 && onSegment(points, d, a, b))
            || (third == 0 && onSegment(points, a, c, d)) || (fourth == 0 && onSegment(points, b, c, d));
    }
}
```

{{< /tab >}}
{{< tab name="C" >}}
```c
#include <math.h>
#include <stdbool.h>
#include <stdlib.h>

typedef enum {
    GEOMETRY_ALGORITHMS_Y_THEN_X,
    GEOMETRY_ALGORITHMS_ANGLE,
    GEOMETRY_ALGORITHMS_X_THEN_Y
} GeometryAlgorithmsSort;

double geometry_algorithms_cross(const double* points, int a, int b, int c) {
    return (points[2 * b] - points[2 * a]) * (points[2 * c + 1] - points[2 * a + 1])
         - (points[2 * b + 1] - points[2 * a + 1]) * (points[2 * c] - points[2 * a]);
}

static double geometry_algorithms_distance_squared(const double* points, int a, int b) {
    double x = points[2 * a] - points[2 * b];
    double y = points[2 * a + 1] - points[2 * b + 1];
    return x * x + y * y;
}

static int geometry_algorithms_compare(
    const double* points,
    int pivot,
    GeometryAlgorithmsSort order,
    int first,
    int second
) {
    if (order == GEOMETRY_ALGORITHMS_ANGLE) {
        double first_angle = atan2(points[2 * first + 1] - points[2 * pivot + 1], points[2 * first] - points[2 * pivot]);
        double second_angle = atan2(points[2 * second + 1] - points[2 * pivot + 1], points[2 * second] - points[2 * pivot]);
        if (first_angle != second_angle) return first_angle < second_angle ? -1 : 1;
        double first_distance = geometry_algorithms_distance_squared(points, pivot, first);
        double second_distance = geometry_algorithms_distance_squared(points, pivot, second);
        return first_distance < second_distance ? -1 : first_distance > second_distance;
    }
    if (order == GEOMETRY_ALGORITHMS_X_THEN_Y) {
        double first_x = points[2 * first];
        double second_x = points[2 * second];
        if (first_x != second_x) return first_x < second_x ? -1 : 1;
        double first_y = points[2 * first + 1];
        double second_y = points[2 * second + 1];
        return first_y < second_y ? -1 : first_y > second_y;
    }
    double first_y = points[2 * first + 1];
    double second_y = points[2 * second + 1];
    if (first_y != second_y) return first_y < second_y ? -1 : 1;
    double first_x = points[2 * first];
    double second_x = points[2 * second];
    return first_x < second_x ? -1 : first_x > second_x;
}

static void geometry_algorithms_swap(int* values, int left, int right) {
    int value = values[left];
    values[left] = values[right];
    values[right] = value;
}

static void geometry_algorithms_sift_down(
    const double* points,
    int pivot,
    GeometryAlgorithmsSort order,
    int* values,
    int start,
    int count,
    int root
) {
    while (true) {
        int child = root * 2 + 1;
        if (child >= count) return;
        if (child + 1 < count
            && geometry_algorithms_compare(points, pivot, order, values[child], values[child + 1]) < 0) child++;
        if (geometry_algorithms_compare(points, pivot, order, values[root], values[child]) >= 0) return;
        geometry_algorithms_swap(values, start + root, start + child);
        root = child;
    }
}

static void geometry_algorithms_sort(
    const double* points,
    int pivot,
    GeometryAlgorithmsSort order,
    int* values,
    int count
) {
    if (count < 2) return;
    for (int index = count / 2 - 1; index >= 0; index--) {
        geometry_algorithms_sift_down(points, pivot, order, values, 0, count, index);
    }
    for (int end = count - 1; end > 0; end--) {
        geometry_algorithms_swap(values, 0, end);
        geometry_algorithms_sift_down(points, pivot, order, values, 0, end, 0);
    }
}

int* geometry_algorithms_graham_scan(const double* points, int count, int* result_size) {
    int* order = malloc(count * sizeof(int));
    for (int index = 0; index < count; index++) order[index] = index;
    geometry_algorithms_sort(points, 0, GEOMETRY_ALGORITHMS_Y_THEN_X, order, count);
    if (count <= 2) {
        *result_size = count;
        return order;
    }
    int pivot = order[0];
    geometry_algorithms_sort(points, pivot, GEOMETRY_ALGORITHMS_ANGLE, order + 1, count - 1);
    int* hull = malloc(count * sizeof(int));
    int size = 0;
    hull[size++] = pivot;
    for (int index = 1; index < count; index++) {
        while (size >= 2 && geometry_algorithms_cross(points, hull[size - 2], hull[size - 1], order[index]) <= 0) size--;
        hull[size++] = order[index];
    }
    free(order);
    *result_size = size;
    return hull;
}

int* geometry_algorithms_jarvis_march(const double* points, int count, int* result_size) {
    if (count <= 2) {
        int* result = malloc(count * sizeof(int));
        for (int index = 0; index < count; index++) result[index] = index;
        *result_size = count;
        return result;
    }
    int lowest = 0;
    for (int index = 1; index < count; index++) {
        if (points[2 * index + 1] < points[2 * lowest + 1] || points[2 * index + 1] == points[2 * lowest + 1] && points[2 * index] < points[2 * lowest]) lowest = index;
    }
    int other = -1;
    bool collinear = true;
    int farthest = lowest;
    double farthest_distance = 0;
    for (int index = 0; index < count; index++) {
        if (index != lowest) {
            if (other < 0) {
                other = index;
            } else if (geometry_algorithms_cross(points, lowest, other, index) != 0) {
                collinear = false;
            }
            double distance = geometry_algorithms_distance_squared(points, lowest, index);
            if (distance > farthest_distance) {
                farthest_distance = distance;
                farthest = index;
            }
        }
    }
    if (collinear) {
        int* result = malloc(2 * sizeof(int));
        result[0] = lowest;
        result[1] = farthest;
        *result_size = 2;
        return result;
    }
    int* hull = malloc(count * sizeof(int));
    int current = lowest;
    int size;
    for (size = 0; size < count; size++) {
        hull[size] = current;
        int next = (current + 1) % count;
        for (int candidate = 0; candidate < count; candidate++) if (geometry_algorithms_cross(points, current, next, candidate) < 0) next = candidate;
        current = next;
        if (current == lowest) {
            size++;
            break;
        }
    }
    *result_size = size;
    return hull;
}

static double geometry_algorithms_closest_range(const double* points, int* order, int low, int high, int* best) {
    if (high - low <= 3) {
        double result = INFINITY;
        for (int left = low; left < high; left++) {
            for (int right = left + 1; right < high; right++) {
                double value = geometry_algorithms_distance_squared(points, order[left], order[right]);
                if (value < result) {
                    result = value;
                    best[0] = order[left];
                    best[1] = order[right];
                }
            }
        }
        int* sorted = malloc((size_t)(high - low) * sizeof(int));
        for (int index = low; index < high; index++) sorted[index - low] = order[index];
        geometry_algorithms_sort(points, 0, GEOMETRY_ALGORITHMS_Y_THEN_X, sorted, high - low);
        for (int index = low; index < high; index++) order[index] = sorted[index - low];
        free(sorted);
        return result;
    }
    int middle = (low + high) / 2;
    double dividing_x = points[2 * order[middle]];
    int left_best[2];
    int right_best[2];
    double left_distance = geometry_algorithms_closest_range(points, order, low, middle, left_best);
    double right_distance = geometry_algorithms_closest_range(points, order, middle, high, right_best);
    double result = left_distance <= right_distance ? left_distance : right_distance;
    if (left_distance <= right_distance) {
        best[0] = left_best[0];
        best[1] = left_best[1];
    } else {
        best[0] = right_best[0];
        best[1] = right_best[1];
    }
    int* merged = malloc((high - low) * sizeof(int));
    int left = low;
    int right = middle;
    int output = 0;
    while (left < middle || right < high) {
        if (right == high || left < middle && points[2 * order[left] + 1] <= points[2 * order[right] + 1]) merged[output++] = order[left++];
        else merged[output++] = order[right++];
    }
    for (int index = 0; index < output; index++) order[low + index] = merged[index];
    free(merged);
    int* strip = malloc((high - low) * sizeof(int));
    int strip_size = 0;
    for (int index = low; index < high; index++) {
        double dx = points[2 * order[index]] - dividing_x;
        if (dx * dx < result) strip[strip_size++] = order[index];
    }
    for (int left = 0; left < strip_size; left++) {
        for (int right = left + 1; right < strip_size && right <= left + 7; right++) {
            double value = geometry_algorithms_distance_squared(points, strip[left], strip[right]);
            if (value < result) {
                result = value;
                best[0] = strip[left];
                best[1] = strip[right];
            }
        }
    }
    free(strip);
    return result;
}

int* geometry_algorithms_closest_pair(const double* points, int count) {
    if (count < 2) return malloc(0);
    int* order = malloc(count * sizeof(int));
    for (int index = 0; index < count; index++) order[index] = index;
    geometry_algorithms_sort(points, 0, GEOMETRY_ALGORITHMS_X_THEN_Y, order, count);
    int* best = malloc(2 * sizeof(int));
    geometry_algorithms_closest_range(points, order, 0, count, best);
    free(order);
    return best;
}

static bool geometry_algorithms_on_segment(const double* points, int point, int start, int end) {
    return geometry_algorithms_cross(points, start, end, point) == 0
        && fmin(points[2 * start], points[2 * end]) <= points[2 * point] && points[2 * point] <= fmax(points[2 * start], points[2 * end])
        && fmin(points[2 * start + 1], points[2 * end + 1]) <= points[2 * point + 1] && points[2 * point + 1] <= fmax(points[2 * start + 1], points[2 * end + 1]);
}

bool geometry_algorithms_segments_intersect(const double* points, int a, int b, int c, int d) {
    double first = geometry_algorithms_cross(points, a, b, c);
    double second = geometry_algorithms_cross(points, a, b, d);
    double third = geometry_algorithms_cross(points, c, d, a);
    double fourth = geometry_algorithms_cross(points, c, d, b);
    if ((first < 0 && second > 0 || first > 0 && second < 0)
        && (third < 0 && fourth > 0 || third > 0 && fourth < 0)) return true;
    return (first == 0 && geometry_algorithms_on_segment(points, c, a, b)) || (second == 0 && geometry_algorithms_on_segment(points, d, a, b))
        || (third == 0 && geometry_algorithms_on_segment(points, a, c, d)) || (fourth == 0 && geometry_algorithms_on_segment(points, b, c, d));
}
```

{{< /tab >}}
{{< tab name="Python" >}}
```python
import math


class GeometryAlgorithms:
    @staticmethod
    def _cross(points: list[float], a: int, b: int, c: int) -> float:
        return (points[2 * b] - points[2 * a]) * (points[2 * c + 1] - points[2 * a + 1]) - (points[2 * b + 1] - points[2 * a + 1]) * (points[2 * c] - points[2 * a])

    @staticmethod
    def _distance_squared(points: list[float], a: int, b: int) -> float:
        return (points[2 * a] - points[2 * b]) ** 2 + (points[2 * a + 1] - points[2 * b + 1]) ** 2

    @staticmethod
    def graham_scan(points: list[float]) -> list[int]:
        count = len(points) // 2
        if count <= 2:
            return list(range(count))
        order = sorted(range(count), key=lambda index: (points[2 * index + 1], points[2 * index]))
        pivot = order[0]
        remaining = sorted(order[1:], key=lambda index: (math.atan2(points[2 * index + 1] - points[2 * pivot + 1], points[2 * index] - points[2 * pivot]), GeometryAlgorithms._distance_squared(points, pivot, index)))
        stack = [pivot]
        for point in remaining:
            while len(stack) >= 2 and GeometryAlgorithms._cross(points, stack[-2], stack[-1], point) <= 0:
                stack.pop()
            stack.append(point)
        return stack

    @staticmethod
    def jarvis_march(points: list[float]) -> list[int]:
        count = len(points) // 2
        if count <= 2:
            return list(range(count))
        lowest = min(range(count), key=lambda index: (points[2 * index + 1], points[2 * index]))
        other = next(index for index in range(count) if index != lowest)
        collinear = all(GeometryAlgorithms._cross(points, lowest, other, index) == 0 for index in range(count) if index not in (lowest, other))
        if collinear:
            farthest = max((index for index in range(count) if index != lowest), key=lambda index: GeometryAlgorithms._distance_squared(points, lowest, index))
            return [lowest, farthest]
        hull = []
        current = lowest
        for _ in range(count):
            hull.append(current)
            following = (current + 1) % count
            for candidate in range(count):
                if GeometryAlgorithms._cross(points, current, following, candidate) < 0:
                    following = candidate
            current = following
            if current == lowest:
                break
        return hull

    @staticmethod
    def _closest_range(points: list[float], order: list[int], low: int, high: int) -> tuple[float, int, int]:
        if high - low <= 3:
            candidates = [(GeometryAlgorithms._distance_squared(points, order[left], order[right]), order[left], order[right]) for left in range(low, high) for right in range(left + 1, high)]
            best = min(candidates, default=(math.inf, -1, -1))
            order[low:high] = sorted(order[low:high], key=lambda index: points[2 * index + 1])
            return best
        middle = (low + high) // 2
        dividing_x = points[2 * order[middle]]
        left = GeometryAlgorithms._closest_range(points, order, low, middle)
        right = GeometryAlgorithms._closest_range(points, order, middle, high)
        best = min(left, right)
        merged = sorted(order[low:high], key=lambda index: (points[2 * index + 1], points[2 * index]))
        order[low:high] = merged
        strip = [index for index in merged if (points[2 * index] - dividing_x) ** 2 < best[0]]
        for left_index, first in enumerate(strip):
            for second in strip[left_index + 1:left_index + 8]:
                value = GeometryAlgorithms._distance_squared(points, first, second)
                if value < best[0]:
                    best = (value, first, second)
        return best

    @staticmethod
    def closest_pair(points: list[float]) -> list[int]:
        count = len(points) // 2
        if count < 2:
            return []
        order = sorted(range(count), key=lambda index: (points[2 * index], points[2 * index + 1]))
        _, first, second = GeometryAlgorithms._closest_range(points, order, 0, count)
        return [first, second]

    @staticmethod
    def _on_segment(points: list[float], point: int, start: int, end: int) -> bool:
        return GeometryAlgorithms._cross(points, start, end, point) == 0 and min(points[2 * start], points[2 * end]) <= points[2 * point] <= max(points[2 * start], points[2 * end]) and min(points[2 * start + 1], points[2 * end + 1]) <= points[2 * point + 1] <= max(points[2 * start + 1], points[2 * end + 1])

    @staticmethod
    def segments_intersect(points: list[float], a: int, b: int, c: int, d: int) -> bool:
        first = GeometryAlgorithms._cross(points, a, b, c)
        second = GeometryAlgorithms._cross(points, a, b, d)
        third = GeometryAlgorithms._cross(points, c, d, a)
        fourth = GeometryAlgorithms._cross(points, c, d, b)
        if first * second < 0 and third * fourth < 0:
            return True
        return (first == 0 and GeometryAlgorithms._on_segment(points, c, a, b)) or (second == 0 and GeometryAlgorithms._on_segment(points, d, a, b)) or (third == 0 and GeometryAlgorithms._on_segment(points, a, c, d)) or (fourth == 0 and GeometryAlgorithms._on_segment(points, b, c, d))
```

{{< /tab >}}
{{< tab name="Rust" >}}
```rust
pub struct GeometryAlgorithms;

impl GeometryAlgorithms {
    fn cross(points: &[f64], a: usize, b: usize, c: usize) -> f64 {
        (points[2 * b] - points[2 * a]) * (points[2 * c + 1] - points[2 * a + 1])
            - (points[2 * b + 1] - points[2 * a + 1]) * (points[2 * c] - points[2 * a])
    }

    fn distance_squared(points: &[f64], a: usize, b: usize) -> f64 {
        (points[2 * a] - points[2 * b]).powi(2) + (points[2 * a + 1] - points[2 * b + 1]).powi(2)
    }

    pub fn graham_scan(points: &[f64]) -> Vec<usize> {
        let mut order: Vec<usize> = (0..points.len() / 2).collect();
        if order.len() <= 2 {
            return order;
        }
        order.sort_by(|left, right| {
            (points[2 * *left + 1], points[2 * *left])
                .partial_cmp(&(points[2 * *right + 1], points[2 * *right]))
                .unwrap()
        });
        let pivot = order[0];
        order[1..].sort_by(|left, right| {
            let left_angle = (points[2 * *left + 1] - points[2 * pivot + 1]).atan2(points[2 * *left] - points[2 * pivot]);
            let right_angle = (points[2 * *right + 1] - points[2 * pivot + 1]).atan2(points[2 * *right] - points[2 * pivot]);
            left_angle
                .partial_cmp(&right_angle)
                .unwrap()
                .then_with(|| Self::distance_squared(points, *left, pivot).partial_cmp(&Self::distance_squared(points, *right, pivot)).unwrap())
        });
        let mut stack = vec![pivot];
        for point in order[1..].iter().copied() {
            while stack.len() >= 2 && Self::cross(points, stack[stack.len() - 2], stack[stack.len() - 1], point) <= 0.0 {
                stack.pop();
            }
            stack.push(point);
        }
        stack
    }

    pub fn jarvis_march(points: &[f64]) -> Vec<usize> {
        let count = points.len() / 2;
        if count <= 2 {
            return (0..count).collect();
        }
        let mut lowest = 0;
        for index in 1..count {
            if (points[2 * index + 1], points[2 * index]) < (points[2 * lowest + 1], points[2 * lowest]) {
                lowest = index;
            }
        }
        let other = (0..count).find(|index| *index != lowest).unwrap();
        let collinear = (0..count)
            .filter(|index| *index != lowest && *index != other)
            .all(|index| Self::cross(points, lowest, other, index) == 0.0);
        if collinear {
            let farthest = (0..count)
                .filter(|index| *index != lowest)
                .max_by(|left, right| {
                    Self::distance_squared(points, lowest, *left)
                        .partial_cmp(&Self::distance_squared(points, lowest, *right))
                        .unwrap()
                })
                .unwrap();
            return vec![lowest, farthest];
        }
        let mut hull = Vec::with_capacity(count);
        let mut current = lowest;
        for _ in 0..count {
            hull.push(current);
            let mut next = (current + 1) % count;
            for candidate in 0..count {
                if Self::cross(points, current, next, candidate) < 0.0 {
                    next = candidate;
                }
            }
            current = next;
            if current == lowest {
                break;
            }
        }
        hull
    }

    fn closest_range(points: &[f64], order: &mut [usize]) -> (f64, usize, usize) {
        if order.len() <= 3 {
            let mut best = (f64::INFINITY, usize::MAX, usize::MAX);
            for left in 0..order.len() {
                for right in left + 1..order.len() {
                    let value = Self::distance_squared(points, order[left], order[right]);
                    if value < best.0 {
                        best = (value, order[left], order[right]);
                    }
                }
            }
            order.sort_by(|left, right| points[2 * *left + 1].partial_cmp(&points[2 * *right + 1]).unwrap());
            return best;
        }
        let middle = order.len() / 2;
        let dividing_x = points[2 * order[middle]];
        let mut left = order[..middle].to_vec();
        let mut right = order[middle..].to_vec();
        let left_best = Self::closest_range(points, &mut left);
        let right_best = Self::closest_range(points, &mut right);
        let mut best = if right_best.0 < left_best.0 { right_best } else { left_best };
        let mut merged = Vec::with_capacity(left.len() + right.len());
        let mut left_index = 0;
        let mut right_index = 0;
        while left_index < left.len() || right_index < right.len() {
            if right_index == right.len()
                || (left_index < left.len()
                    && (points[2 * left[left_index] + 1], points[2 * left[left_index]])
                        <= (points[2 * right[right_index] + 1], points[2 * right[right_index]]))
            {
                merged.push(left[left_index]);
                left_index += 1;
            } else {
                merged.push(right[right_index]);
                right_index += 1;
            }
        }
        let strip: Vec<usize> = merged
            .iter()
            .copied()
            .filter(|index| (points[2 * *index] - dividing_x).powi(2) < best.0)
            .collect();
        for left_index in 0..strip.len() {
            for second in strip.iter().skip(left_index + 1).take(7) {
                let value = Self::distance_squared(points, strip[left_index], *second);
                if value < best.0 {
                    best = (value, strip[left_index], *second);
                }
            }
        }
        order.copy_from_slice(&merged);
        best
    }

    pub fn closest_pair(points: &[f64]) -> Vec<usize> {
        let mut order: Vec<usize> = (0..points.len() / 2).collect();
        order.sort_by(|left, right| {
            (points[2 * *left], points[2 * *left + 1])
                .partial_cmp(&(points[2 * *right], points[2 * *right + 1]))
                .unwrap()
        });
        if order.len() < 2 {
            return Vec::new();
        }
        let (_, first, second) = Self::closest_range(points, &mut order);
        vec![first, second]
    }

    fn on_segment(points: &[f64], point: usize, start: usize, end: usize) -> bool {
        Self::cross(points, start, end, point) == 0.0
            && points[2 * start].min(points[2 * end]) <= points[2 * point]
            && points[2 * point] <= points[2 * start].max(points[2 * end])
            && points[2 * start + 1].min(points[2 * end + 1]) <= points[2 * point + 1]
            && points[2 * point + 1] <= points[2 * start + 1].max(points[2 * end + 1])
    }

    pub fn segments_intersect(points: &[f64], a: usize, b: usize, c: usize, d: usize) -> bool {
        let first = Self::cross(points, a, b, c);
        let second = Self::cross(points, a, b, d);
        let third = Self::cross(points, c, d, a);
        let fourth = Self::cross(points, c, d, b);
        if first * second < 0.0 && third * fourth < 0.0 {
            return true;
        }
        (first == 0.0 && Self::on_segment(points, c, a, b))
            || (second == 0.0 && Self::on_segment(points, d, a, b))
            || (third == 0.0 && Self::on_segment(points, a, c, d))
            || (fourth == 0.0 && Self::on_segment(points, b, c, d))
    }
}
```

{{< /tab >}}
{{< tab name="TypeScript" >}}
```typescript
export class GeometryAlgorithms {
  private static cross(points: number[], a: number, b: number, c: number): number {
    return (points[2 * b] - points[2 * a]) * (points[2 * c + 1] - points[2 * a + 1]) - (points[2 * b + 1] - points[2 * a + 1]) * (points[2 * c] - points[2 * a]);
  }

  private static distanceSquared(points: number[], a: number, b: number): number {
    return (points[2 * a] - points[2 * b]) ** 2 + (points[2 * a + 1] - points[2 * b + 1]) ** 2;
  }

  static grahamScan(points: number[]): number[] {
    const count = Math.floor(points.length / 2);
    if (count <= 2) return Array.from({ length: count }, (_, index) => index);
    let order = Array.from({ length: count }, (_, index) => index).sort((left, right) => points[2 * left + 1] - points[2 * right + 1] || points[2 * left] - points[2 * right]);
    const pivot = order[0];
    order = order.slice(1).sort((left, right) => {
      const leftAngle = Math.atan2(points[2 * left + 1] - points[2 * pivot + 1], points[2 * left] - points[2 * pivot]);
      const rightAngle = Math.atan2(points[2 * right + 1] - points[2 * pivot + 1], points[2 * right] - points[2 * pivot]);
      return leftAngle - rightAngle || GeometryAlgorithms.distanceSquared(points, pivot, left) - GeometryAlgorithms.distanceSquared(points, pivot, right);
    });
    const stack = [pivot];
    for (const point of order) {
      while (stack.length >= 2 && GeometryAlgorithms.cross(points, stack[stack.length - 2], stack[stack.length - 1], point) <= 0) stack.pop();
      stack.push(point);
    }
    return stack;
  }

  static jarvisMarch(points: number[]): number[] {
    const count = Math.floor(points.length / 2);
    if (count <= 2) return Array.from({ length: count }, (_, index) => index);
    let lowest = 0;
    for (let index = 1; index < count; index++) if (points[2 * index + 1] < points[2 * lowest + 1] || points[2 * index + 1] === points[2 * lowest + 1] && points[2 * index] < points[2 * lowest]) lowest = index;
    const other = Array.from({ length: count }, (_, index) => index).find((index) => index !== lowest)!;
    const collinear = Array.from({ length: count }, (_, index) => index).every((index) => index === lowest || index === other || GeometryAlgorithms.cross(points, lowest, other, index) === 0);
    if (collinear) {
      const farthest = Array.from({ length: count }, (_, index) => index).filter((index) => index !== lowest).reduce((best, index) => GeometryAlgorithms.distanceSquared(points, lowest, index) > GeometryAlgorithms.distanceSquared(points, lowest, best) ? index : best, other);
      return [lowest, farthest];
    }
    const hull: number[] = [];
    let current = lowest;
    for (let step = 0; step < count; step++) {
      hull.push(current);
      let next = (current + 1) % count;
      for (let candidate = 0; candidate < count; candidate++) if (GeometryAlgorithms.cross(points, current, next, candidate) < 0) next = candidate;
      current = next;
      if (current === lowest) break;
    }
    return hull;
  }

  private static closestRange(points: number[], order: number[], low: number, high: number): [number, number, number] {
    if (high - low <= 3) {
      let best: [number, number, number] = [Number.MAX_VALUE, -1, -1];
      for (let left = low; left < high; left++) for (let right = left + 1; right < high; right++) {
        const value = GeometryAlgorithms.distanceSquared(points, order[left], order[right]);
        if (value < best[0]) best = [value, order[left], order[right]];
      }
      order.splice(low, high - low, ...order.slice(low, high).sort((left, right) => points[2 * left + 1] - points[2 * right + 1]));
      return best;
    }
    const middle = Math.floor((low + high) / 2);
    const dividingX = points[2 * order[middle]];
    const left = GeometryAlgorithms.closestRange(points, order, low, middle);
    const right = GeometryAlgorithms.closestRange(points, order, middle, high);
    let best = left[0] <= right[0] ? left : right;
    const merged = [...order.slice(low, middle), ...order.slice(middle, high)].sort((first, second) => points[2 * first + 1] - points[2 * second + 1]);
    order.splice(low, high - low, ...merged);
    const strip = merged.filter(index => (points[2 * index] - dividingX) ** 2 < best[0]);
    for (let left = 0; left < strip.length; left++) for (let right = left + 1; right < strip.length && right <= left + 7; right++) {
      const value = GeometryAlgorithms.distanceSquared(points, strip[left], strip[right]);
      if (value < best[0]) best = [value, strip[left], strip[right]];
    }
    return best;
  }

  static closestPair(points: number[]): number[] {
    const count = Math.floor(points.length / 2);
    if (count < 2) return [];
    const order = Array.from({ length: count }, (_, index) => index).sort((left, right) => points[2 * left] - points[2 * right] || points[2 * left + 1] - points[2 * right + 1]);
    const [, first, second] = GeometryAlgorithms.closestRange(points, order, 0, count);
    return [first, second];
  }

  private static onSegment(points: number[], point: number, start: number, end: number): boolean {
    return GeometryAlgorithms.cross(points, start, end, point) === 0 && Math.min(points[2 * start], points[2 * end]) <= points[2 * point] && points[2 * point] <= Math.max(points[2 * start], points[2 * end]) && Math.min(points[2 * start + 1], points[2 * end + 1]) <= points[2 * point + 1] && points[2 * point + 1] <= Math.max(points[2 * start + 1], points[2 * end + 1]);
  }

  static segmentsIntersect(points: number[], a: number, b: number, c: number, d: number): boolean {
    const first = GeometryAlgorithms.cross(points, a, b, c);
    const second = GeometryAlgorithms.cross(points, a, b, d);
    const third = GeometryAlgorithms.cross(points, c, d, a);
    const fourth = GeometryAlgorithms.cross(points, c, d, b);
    if (first * second < 0 && third * fourth < 0) return true;
    return (first === 0 && GeometryAlgorithms.onSegment(points, c, a, b)) || (second === 0 && GeometryAlgorithms.onSegment(points, d, a, b)) || (third === 0 && GeometryAlgorithms.onSegment(points, a, c, d)) || (fourth === 0 && GeometryAlgorithms.onSegment(points, b, c, d));
  }
}
```

{{< /tab >}}
{{< tab name="Go" >}}
```go
package geometry

import (
	"math"
	"sort"
)

type GeometryAlgorithms struct{}

func geometryAlgorithmsCross(points []float64, a, b, c int) float64 {
	return (points[2*b]-points[2*a])*(points[2*c+1]-points[2*a+1]) - (points[2*b+1]-points[2*a+1])*(points[2*c]-points[2*a])
}

func geometryAlgorithmsDistanceSquared(points []float64, a, b int) float64 {
	x := points[2*a] - points[2*b]
	y := points[2*a+1] - points[2*b+1]
	return x*x + y*y
}

func (GeometryAlgorithms) GrahamScan(points []float64) []int {
	count := len(points) / 2
	order := make([]int, count)
	for index := range order {
		order[index] = index
	}
	if count <= 2 {
		return order
	}
	sort.Slice(order, func(left, right int) bool {
		if points[2*order[left]+1] == points[2*order[right]+1] {
			return points[2*order[left]] < points[2*order[right]]
		}
		return points[2*order[left]+1] < points[2*order[right]+1]
	})
	pivot := order[0]
	remaining := append([]int(nil), order[1:]...)
	sort.Slice(remaining, func(left, right int) bool {
		turn := geometryAlgorithmsCross(points, pivot, remaining[left], remaining[right])
		if turn != 0 {
			return turn > 0
		}
		return geometryAlgorithmsDistanceSquared(points, pivot, remaining[left]) < geometryAlgorithmsDistanceSquared(points, pivot, remaining[right])
	})
	stack := []int{pivot}
	for _, point := range remaining {
		for len(stack) >= 2 && geometryAlgorithmsCross(points, stack[len(stack)-2], stack[len(stack)-1], point) <= 0 {
			stack = stack[:len(stack)-1]
		}
		stack = append(stack, point)
	}
	return stack
}

func (GeometryAlgorithms) JarvisMarch(points []float64) []int {
	count := len(points) / 2
	if count <= 2 {
		order := make([]int, count)
		for index := range order {
			order[index] = index
		}
		return order
	}
	lowest := 0
	for index := 1; index < count; index++ {
		if points[2*index+1] < points[2*lowest+1] || points[2*index+1] == points[2*lowest+1] && points[2*index] < points[2*lowest] {
			lowest = index
		}
	}
	other := 0
	if other == lowest {
		other = 1
	}
	collinear := true
	farthest := lowest
	farthestDistance := 0.0
	for index := 0; index < count; index++ {
		if index == lowest {
			continue
		}
		if index != other && geometryAlgorithmsCross(points, lowest, other, index) != 0 {
			collinear = false
		}
		distance := geometryAlgorithmsDistanceSquared(points, lowest, index)
		if distance > farthestDistance {
			farthestDistance = distance
			farthest = index
		}
	}
	if collinear {
		return []int{lowest, farthest}
	}
	hull := make([]int, 0, count)
	current := lowest
	for step := 0; step < count; step++ {
		hull = append(hull, current)
		next := (current + 1) % count
		for candidate := 0; candidate < count; candidate++ {
			if geometryAlgorithmsCross(points, current, next, candidate) < 0 {
				next = candidate
			}
		}
		current = next
		if current == lowest {
			break
		}
	}
	return hull
}

func (GeometryAlgorithms) closestRange(points []float64, order []int) (float64, int, int) {
	if len(order) <= 3 {
		bestDistance := math.Inf(1)
		first, second := -1, -1
		for left := 0; left < len(order); left++ {
			for right := left + 1; right < len(order); right++ {
				value := geometryAlgorithmsDistanceSquared(points, order[left], order[right])
				if value < bestDistance {
					bestDistance, first, second = value, order[left], order[right]
				}
			}
		}
		sort.SliceStable(order, func(left, right int) bool { return points[2*order[left]+1] < points[2*order[right]+1] })
		return bestDistance, first, second
	}
	middle := len(order) / 2
	dividingX := points[2*order[middle]]
	leftDistance, leftFirst, leftSecond := GeometryAlgorithms{}.closestRange(points, order[:middle])
	rightDistance, rightFirst, rightSecond := GeometryAlgorithms{}.closestRange(points, order[middle:])
	bestDistance, first, second := leftDistance, leftFirst, leftSecond
	if rightDistance < bestDistance {
		bestDistance, first, second = rightDistance, rightFirst, rightSecond
	}
	merged := append(append([]int(nil), order[:middle]...), order[middle:]...)
	sort.SliceStable(merged, func(left, right int) bool { return points[2*merged[left]+1] < points[2*merged[right]+1] })
	copy(order, merged)
	strip := make([]int, 0, len(merged))
	for _, index := range merged {
		if (points[2*index]-dividingX)*(points[2*index]-dividingX) < bestDistance {
			strip = append(strip, index)
		}
	}
	for left := 0; left < len(strip); left++ {
		for right := left + 1; right < len(strip) && right <= left+7; right++ {
			value := geometryAlgorithmsDistanceSquared(points, strip[left], strip[right])
			if value < bestDistance {
				bestDistance, first, second = value, strip[left], strip[right]
			}
		}
	}
	return bestDistance, first, second
}

func (GeometryAlgorithms) ClosestPair(points []float64) []int {
	count := len(points) / 2
	if count < 2 {
		return []int{}
	}
	order := make([]int, count)
	for index := range order {
		order[index] = index
	}
	sort.SliceStable(order, func(left, right int) bool {
		if points[2*order[left]] == points[2*order[right]] {
			return points[2*order[left]+1] < points[2*order[right]+1]
		}
		return points[2*order[left]] < points[2*order[right]]
	})
	_, first, second := GeometryAlgorithms{}.closestRange(points, order)
	return []int{first, second}
}

func geometryAlgorithmsOnSegment(points []float64, point, start, end int) bool {
	return geometryAlgorithmsCross(points, start, end, point) == 0 && math.Min(points[2*start], points[2*end]) <= points[2*point] && points[2*point] <= math.Max(points[2*start], points[2*end]) && math.Min(points[2*start+1], points[2*end+1]) <= points[2*point+1] && points[2*point+1] <= math.Max(points[2*start+1], points[2*end+1])
}

func (GeometryAlgorithms) SegmentsIntersect(points []float64, a, b, c, d int) bool {
	first := geometryAlgorithmsCross(points, a, b, c)
	second := geometryAlgorithmsCross(points, a, b, d)
	third := geometryAlgorithmsCross(points, c, d, a)
	fourth := geometryAlgorithmsCross(points, c, d, b)
	if first*second < 0 && third*fourth < 0 {
		return true
	}
	return first == 0 && geometryAlgorithmsOnSegment(points, c, a, b) || second == 0 && geometryAlgorithmsOnSegment(points, d, a, b) || third == 0 && geometryAlgorithmsOnSegment(points, a, c, d) || fourth == 0 && geometryAlgorithmsOnSegment(points, b, c, d)
}
{{< /tab >}}
{{< /tabs >}}

## Complexity
For \(n\) points and hull size \(h\):

| Operation | Time | Extra space |
| --- | --- | --- |
| Graham scan | O(n log n) | O(n) |
| Jarvis March | O(nh) | O(h) |
| Closest pair | O(n log n) | O(n) |
| Segment intersection query | O(1) | O(1) |

## When to use
- You need the boundary of the smallest convex shape that contains a point set.
- You need a simple online hull method when the output itself may be large.
- You need the nearest pair among many two-dimensional points.
- You need collision, crossing, or boundary checks for line segments.

## Alternatives
- **Andrew's monotone chain** — computes the same convex hull in O(n log n) with simpler code when angular sorting is unnecessary.
- **Divide-and-conquer hull merging** — finds upper and lower chains separately and merges them in O(n log n).
- **Sweep-line closest pair** — also runs in O(n log n), integrates naturally with sweep events, and needs careful handling of equal coordinates.
- **Spatial indexes** — accelerate many nearby-object or intersection queries after a bulk algorithm has produced a global result.

## Related
- [Computational Complexity Theory](01-complexity-theory.md)
- [Randomized & Approximation Algorithms](02-randomized-approximation-algorithms.md)
- [Spatial Indexing & Geospatial Data Structures](../02-search-trees/07-spatial-indexing.md)
