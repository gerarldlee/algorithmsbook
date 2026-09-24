---
title: "AI Agents"
weight: 5
toc: true
---

## What it is
An AI agent is an LLM-based system that can act in the world — calling tools, executing code, and querying external systems — in a loop, rather than emitting a single static answer. It combines the model's reasoning with **tool use**, **planning**, and **memory** to carry out multi-step tasks with some autonomy.

## How it works

- **Tool use / function calling:** the model is given a schema of available functions; it emits a structured call, the runtime executes it and returns the result, and the model continues. This is the "act" step.
- **ReAct (Reason + Act):** an interleaved loop where the model writes a *thought*, performs an *action* (tool call), and observes the result, repeating until it can produce a final answer.
- **Planning:** decomposing a goal into sub-tasks (task decomposition) and possibly revising the plan when steps fail (self-reflection).
- **Memory:** short-term context plus long-term store (vector DB of past interactions) lets the agent recall facts across sessions.
- **Multi-agent systems:** several specialized agents coordinate (orchestrator pattern) to handle parallel subtasks.

```yaml
# AI agent (architecture description)
loop:
  - plan: decompose the goal into steps (task decomposition)
  - reason: emit a thought and choose the next action (ReAct)
  - act:   call a tool / function; runtime executes it
  - observe: append the tool result to the context
  - reflect: check progress; revise plan or terminate
  - until: goal satisfied or max iterations reached

tools:
  - function_calling: model selects from a JSON schema of tools
  - code_execution: sandboxed interpreter for compute tasks
  - retrieval: search documents / vector DB for grounding

memory:
  - short_term: conversation context (the prompt history)
  - long_term: vector store of past facts and episodes

coordination:
  - orchestrator: a lead agent delegates to worker agents
  - multi_agent: specialized agents collaborate on subtasks
```

## Tradeoffs

| Aspect | Notes |
| --- | --- |
| Autonomy vs. safety | More tool access means more capability but more failure/abuse surface |
| Reliability | Multi-step loops compound errors; each step's failure propagates |
| Cost/latency | Many tool calls and reasoning steps are slow and token-expensive |
| Controllability | Open-ended agents are harder to debug and audit than single calls |
| Context limits | Long tool histories can overflow the window; summarization needed |

## When to use
- Multi-step workflows with real-world actions (book a trip, run a pipeline, browse + summarize).
- Tasks requiring up-to-date data through retrieval or code execution.
- Situations where delegating subtasks to specialized agents improves quality.

## Alternatives
- **Single-call LLM** — one prompt/response, cheaper and predictable, but cannot act or iterate.
- **Hardcoded workflow / DAG** — deterministic orchestration, reliable but inflexible to novel inputs.
- **Human-in-the-loop approval** — adds a person before risky actions, safer but slower and less autonomous.

## Related
- [Retrieval-Augmented Generation (RAG)](02-rag.md)
- [LLM Serving](04-llm-serving.md)
- [Distributed Training](03-distributed-training.md)
- [Transformers](../01-ml-foundations/05-transformers.md)
