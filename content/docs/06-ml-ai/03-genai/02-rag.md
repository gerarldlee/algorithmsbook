---
title: "Retrieval-Augmented Generation (RAG): Chunking Frameworks, Hybrid Search, Dense/Sparse Embeddings, and Re-ranking"
weight: 2
toc: true
---

## What it is
Retrieval-Augmented Generation (RAG) is a retrieval-and-generation pattern that supplies an LLM with selected external context before it produces an answer. It extends a model with current, private, or domain-specific knowledge without changing its weights, and it gives the application evidence that it can return as citations.

## How it works
RAG separates into an indexing path and a request path. The indexing path preserves document identity and source locations, creates chunks, builds searchable representations, and writes versioned artifacts. The request path interprets the question, retrieves candidates, places a bounded selection in the prompt, generates an answer, and maps claims back to source locations.

Chunking is a systems decision rather than a fixed token count. Fixed windows are predictable, semantic boundaries preserve tables and paragraphs, and recursive splitters used by LangChain and LlamaIndex combine structural rules with size limits. Overlap can retain context across a boundary, but it also duplicates candidates and consumes context. Store the original document ID, chunk ordinal, headings, URI, and access-control labels with every chunk. The labels support policy evaluation, but they do not enforce authorization by themselves: tenant and policy filtering must occur before any unauthorized candidate reaches the reranker, context builder, or generation model.

A **dense embedding** maps text into a vector where related meanings tend to lie near one another. A **sparse representation**, such as a BM25 vector, records weighted terms and preserves exact identifiers, names, and numbers. Hybrid retrieval runs both paths, then fuses the rankings. Reciprocal rank fusion combines ranks without requiring calibrated score scales. A **cross-encoder reranker**, such as a transformer trained to score a query-document pair, can improve ranking by jointly considering the query and candidate, but it does not guarantee better end-to-end accuracy and costs more because it processes the pairs.

The following pipeline manifest makes the data contracts and ordering explicit:

```yaml
indexing:
  inputs:
    - object_store_documents
    - document_metadata
  chunking:
    strategy: semantic
    max_tokens: 512
    overlap_tokens: 64
    preserve: [document_id, ordinal, heading_path, uri, acl]
  indexes:
    dense:
      model: organization_embedding_model
      dimensions: 768
      store: vector_database
    sparse:
      method: BM25
      store: full_text_database
  artifact_version: corpus_manifest_hash

retrieval:
  request:
    - normalize_query
    - classify_query
    - expand_query
  candidates:
    dense_limit: 50
    sparse_limit: 50
  fusion:
    method: reciprocal_rank_fusion
    constant: 60
  rerank:
    model: organization_cross_encoder
    input_limit: 100
    output_limit: 8
  permissions:
    inputs: [tenant_id, acl_labels, policy_context]
    filter: tenant_and_policy
    fail_closed: true
    before: [cross_encoder, context_builder, generation_model]

generation:
  context_builder:
    deduplicate: true
    preserve_source_order: true
    label_sources: true
  model:
    temperature: 0
    require_source_for_claims: true
  evaluation:
    retrieval_metrics: [recall_at_k, ndcg_at_k]
    answer_metrics: [faithfulness, answer_relevance, citation_accuracy]
```

Grounding reduces unsupported answers but does not make the generator reliable by itself. A retrieved passage can be irrelevant, the model can ignore it, and a correct passage can be summarized incorrectly. Evaluate retrieval separately from generation with a representative question set, then test citation coverage and faithfulness end to end.

## Tradeoffs

| Design choice | Gain | Cost or risk |
| --- | --- | --- |
| Dense retrieval alone | Captures paraphrase and semantic similarity | Can miss exact identifiers and rare terms |
| Sparse retrieval alone | Preserves lexical precision and exact matches | Depends on query and document vocabulary overlap |
| Hybrid retrieval and rank fusion | Recovers candidates from both representations | Adds indexes, latency, and tuning for fusion parameters |
| Cross-encoder reranking | Can improve ordering with joint query-document context | Adds model inference cost and a second latency stage without guaranteeing better answer accuracy |
| Larger context budget | Preserves more retrieved evidence | Increases generation latency, token cost, and distraction risk |
| Direct generation without citations | Simpler output contract | Makes claims harder to verify and does not expose retrieval coverage |
| Iterative retrieval | Can resolve multi-step evidence needs | Requires stopping rules and raises cost and latency |

## When to use
- You need current or private knowledge without retraining the language model.
- You must attach source evidence or audit references to model answers.
- The corpus is too large or too structured to place reliably in the model context window.
- You can define an evaluation set containing questions, relevant passages, and answer-level checks.
- You need access control that can be enforced before retrieved content reaches the generator.

## Alternatives
- **Fine-tuning** — wins when behavior, format, or task-specific reasoning must change, but it does not reliably refresh factual knowledge and requires training data.
- **Long-context prompting** — wins when the entire trusted source set fits and is small enough to attend to, but it has high recurring token cost and weak retrieval discipline.
- **Graph retrieval (GraphRAG)** — wins for relationship-heavy, multi-hop questions, but it requires entity resolution, graph construction, and graph maintenance.
- **Deterministic application search** — wins when a structured database or API can answer exactly, but it does not provide open-ended synthesis over prose.

## Related
- [Vector Databases (Pinecone, Qdrant, Milvus), Similarity Metrics (Cosine, L2, Dot Product), and Approximate Nearest Neighbors (HNSW, IVF-PQ)](01-vector-databases.md)
- [High-Throughput LLM Serving Frameworks: vLLM, PagedAttention, KV Caching, Continuous Batching, and Speculative Decoding](04-llm-serving.md)
- [AI Agent Systems: Tool-Calling Mechanics, Long/Short-Term Memory Stores, Reasoning Frameworks (ReAct), and Multi-Agent Orchestration](05-ai-agents.md)
- [Transformer Architecture](../01-ml-foundations/05-transformers.md)
