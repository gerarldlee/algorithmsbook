---
title: "Growth of Algorithm"
weight: 3
---


We will not deal with the academic definition of big-\(O\), big-\(\Theta\), and big-\(\Omega\).  They are not practical for us.  Instead we will deal with the best case, and worse case runtime of a given *input*.

For the sake of completeness, the asymptotic notation are the bounding of a function runtime.

- \(O\) means an upper bound.  The usual upper bounds of a given function with N input is \(O(N \cdot log(N))\), \(O(N^2)\), \(O(N^3)\)
- \(\Omega\) means a lower bound.  The usual lower bounds of a given function with N input is \(\Omega(log(N))\), \(\Omega(1)\)
- \(\Theta\) means when an upper bound is equal to the lower bound.  The usual equivalence is \(\Theta(N)\)
- A best case runtime of a given *input* scenario may also have an upper bound, and a lower bound.  The same is true for the worse case input scenario.

Given a bubble sort algorithm:

```java
for (int j=0; j<array.length-1; j++) {
	for (int i=1; i<array.length-j-1; i++) {
		if (array[i] > array[j]) {
			int tmp = array[i];
			array[i] = array[j];
			array[j] = tmp;
		}
	}
}
```

The best case is when the input array is already sorted in ascending order.  This means that the algorithm will just go through all elements in the array and will do nothing, until all the array elements has been visited.

The worse case is when the array is sorted in descending order.
