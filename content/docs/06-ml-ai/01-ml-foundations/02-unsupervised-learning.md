---
title: "Unsupervised Learning: K-Means, Hierarchical Clustering, Principal Component Analysis (PCA)"
weight: 2
toc: true
---

## What it is
Unsupervised learning is the branch of machine learning that discovers structure in data without target labels. It groups related examples, identifies density, or finds lower-dimensional representations that preserve useful properties of the input distribution.

## How it works
An unsupervised pipeline chooses whether the output is a partition, a hierarchy, or a transformed representation, then applies an objective appropriate to that output. The result still requires evaluation: a visually plausible cluster is not evidence of useful structure. Scikit-learn provides standard implementations of these methods, FAISS provides optimized large-scale clustering and nearest-neighbor search, and PyTorch provides tensor primitives for custom implementations. Domain labels and downstream tasks provide external validation when available.

```yaml
pipeline:
  input:
    features: "numeric feature matrix"
    preprocessing: ["impute missing values", "scale sensitive features"]
  representations:
    k_means:
      parameters: {k: 8, initialization: "k-means++", restarts: 10}
      objective: "within-cluster sum of squares"
    hierarchical:
      parameters: {linkage: "ward", criterion: "increase in within-cluster sum of squares"}
      output: "dendrogram"
    pca:
      parameters: {components: 2, standardization: true}
      objective: "maximum retained variance"
  evaluation:
    internal: ["silhouette score", "Davies-Bouldin index"]
    external: ["adjusted Rand index", "normalized mutual information"]
    downstream: "cluster quality on a held-out task"
```

**K-means** alternates between assigning each point to its nearest centroid and replacing each centroid with the mean of its assigned points. K-means++ initialization reduces the chance of starting with distant centroids, and multiple restarts reduce sensitivity to the initial assignment. The method requires `k` and favors compact, similarly sized clusters.

**Hierarchical clustering** produces a tree of merges or splits. Agglomerative clustering starts with one cluster per observation and merges clusters according to a **linkage** rule such as single, complete, average, or Ward linkage. Ward is a linkage criterion rather than a standalone vector-distance metric: it chooses the merge that minimizes the increase in the within-cluster sum of squared Euclidean deviations. Divisive clustering starts with one cluster and splits it using a chosen criterion. A dendrogram can be cut at different levels to obtain different cluster counts without rerunning the fit.

**Principal component analysis (PCA)** centers the data and finds directions of maximum variance. The first principal component is the leading eigenvector of the covariance matrix; later components are orthogonal directions with smaller eigenvalues. PCA can rotate the data into a lower-dimensional coordinate system, or project it onto a chosen number of components while retaining as much variance as the linear model permits. **DBSCAN** is a density-based alternative that groups points connected through epsilon neighborhoods; points with insufficient neighbors are noise unless they are density-reachable border points of a core cluster.

## Complexity
Let `n` be the number of examples, `d` the number of features, `k` the number of clusters, and `I` the number of K-means iterations.

| Operation | Representative time | Additional space |
| --- | --- | --- |
| K-means iteration | O(nkd) | O(n + kd) for assignments and centroid values |
| K-means fit | O(Inkd) | O(n + kd) for assignments and centroid values, excluding the O(nd) stored input |
| Naive agglomerative hierarchy | O(n^3 d) when pairwise distances are recomputed after merges | O(n^2) if pairwise distances are cached |
| PCA with a dense covariance matrix | O(nd^2 + d^3) | O(d^2) for the covariance matrix and eigenvectors, excluding the input |
| PCA projection to `q` components | O(ndq) | O(nq) for materialized projected values or O(1) per row when streamed |
| DBSCAN with a fixed-dimensional spatial tree | O(n log n + R) expected under bounded-dimension query assumptions, where `R` is the number of returned neighbor pairs; dense neighborhoods can reach O(n²) | O(n + R) for labels, returned neighbors, and queue state |

## When to use
- You need to segment customers or observations and a fixed number of compact groups is an acceptable assumption.
- You need a hierarchy so you can inspect cluster merges and choose a level after fitting.
- You need to detect irregular clusters and noise in spatial or density-based data.
- You need deterministic, linear dimensionality reduction for visualization or downstream modeling.
- You have no labels but can validate the representation with a downstream task or domain expert review.

## Alternatives
- **Gaussian mixture models** — provide soft cluster probabilities and elliptical cluster shapes, but require an EM procedure and a component-count choice.
- **t-SNE and UMAP** — reveal local non-linear neighborhoods in visualizations, but neighborhood parameters and random initialization affect the display and they are not reconstruction models.
- **Autoencoders** — learn non-linear compressed representations, but need architecture design, training, and a reconstruction or downstream objective.

## Related
- [Supervised Learning](01-supervised-learning.md)
- [ML System Design](../02-mlops/01-ml-system-design.md)
- [Vector Databases](../03-genai/01-vector-databases.md)
