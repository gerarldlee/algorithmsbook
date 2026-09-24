---
title: "Unsupervised Learning"
weight: 2
toc: true
---

## What it is
Unsupervised learning finds structure — clusters, densities, or lower-dimensional representations — in unlabeled data. It has no target labels; the algorithm discovers patterns directly from the input distribution.

## How it works
- **k-means** alternates between assigning each point to the nearest centroid and recomputing centroids as cluster means, minimizing within-cluster sum of squares. It requires choosing `k` in advance.
- **Hierarchical clustering** builds a dendrogram by agglomerative (bottom-up) or divisive (top-down) merging/splitting of clusters, using a linkage criterion (single, complete, average).
- **DBSCAN** groups points that are densely connected via ε-neighborhoods, marking sparse points as noise; it discovers arbitrary-shape clusters and requires no `k`.
- **PCA** projects data onto the principal components — the eigenvectors of the covariance matrix with the largest eigenvalues — maximizing retained variance for dimensionality reduction.

Clustering quality is assessed with internal metrics such as the silhouette score (cohesion vs. separation) or the Davies–Bouldin index, and, when labels exist, external metrics like adjusted Rand index.

## Tradeoffs

| Method | Strengths | Weaknesses |
| --- | --- | --- |
| k-means | Fast, simple, scales well | Needs `k`; assumes spherical clusters; sensitive to outliers |
| Hierarchical | Dendrogram, any `k` after fit | O(n³) or O(n² log n); no global objective |
| DBSCAN | Arbitrary shapes, noise detection | Sensitive to ε/minPts; poor on varying densities |
| PCA | Linear, deterministic, fast | Only linear structure; components hard to interpret |

## When to use
- Customer/market segmentation where a fixed number of groups is known (k-means).
- Exploratory analysis requiring a full cluster hierarchy (hierarchical clustering).
- Geographic or spatial data with noise and irregular shapes (DBSCAN).
- Dimensionality reduction or feature de-correlation before visualization/modeling (PCA).

## Alternatives
- **Gaussian Mixture Models (GMM)** — soft, probabilistic clusters with covariance, but needs EM iterations and a chosen component count.
- **t-SNE / UMAP** — superior non-linear visualization, but stochastic and not suited for downstream reconstruction.

## Related
- [Supervised Learning](01-supervised-learning.md)
- [Neural Networks](03-neural-networks.md)
- [Deep Learning Architectures](04-deep-learning-architectures.md)
