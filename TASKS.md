# Project Tasks

This file turns the book outline and repository authoring rules into an actionable checklist.
`TOC.md` remains the canonical outline; update both files when the scope changes.

Checked items are verified in the current repository. Chapter topic items remain open until each
page has been audited against the full chapter and language contracts, even when the page file
already exists.

## Completed implementation

- [x] Add the preferred-language selector before Docs in the header.
- [x] Default the selector to Java and persist the selected language.
- [x] Filter complete six-language algorithm groups to the selected language.
- [x] Load the selector JavaScript through Hextra's custom head-end hook.

## Project foundation

- [x] Keep the Hugo site on extended Hugo `0.159.2`.
- [x] Keep Hextra `v0.12.3` managed as a Go module; do not add a `themes/` directory or submodule.
- [x] Maintain the relative-link render hook in `layouts/_markup/render-link.html`.
- [x] Keep generated output (`public/`, `resources/`, `.hugo_build.lock`) out of source control.
- [x] Keep the link, front-matter, weight, naming, and heading checks passing with `python tools/check_links.py`.
- [ ] Add every new page to its parent `_index.md` in weight order.
- [ ] Add every new category or part to the relevant navigation pages and home-page table of contents.
- [x] Keep `TOC.md` synchronized with the content tree.

## Chapter implementation contract

Apply these checks to every chapter:

- [ ] Use YAML front matter with a quoted Title Case `title`.
- [ ] Set `weight` to the two-digit filename prefix and keep sibling weights unique.
- [ ] Set `toc: true` on chapters; omit it from navigation pages, the home page, about page, and essentials reference pages unless there is a deliberate exception.
- [ ] Remove `draft: true` before committing a completed page.
- [ ] Use `##` for chapter sections and never add a page-level `# H1`.
- [ ] Keep the required section order: What it is, How it works, optional Complexity or Tradeoffs, When to use, Alternatives, Related.
- [ ] Use Complexity and Tradeoffs exclusively; do not include both on one chapter.
- [ ] Put Related last and use relative internal links.
- [ ] Use active, present-tense prose, define terms on first use, and keep claims checkable.
- [ ] Use theme-neutral Markdown; do not add hard-coded colors, inline styles, font tags, or background classes.
- [ ] Tag every fenced code block with its language.
- [ ] Run a production build and the link checker before publishing.

## Algorithm examples

For every algorithm chapter:

- [ ] Provide the complete six-language group in this order: Java, C, Python, Rust, TypeScript, Go.
- [ ] Use the exact fence identifiers `java`, `c`, `python`, `rust`, `typescript`, and `go`.
- [ ] Keep type names, operation sets, and algorithms equivalent across languages.
- [ ] Keep language-specific explanations inside that language's code block as comments.
- [ ] Keep language order and tab names identical across groups on a page.
- [ ] If tab shortcodes are introduced, synchronize their language groups with `tabs.sync: true`.
- [ ] Use Mermaid fences for diagrams and keep diagrams free of hard-coded colors.

## Part I — Fundamental Data Structures & Core Algorithms

### Chapter 1 — Linear Data Structures & Memory Models

- [x] 1.1 Dynamic Arrays, Memory Allocation, and Amortized Analysis
- [x] 1.2 Linked Lists (Singly, Doubly, Skip Lists)
- [x] 1.3 Stacks, Queues, Deques, and Ring/Circular Buffers
- [x] 1.4 Hash Tables: Hash Functions, Collision Resolution, and Universal Hashing
- [x] 1.5 Bitwise Algorithms, Bitsets, and Bloom Filters

### Chapter 2 — Hierarchical Data Structures & Search Trees

- [x] 2.1 Binary Search Trees & Self-Balancing Trees (AVL, Red-Black Trees)
- [x] 2.2 Heaps, Priority Queues, and Fibonacci Heaps
- [x] 2.3 Storage Engine Trees: B-Trees, B+ Trees, and Log-Structured Merge-Trees (LSM-Trees)
- [x] 2.4 Range Queries: Segment Trees, Fenwick Trees (Binary Indexed Trees), and Interval Trees
- [x] 2.5 Disjoint-Set Data Structures (Union-Find with Path Compression)
- [x] 2.6 Tries, Radix Trees, and Suffix Trees/Arrays

### Chapter 3 — Core Algorithmic Paradigms

- [x] 3.1 Divide-and-Conquer & Advanced Sorting (Quick, Merge, Radix, Counting Sort)
- [x] 3.2 Greedy Choice Paradigms & Interval Scheduling
- [x] 3.3 Dynamic Programming (Memoization, Tabulation, State Compression, Space Optimization)
- [x] 3.4 Backtracking, Branch-and-Bound, and Constraint Satisfaction Problems
- [x] 3.5 Amortized Analysis Techniques (Aggregate, Accounting, and Potential Methods)

### Chapter 4 — Graph Theory & Network Algorithms

- [x] 4.1 Graph Representations (Adjacency Matrix, Adjacency List, Edge List)
- [x] 4.2 Graph Traversals: Breadth-First Search (BFS) and Depth-First Search (DFS)
- [x] 4.3 Topological Sorting & Strongly Connected Components (Tarjan’s, Kosaraju’s)
- [x] 4.4 Minimum Spanning Trees (Kruskal’s, Prim’s Algorithms)
- [x] 4.5 Shortest Path Algorithms: Single-Source (Dijkstra’s, Bellman-Ford) & All-Pairs (Floyd-Warshall, Johnson’s)
- [x] 4.6 Network Flow & Matching (Ford-Fulkerson, Edmonds-Karp, Dinic’s, Hopcroft-Karp)

## Part II — System Design Foundations & High-Scale Architecture

### Chapter 5 — System Design Fundamentals

- [ ] 5.1 Fundamentals of System Design: Latency, Throughput, Availability, and SLA/SLO/SLI
- [ ] 5.2 Network Protocols: OSI Model, TCP/UDP, HTTP/1.1 vs HTTP/2 vs HTTP/3, gRPC, and WebSockets
- [ ] 5.3 Load Balancing Strategies: L4 vs L7, Round-Robin, Least Connections, Consistent Hashing
- [ ] 5.4 Reverse Proxies, API Gateways, and Edge Routing (Nginx, Envoy, Traefik)
- [ ] 5.5 API Paradigms: REST, GraphQL, gRPC Protocol Buffers, and Event-Driven Systems

### Chapter 6 — Caching Strategies & Edge Acceleration

- [ ] 6.1 In-Memory Caching Engines (Redis, Memcached) & Eviction Policies (LRU, LFU, ARC)
- [ ] 6.2 Application Caching Patterns: Cache-Aside, Write-Through, Write-Around, Write-Behind
- [ ] 6.3 Content Delivery Networks (CDNs), Edge Computing, and Static/Dynamic Content Acceleration
- [ ] 6.4 Rate Limiting & Traffic Shaping: Token Bucket, Leaky Bucket, Sliding Window Log, and Counter

## Part III — Messaging, Notifications & Real-Time Communication

### Chapter 7 — Asynchronous Messaging & Pub/Sub Systems

- [ ] 7.1 Message Queues vs Event Streams (RabbitMQ, Apache Kafka, Apache Pulsar)
- [ ] 7.2 Publish-Subscribe (Pub/Sub) Architecture Mechanics & Fan-Out Design Patterns
- [ ] 7.3 Message Delivery Guarantees: At-Most-Once, At-Least-Once, and Exactly-Once (Idempotency Patterns)
- [ ] 7.4 Backpressure, Dead Letter Queues (DLQ), and Event Replay Frameworks

### Chapter 8 — Real-Time Communication & Notification Systems

- [ ] 8.1 Multi-Channel Notification Dispatchers: Push (APNs, FCM), SMS, Email, and Webhook Architecture
- [ ] 8.2 Real-Time Protocols: WebSockets, Server-Sent Events (SSE), and Long Polling
- [ ] 8.3 Distributed Presence Engines, User State Tracking, and Heartbeat Protocols
- [ ] 8.4 Scalable Real-Time Chat & Collaboration Systems Architecture

## Part IV — Distributed Systems & Database Architecture

### Chapter 9 — Distributed Systems Principles & Consensus

- [ ] 9.1 The CAP Theorem, PACELC, and Architectural Trade-offs
- [ ] 9.2 Consensus Protocols: Paxos, Raft, Multi-Paxos, and Distributed Locks (Chubby, Redlock)
- [ ] 9.3 Clocks & Ordering: Physical Clocks, NTP, Logical Clocks (Lamport), and Vector Clocks
- [ ] 9.4 Distributed Transactions: Two-Phase Commit (2PC), Three-Phase Commit (3PC), and the Saga Pattern

### Chapter 10 — Database Engineering, Replication & Scaling

- [ ] 10.1 Relational Data Modeling, Normalization, and Indexing Strategies (B-Tree, Hash, GIN, GiST)
- [ ] 10.2 NoSQL Classifications: Key-Value, Document, Columnar (Cassandra), and Graph Databases (Neo4j)
- [ ] 10.3 Storage Engines: OLTP (Row-Oriented) vs OLAP (Columnar/Parquet/ClickHouse)
- [ ] 10.4 ACID Guarantees & Transaction Isolation Levels (Read Committed, Repeatable Read, Serializable)
- [ ] 10.5 Database Replication (Leader-Follower, Multi-Leader, Leaderless/Dynamo-Style)
- [ ] 10.6 Partitioning & Sharding Strategies: Range, Hash, List, and Directory-Based Sharding
- [ ] 10.7 Distributed Query Execution, Global Secondary Indexes, and Point-In-Time Recovery (PITR)

## Part V — Cloud Architecture, Deployment Engineering & DevOps

### Chapter 11 — Cloud Primitives & Serverless Architectures

- [ ] 11.1 Cloud Compute Mechanics: Virtual Machines, Bare-Metal, Containers, and Hypervisors
- [ ] 11.2 Storage Primitives: Block Storage, Object Storage (S3), and Network File Systems
- [ ] 11.3 Cloud Networking: Virtual Private Clouds (VPC), Subnets, NAT Gateways, Peering, and Transit Gateways
- [ ] 11.4 Serverless & Edge Computing (AWS Lambda, Cloudflare Workers, Event-Driven Triggers)
- [ ] 11.5 Infrastructure as Code (IaC): Declarative Provisioning with Terraform and OpenTofu

### Chapter 12 — Containerization, Orchestration & CI/CD Pipelines

- [ ] 12.1 Container Internals: Docker, OCI Runtimes, Linux Namespaces, and cgroups
- [ ] 12.2 Container Orchestration: Kubernetes Architecture (Control Plane, Worker Nodes, Pods, Services, Ingress)
- [ ] 12.3 Deployment Strategies: Blue-Green, Canary Releases, Rolling Updates, and Shadow Deployments
- [ ] 12.4 CI/CD Workflows, Automated Testing Pipelines, and GitOps Engines (ArgoCD, Flux)
- [ ] 12.5 Observability Platforms: Structured Logging, Metrics (Prometheus), Distributed Tracing (OpenTelemetry), and Alerting

## Part VI — Machine Learning Systems & Scalable AI Infrastructure

### Chapter 13 — Machine Learning & Deep Learning Foundations

- [ ] 13.1 Supervised Learning: Linear/Logistic Regression, Decision Trees, Random Forests, Gradient Boosting (XGBoost)
- [ ] 13.2 Unsupervised Learning: K-Means, Hierarchical Clustering, Principal Component Analysis (PCA)
- [ ] 13.3 Neural Network Mechanics: Forward/Backpropagation, Activation Functions, Loss Functions, and Optimizers (Adam, SGD)
- [ ] 13.4 Deep Learning Architectures: Convolutional Neural Networks (CNNs), Recurrent Neural Networks (RNNs)
- [ ] 13.5 Transformer Architecture: Self-Attention Mechanics, Scaled Dot-Product, Positional Encodings, Multi-Head Attention

### Chapter 14 — MLOps & Production Machine Learning Systems

- [ ] 14.1 End-to-End ML System Design: Training, Validation, Feature Engineering, and Inference Pipelines
- [ ] 14.2 Feature Stores, Dataset Versioning (DVC), and Pipeline Orchestration (Airflow, Kubeflow)
- [ ] 14.3 Model Optimization: Quantization (INT8/FP16), Pruning, Knowledge Distillation, and Model Compilation (TensorRT, ONNX)
- [ ] 14.4 High-Performance Inference: Batching, Parallel Execution, and Real-Time vs Async Pipeline Serving

### Chapter 15 — Generative AI Infrastructure & Large Scale LLM Orchestration

- [ ] 15.1 Vector Databases (Pinecone, Qdrant, Milvus), Similarity Metrics (Cosine, L2, Dot Product), and Approximate Nearest Neighbors (HNSW, IVF-PQ)
- [ ] 15.2 Retrieval-Augmented Generation (RAG): Chunking Frameworks, Hybrid Search, Dense/Sparse Embeddings, and Re-ranking
- [ ] 15.3 Distributed Model Training: Data Parallelism, Tensor Parallelism, Pipeline Parallelism (DeepSpeed, Megatron-LM)
- [ ] 15.4 High-Throughput LLM Serving Frameworks: vLLM, PagedAttention, KV Caching, Continuous Batching, and Speculative Decoding
- [ ] 15.5 AI Agent Systems: Tool-Calling Mechanics, Long/Short-Term Memory Stores, Reasoning Frameworks (ReAct), and Multi-Agent Orchestration
