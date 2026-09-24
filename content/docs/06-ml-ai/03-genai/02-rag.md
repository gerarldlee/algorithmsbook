---
title: "Retrieval-Augmented Generation (RAG)"
weight: 2
toc: true
---

## What it is
Retrieval-Augmented Generation (RAG) grounds an LLM's answer in external knowledge by first **retrieving** relevant documents and then feeding them into the model's prompt before it **generates** a response. It gives LLMs access to fresh, private, or domain-specific data without retraining or fine-tuning, and reduces hallucination by anchoring output to retrieved sources.

## How it works
RAG is an offline + online pipeline:

- **Indexing (offline):** documents are split into overlapping **chunks**, each chunk is converted to an embedding vector, and the vectors are stored in a vector database alongside metadata.
- **Retrieval (online):** the user query is embedded, and the vector database returns the top-`k` nearest chunks (often via HNSW or IVF-PQ). Retrieved chunks may be **reranked** by a cross-encoder to boost precision, then compressed/deduplicated.
- **Generation (online):** the top chunks are placed into the prompt as context, and the LLM produces an answer (ideally with citations).

*Naive* RAG retrieves once with a fixed top-`k`. *Advanced* RAG adds query rewriting, hybrid retrieval (dense + sparse/BM25), reranking, and iterative "self-ask" loops.

```yaml
# RAG pipeline (architecture description)
indexing:
  - split: chunk documents into ~256-512 token windows with overlap
  - embed: map each chunk to a dense vector via an embedding model
  - store: insert vectors + metadata into the vector database (HNSW/IVF-PQ)

retrieval:
  - embed_query: embed the user's question with the same model
  - search: top-k approximate nearest neighbors from the vector DB
  - rerank: score candidates with a cross-encoder; keep the best m

generation:
  - prompt: prepend retrieved chunks as context with instructions + citations
  - generate: LLM produces a grounded answer from the context window
```

## Tradeoffs

| Aspect | Notes |
| --- | --- |
| Freshness | New data is available after re-embedding; no retraining required |
| Hallucination | Grounding reduces but does not eliminate fabrication |
| Quality ceiling | Answer quality is bounded by retrieval quality (garbage in, garbage out) |
| Latency | Extra retrieval + reranking steps add to end-to-end response time |
| Cost | Index storage, embeddings, and rerankers all add ongoing expense |

## When to use
- Question answering over private/internal corpora (docs, support tickets, policies).
- Grounding LLMs in data that changes frequently or is too large for the context window.
- Applications requiring cited, auditable answers rather than open-ended generation.

## Alternatives
- **Fine-tuning** — bakes knowledge into weights for a specific style/task, but is expensive and stale until retrained.
- **Long-context prompting** — paste everything into the window, but hits context limits and higher token cost.
- **Graph RAG** — retrieves over a knowledge graph for multi-hop reasoning, but requires building and maintaining the graph.

## Related
- [Vector Databases](01-vector-databases.md)
- [LLM Serving](04-llm-serving.md)
- [AI Agents](05-ai-agents.md)
- [Transformers](../01-ml-foundations/05-transformers.md)
