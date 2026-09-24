---
title: "Rate Limiting"
weight: 4
toc: true
---

## What it is
Rate limiting caps how many requests a client can make in a window to protect services from abuse, runaway clients, and cascading failures. Common algorithms are the token bucket (allows bursts up to a capacity, refilled steadily), the leaky bucket (a fixed-rate queue that smooths output), and fixed or sliding window counters.

## How it works
The token bucket holds a fixed capacity of tokens that refill at a steady rate. Each request consumes one token; when the bucket is empty the request is rejected, but a full bucket lets a client burst up to its capacity before being throttled. The leaky bucket instead meters outgoing requests at a constant rate, queuing (or dropping) any excess, which smooths traffic but adds latency under bursts. For distributed systems the same bucket state is stored atomically in Redis (e.g. a Lua script decrementing a key), so limits hold across many server instances.

```java
class TokenBucket {
    private final double capacity;
    private final double refillRate;   // tokens per second
    private double tokens;
    private long lastRefill;

    TokenBucket(double capacity, double refillRate) {
        this.capacity = capacity;
        this.refillRate = refillRate;
        this.tokens = capacity;
        this.lastRefill = System.nanoTime();
    }

    synchronized boolean allow() {
        long now = System.nanoTime();
        double elapsed = (now - lastRefill) / 1e9;
        tokens = Math.min(capacity, tokens + elapsed * refillRate);
        lastRefill = now;
        if (tokens < 1.0) return false;
        tokens -= 1.0;
        return true;
    }
}
```

```c
#include <stdbool.h>
#include <time.h>

typedef struct {
    double capacity;
    double refill_rate;
    double tokens;
    double last_refill;
} TokenBucket;

static double now_seconds(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1e9;
}

void token_bucket_init(TokenBucket *b, double capacity, double refill_rate) {
    b->capacity = capacity;
    b->refill_rate = refill_rate;
    b->tokens = capacity;
    b->last_refill = now_seconds();
}

bool token_bucket_allow(TokenBucket *b) {
    double now = now_seconds();
    double elapsed = now - b->last_refill;
    b->tokens += elapsed * b->refill_rate;
    if (b->tokens > b->capacity) b->tokens = b->capacity;
    b->last_refill = now;
    if (b->tokens < 1.0) return false;
    b->tokens -= 1.0;
    return true;
}
```

```python
import time

class TokenBucket:
    def __init__(self, capacity: float, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.monotonic()

    def allow(self) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
        if self.tokens < 1.0:
            return False
        self.tokens -= 1.0
        return True
```

```rust
use std::time::Instant;

struct TokenBucket {
    capacity: f64,
    refill_rate: f64,
    tokens: f64,
    last_refill: Instant,
}

impl TokenBucket {
    fn new(capacity: f64, refill_rate: f64) -> Self {
        TokenBucket {
            capacity,
            refill_rate,
            tokens: capacity,
            last_refill: Instant::now(),
        }
    }

    fn allow(&mut self) -> bool {
        let now = Instant::now();
        let elapsed = now.duration_since(self.last_refill).as_secs_f64();
        self.tokens = (self.tokens + elapsed * self.refill_rate).min(self.capacity);
        self.last_refill = now;
        if self.tokens < 1.0 {
            return false;
        }
        self.tokens -= 1.0;
        true
    }
}
```

```typescript
class TokenBucket {
    private capacity: number;
    private refillRate: number;
    private tokens: number;
    private lastRefill: number;

    constructor(capacity: number, refillRate: number) {
        this.capacity = capacity;
        this.refillRate = refillRate;
        this.tokens = capacity;
        this.lastRefill = performance.now();
    }

    allow(): boolean {
        const now = performance.now();
        const elapsed = (now - this.lastRefill) / 1000;
        this.tokens = Math.min(this.capacity, this.tokens + elapsed * this.refillRate);
        this.lastRefill = now;
        if (this.tokens < 1) return false;
        this.tokens -= 1;
        return true;
    }
}
```

```go
package ratelimit

import "time"

type TokenBucket struct {
	capacity   float64
	refillRate float64
	tokens     float64
	lastRefill time.Time
}

func NewTokenBucket(capacity, refillRate float64) *TokenBucket {
	return &TokenBucket{capacity: capacity, refillRate: refillRate, tokens: capacity, lastRefill: time.Now()}
}

func (b *TokenBucket) Allow() bool {
	now := time.Now()
	elapsed := now.Sub(b.lastRefill).Seconds()
	b.tokens += elapsed * b.refillRate
	if b.tokens > b.capacity {
		b.tokens = b.capacity
	}
	b.lastRefill = now
	if b.tokens < 1.0 {
		return false
	}
	b.tokens -= 1.0
	return true
}
```

## Tradeoffs
- **Burst behavior**: the token bucket permits short bursts up to capacity, which is friendly to legitimate spikes but lets a client briefly exceed the steady rate.
- **Smoothing vs. latency**: the leaky bucket outputs at a constant rate, smoothing traffic, but queues requests during bursts and adds tail latency.
- **Precision**: fixed-window counters are simple but allow up to 2× the limit at window boundaries; sliding windows are more accurate but cost more state and computation.
- **State overhead**: per-client in-memory buckets are cheap on one node but do not coordinate across instances; distributed limiting via Redis is accurate but adds a network hop and a single point of dependency.
- **Memory amplification**: a naive per-key counter for many clients can exhaust memory, so designs cap the tracked key set or use approximate (probabilistic) counters.

## When to use
- Protecting public APIs from abusive or runaway clients, per user, per IP, or per API key.
- Smoothing bursty ingestion into a downstream queue or database so backpressure does not overwhelm it.
- Enforcing a global quota across many stateless server instances via a shared Redis-backed bucket.
- Shaping outbound traffic to third-party APIs that bill or throttle by request volume.

## Alternatives
- **Leaky bucket** — constant output rate that smooths traffic, but queues requests and can add latency under bursts.
- **Fixed/sliding window counters** — simpler to reason about and cheap to store, but less burst-friendly and (fixed) less precise at boundaries.
- **Distributed Redis rate limiter (Lua/INCR + EXPIRE)** — accurate across instances but adds a network round trip and a Redis dependency.

## Related
- [In-Memory Caching](01-in-memory-caching.md)
- [CDNs and Edge Computing](03-cdns-edge.md)
- [Load Balancing](../01-system-design-fundamentals/03-load-balancing.md)
- [API Paradigms](../01-system-design-fundamentals/05-api-paradigms.md)
