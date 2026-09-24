---
title: "Decentralized Systems, Web3 & Blockchain: Merkle-Patricia Tries, PoW/PoS Consensus, EVM Runtimes, P2P Mesh Networks (Libp2p, Kademlia DHT), and DeFi Protocols (AMMs, Oracles)"
weight: 5
toc: true
---

## What it is

A decentralized system spreads authority across independent participants instead of assigning every decision to one server or administrator. A blockchain adds an ordered history of transactions, a replicated state, and rules that make accepting a new history observable. **Proof of Work (PoW)** makes producing a block costly through computation, while **Proof of Stake (PoS)** makes proposing and attesting to blocks conditional on bonded stake. A **Merkle-Patricia Trie** is a compact authenticated tree that lets a node prove that a key or account is included without receiving the whole dataset. **EVM runtimes** execute smart-contract bytecode deterministically and update a state machine. **DeFi protocols** such as automated market makers and oracles apply programmable finance rules to shared state.

The blockchain is not just a chain of files. Peers exchange transactions and blocks over a peer-to-peer network, validators check rules, and a state model determines balances, contract storage, and application results. The system is decentralized when no single operator can unilaterally change accepted history or censor the network's rules without making its state diverge from the verified network state.

## How it works

A new node joins through one or more peers, discovers other peers, and exchanges version and block information. Libp2p provides peer identity, connection management, encrypted transport, and discovery protocols. A Kademlia distributed hash table (DHT) maps keys to nearby peers, so a node can find providers without a central directory. A node verifies the block header, Merkle root, parent link, signatures or consensus proof, and transaction rules before adding a block to its local chain.

A Merkle-Patricia trie compresses a key-value map into a root hash. Leaves hold encoded key-value pairs, internal nodes link by prefix, and a path from the root identifies the branches that prove a value. A transaction or account inclusion proof therefore contains a small path plus the claimed value, while the root anchors the result in the block header. Changing a value changes the path and root, making a different state detectable.

Consensus orders valid blocks. In PoW, a miner varies a nonce and other block fields until the block header meets the chain's difficulty target; the work makes rewriting history expensive. In PoS, validators lock stake, receive proposer or attesting duties, and sign votes for a chain head; the protocol defines slashing, finality, and fork choice. A chain's exact rules are protocol-specific; the shared idea is that participants spend resources or risk stake to make conflicting histories costly and detectable.

The smart-contract execution path is explicit:

```text
receive_block(block):
  verify_parent(block)
  verify_consensus_proof(block)
  recover_trie_root(block)
  for transaction in ordered_transactions(block):
    verify_signature_and_nonce(transaction)
    charge_gas(transaction, block_context)
    execute_contract_or_transfer(transaction, pre_state)
    record_receipt_status()
  store_state_root_and_block_payload()
```

An EVM transaction names a recipient, carries calldata, and can transfer value. The runtime executes contract bytecode against the current state and records the outcome. A top-level contract **revert** is not the same as transaction rejection: on modern EVM chains, the transaction can be included in a block, consume gas, and produce a receipt with a failed status while the reverted call frame's state changes and logs are discarded. A contract can also catch a lower-level revert and finish successfully. A transaction that the node never includes, such as one with a future nonce, has no block receipt. A contract is therefore a state-transition function, not a message that can freely change another contract's rules. Gas limits resources; they do not prove that the contract's business logic is correct.

DeFi builds financial state on top of this execution model. An automated market maker (AMM) holds reserves and prices a swap from the reserve ratio; the constant-product design uses `x * y = k` before fees, so a trade changes both reserves and incurs price impact. An oracle brings an external price or observation into a contract, often through multiple reporters and an aggregation rule. A stale or manipulated oracle can make an otherwise correct contract economically unsafe, so freshness, confidence intervals, and circuit-breaker rules matter.

A protocol-neutral topology shows the boundaries without pretending that every chain has identical finality rules:

```yaml
network:
  transport: libp2p
  peer_discovery: [kademlia_dht, gossip]
  node_operations: [announce, request, validate, store, serve]
block:
  parent_hash: previous_block_hash
  transactions: ordered_transaction_roots
  state_root: merkle_patricia_trie_root
  consensus: [proof_of_work, proof_of_stake]
state:
  storage: [balances, nonces, contract_code, contract_storage]
  proof: merkle_path_from_root_to_key
smart_contract_runtime:
  transaction: [sender, recipient, value, calldata, gas_limit, nonce, signature]
  execution: [validate, deduct_gas, run_code, commit_or_revert]
defi:
  amm:
    reserves: [x, y]
    invariant: x_times_y_equals_k
    price_effect: reserve_ratio_and_fee
  oracle:
    inputs: [external_observations, reporter_signatures, timestamps]
    result: aggregate_price_with_freshness_metadata
```

## Tradeoffs

| Property | Gain | Cost |
| --- | --- | --- |
| PoW | An open participation model with a costly computation signal | Energy expenditure, specialized mining hardware, slower blocks, and pool concentration risks |
| PoS | Lower energy use and explicit validator economics | Stake, slashing, governance, key security, and protocol-specific finality assumptions |
| Merkle-Patricia trie | Compact authenticated state and inclusion proofs | More hash computation, proof traversal, and implementation complexity than a flat map |
| P2P mesh | No single directory or network gateway | Peer churn, discovery overhead, bandwidth use, and attacks on connection resources |
| EVM compatibility | Broad contract tooling and composability | Gas, bytecode limits, oracle risk, and irreversible execution require careful design |
| AMM | Automated pricing without a conventional order book | Slippage, price impact, liquidity concentration, and exposure to asset oracles |
| On-chain oracles | Contracts can consume external information | Reporter failure, stale data, manipulation, and cost at consensus time |
| Off-chain computation or data | Lower cost and greater privacy | Requires an attested bridge, which becomes a new trust boundary |

## When to use

- Participants need a shared, tamper-evident history without a single operator controlling every copy.
- Independent nodes can verify protocol rules and recover state from the same chain.
- The application can tolerate public transaction data and the latency of network finality.
- A smart contract has deterministic inputs, bounded gas use, and an explicit failure or upgrade policy.
- The value of DeFi composability is worth the oracle, liquidity, key, and governance risks.

## Alternatives

- **A replicated database with a consensus log** — gives a clearer operational model and stronger conventional database guarantees, but requires a trusted operator or quorum authority.
- **A permissioned distributed ledger** — simplifies identity and governance, but the validator set is centrally admitted and less open.
- **Server-side multi-party computation** — can keep inputs private, but adds coordination, computation, and availability constraints.
- **Off-chain databases with cryptographic proofs or attestations** — can reduce on-chain cost, but a verifier must trust the proof system and the attested data path.

## Related

- [Consensus Protocols: Paxos, Raft, Multi-Paxos, and Distributed Locks (Chubby, Redlock)](02-consensus.md)
- [Distributed Transactions: Two-Phase Commit (2PC), Three-Phase Commit (3PC), and the Saga Pattern](04-distributed-transactions.md)
- [Database Replication & Data Synchronization](../../04-distributed-systems/02-databases/05-replication.md)
- [Data Serialization & In-Memory Formats](../../03-messaging/03-data-engineering-stream-processing/03-serialization-in-memory-formats.md)
