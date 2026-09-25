---
title: "Chapter 15 References"
weight: 7
---

## Books

- Ian Goodfellow, Yoshua Bengio, and Aaron Courville, *Deep Learning*, MIT Press, 2016.
- Chip Huyen, *Designing Machine Learning Systems*, second edition, O'Reilly Media, 2024.
- Chip Huyen, *AI Engineering: Building Applications with Foundation Models*, O'Reilly Media, 2025.
- Daniel J. Jurafsky and James H. Martin, *Speech and Language Processing*, draft third edition, 2024.

## Websites

- [ScaNN: Scalable Nearest Neighbors](https://github.com/google-research/google-research/tree/master/scann) — Google Research implementation and algorithm notes for partition-and-search, quantization, and rescoring.
- [Accelerating Large-Scale Inference with Anisotropic Vector Quantization](https://arxiv.org/abs/1908.10396) — the ScaNN paper.
- [DiskANN: Fast Accurate Billion-point Nearest Neighbor Search on a Single Node](https://www.microsoft.com/en-us/research/publication/diskann-fast-accurate-billion-point-nearest-neighbor-search-on-a-single-node/) — the DiskANN and Vamana system paper.
- [DiskANN source code](https://github.com/microsoft/DiskANN) — Microsoft implementations of out-of-core and in-memory vector indexing.
- [Efficient and Robust Approximate Nearest Neighbor Search Using HNSW](https://arxiv.org/abs/1603.09320) — the HNSW paper.
- [FAISS wiki](https://github.com/facebookresearch/faiss/wiki) — implementation notes for exact and approximate vector indexes, including IVF and product quantization.
- [Pinecone documentation](https://docs.pinecone.io/) — managed vector database concepts and API guidance.
- [Qdrant documentation](https://qdrant.tech/documentation/) — self-hosted vector search, collections, and payload filtering.
- [Milvus documentation](https://milvus.io/docs) — distributed vector database architecture and index guidance.
- [LangChain RAG tutorials](https://docs.langchain.com/oss/python/langchain/rag) — retrieval, indexing, and retrieval-chain patterns.
- [LlamaIndex documentation](https://docs.llamaindex.ai/en/stable/) — data connectors, indexes, query engines, and agent workflows.
- [DeepSpeed documentation](https://deepspeed.readthedocs.io/) — ZeRO, pipeline parallelism, and large-scale training configuration.
- [Megatron-LM source code](https://github.com/NVIDIA/Megatron-LM) — NVIDIA implementation of tensor, pipeline, sequence, and context parallelism.
- [PyTorch FSDP documentation](https://pytorch.org/docs/stable/fsdp.html) — explicit parameter, gradient, and optimizer-state sharding.
- [vLLM documentation](https://docs.vllm.ai/) — distributed LLM inference, scheduling, paged KV caches, and supported optimizations.
- [Efficient Memory Management for Large Language Model Serving with PagedAttention](https://arxiv.org/abs/2309.06180) — the PagedAttention and vLLM systems paper.
- [Orca: A Distributed Serving System for Transformer-Based Generative Models](https://www.microsoft.com/en-us/research/publication/orca-a-distributed-serving-system-for-transformer-based-generative-models/) — the continuous-batching serving design.
- [LangChain agents](https://docs.langchain.com/oss/python/langchain/agents) — tool-calling agent loops and runtime state.
- [LlamaIndex agents](https://developers.llamaindex.ai/python/framework/use_cases/agents/) — prebuilt agents and event-driven agent workflows.
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) — the interleaved reasoning-and-action paper.
- [Hugging Face PEFT documentation](https://huggingface.co/docs/peft/index) — adapter configuration and PEFT integration.
- [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685) — the LoRA paper.
- [QLoRA: Efficient Finetuning of Quantized LLMs](https://arxiv.org/abs/2305.14314) — the QLoRA paper.
- [Deep Reinforcement Learning from Human Preferences](https://arxiv.org/abs/1709.06041) — the foundational RLHF paper.
- [Direct Preference Optimization: Your Language Model is Secretly a Reward Model](https://arxiv.org/abs/2305.18290) — the DPO paper.
- [Hugging Face TRL documentation](https://huggingface.co/docs/trl/index) — supervised, reward, DPO, and reinforcement-learning trainers.
