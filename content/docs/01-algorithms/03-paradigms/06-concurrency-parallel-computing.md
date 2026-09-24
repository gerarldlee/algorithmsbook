---
title: "Concurrency & Parallel Computing: Mutexes, Semaphores, Lock-Free CAS Operations, Async Event Loops, and SIMD/Vectorization"
weight: 6
toc: true
tabs: {sync: true}
---

## What it is

**Concurrency and parallel computing** coordinate multiple tasks so that independent work can overlap in time and, when suitable hardware is available, execute at the same time. The mental model is a group of workers sharing limited resources: synchronization controls admission and shared state, atomic operations update small shared values without a lock, event loops keep many waits in flight, and SIMD applies one operation to several data lanes at once.

## How it works

A **mutex** gives one worker exclusive access to a protected section. A **semaphore** starts with a number of permits, and each worker must acquire a permit before proceeding and release it afterward. A one-permit semaphore has mutex-like behavior, while several permits allow a fixed number of workers into a resource pool. The `run_bounded` operation uses one permit, records the number of workers in the protected region, and returns both the total and the observed peak concurrency.

**Compare-and-swap (CAS)** atomically replaces a memory value only when it still equals an expected value. The hardware-assisted counter examples repeatedly load the old value, prepare an increment, and retry when another worker has already won. A successful worker publishes the new value without taking a mutex. Lock freedom requires the algorithm to make progress without any individual worker being blocked forever; it does not promise that every increment succeeds on its first attempt, and heavy contention can waste work on retries. The portable Python and TypeScript examples instead serialize the read-and-replace operation with a short critical section because neither example supplies a portable cross-worker atomic CAS primitive. Conventional GIL-enabled CPython threads do not execute Python bytecode in parallel, and the GIL does not make a multi-step read-and-replace indivisible. Free-threaded CPython removes the GIL, but the shown mutex still preserves atomicity. The TypeScript serializer is confined to one event-loop instance; it provides no atomicity across worker threads or SharedArrayBuffer data.

An **event loop** runs a scheduler that dispatches ready callbacks and returns control when a task awaits I/O, a timer, or another promise. The `schedule_sum` operation submits two range reductions to each language's task mechanism and completes after both results arrive. A callback consumes no extra worker thread while it is waiting, but CPU work in a callback can delay other callbacks on the same loop. Java uses `CompletableFuture` worker tasks, Python and TypeScript use cooperative tasks, and Rust returns a future for an executor to poll. The C implementation uses two pthreads, while the Go implementation sends two jobs to a goroutine-backed queue. Those scheduling mechanisms need not overlap their two range reductions in the same way, and the example promises equivalent sums rather than identical parallelism. In the TypeScript example, `Promise.all` waits for two callbacks; it does not make their synchronous arithmetic run on multiple threads. Worker threads with a shared `SharedArrayBuffer` are a different model and require their own synchronized state.

**SIMD** executes one instruction over several packed values. The `vectorizedSum` operation uses four independent lanes, combines them, and then handles the remaining tail values. This portable layout gives optimizing compilers and JIT runtimes a chance to emit SIMD instructions, but it does not guarantee that the hardware will do so. Explicit mechanisms such as the Java Vector API, C or Rust SIMD intrinsics, and vectorized runtimes give stronger control when the target and fallback paths are managed carefully. Alignment, width, overflow, short inputs, and memory bandwidth can make vector execution no faster than a scalar loop.

The six programs expose the same operation set: `run_bounded` controls admission to a protected region, `cas_increment` performs two workers' increments on one counter, `schedule_sum` submits two range tasks and joins their results, and `vectorizedSum` reduces four lanes plus a tail. Java, C, Rust, and Go use native threads or atomic instructions for the two-worker counter; Python and TypeScript use portable serialized critical sections. Every implementation returns the same counter and range sums, but the synchronization guarantees and scheduling behavior are those stated above.

{{< tabs >}}
{{< tab name="Java" >}}
```java
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Semaphore;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

record BoundedResult(long sum, int peakConcurrency) {}

public class ConcurrencyExample {
    private final int[] values;

    public ConcurrencyExample(int[] values) {
        this.values = values.clone();
    }

    public BoundedResult runBounded(int left, int right) throws InterruptedException {
        Semaphore permit = new Semaphore(1);
        AtomicLong total = new AtomicLong();
        AtomicInteger active = new AtomicInteger();
        AtomicInteger peak = new AtomicInteger();

        Runnable firstTask = () -> addBounded(left, permit, total, active, peak);
        Runnable secondTask = () -> addBounded(right, permit, total, active, peak);

        Thread first = new Thread(firstTask);
        Thread second = new Thread(secondTask);
        first.start();
        second.start();
        first.join();
        second.join();
        return new BoundedResult(total.get(), peak.get());
    }

    private void addBounded(
        long value,
        Semaphore permit,
        AtomicLong total,
        AtomicInteger active,
        AtomicInteger peak
    ) {
        boolean acquired = false;
        try {
            permit.acquire();
            acquired = true;
            int current = active.incrementAndGet();
            peak.accumulateAndGet(current, Math::max);
            total.addAndGet(value);
            active.decrementAndGet();
        } catch (InterruptedException exception) {
            Thread.currentThread().interrupt();
        } finally {
            if (acquired) permit.release();
        }
    }

    public long casIncrement(int perWorker) throws InterruptedException {
        AtomicLong counter = new AtomicLong();
        Runnable task = () -> {
            for (int index = 0; index < perWorker; index++) {
                long current = counter.get();
                while (!counter.compareAndSet(current, current + 1)) {
                    current = counter.get();
                }
            }
        };

        Thread first = new Thread(task);
        Thread second = new Thread(task);
        first.start();
        second.start();
        first.join();
        second.join();
        return counter.get();
    }

    public CompletableFuture<Long> scheduleSum() {
        int middle = values.length / 2;
        CompletableFuture<Long> left = CompletableFuture.supplyAsync(() -> rangeSum(0, middle));
        CompletableFuture<Long> right = CompletableFuture.supplyAsync(() -> rangeSum(middle, values.length));
        return left.thenCombine(right, Long::sum);
    }

    public long vectorizedSum() {
        long[] lanes = new long[4];
        int vectorEnd = values.length - values.length % 4;
        for (int index = 0; index < vectorEnd; index += 4) {
            lanes[0] += values[index];
            lanes[1] += values[index + 1];
            lanes[2] += values[index + 2];
            lanes[3] += values[index + 3];
        }
    int64_t total = lanes[0] + lanes[1] + lanes[2] + lanes[3];
        for (int index = vectorEnd; index < values.length; index++) {
            total += values[index];
        }
        return total;
    }

    private long rangeSum(int start, int end) {
        long total = 0;
        for (int index = start; index < end; index++) {
            total += values[index];
        }
        return total;
    }
}
```

{{< /tab >}}
{{< tab name="C" >}}
```c
#include <pthread.h>
#include <semaphore.h>
#include <stdatomic.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>

typedef atomic_int_least64_t AtomicCounter;

typedef struct {
    int *values;
    size_t length;
} ConcurrencyExample;

typedef struct {
    int64_t sum;
    int peak_concurrency;
} BoundedResult;

typedef struct {
    sem_t permit;
    pthread_mutex_t state_mutex;
    int64_t total;
    int active;
    int peak;
} BoundedState;

typedef struct {
    BoundedState *state;
    int64_t value;
} BoundedTask;

typedef struct {
    AtomicCounter *counter;
    int iterations;
} IncrementTask;

typedef struct {
    const int *values;
    size_t start;
    size_t end;
} EventJob;

typedef struct {
    const int *values;
    EventJob jobs[2];
    int64_t results[2];
    size_t completed;
    pthread_mutex_t state_mutex;
} ScheduleState;

ConcurrencyExample *cc_new(const int *values, size_t length) {
    ConcurrencyExample *example = malloc(sizeof(*example));
    if (example == NULL) return NULL;
    example->values = malloc(length == 0 ? sizeof(*values) : length * sizeof(*values));
    if (example->values == NULL) {
        free(example);
        return NULL;
    }
    for (size_t index = 0; index < length; index++) example->values[index] = values[index];
    example->length = length;
    return example;
}

void cc_free(ConcurrencyExample *example) {
    free(example->values);
    free(example);
}

static void *bounded_worker(void *argument) {
    BoundedTask *task = argument;
    sem_wait(&task->state->permit);
    pthread_mutex_lock(&task->state->state_mutex);
    task->state->active++;
    if (task->state->active > task->state->peak) task->state->peak = task->state->active;
    task->state->total += task->value;
    task->state->active--;
    pthread_mutex_unlock(&task->state->state_mutex);
    sem_post(&task->state->permit);
    return NULL;
}

BoundedResult cc_run_bounded(ConcurrencyExample *example, int64_t left, int64_t right) {
    (void)example;
    BoundedState state = {0};
    sem_init(&state.permit, 0, 1);
    pthread_mutex_init(&state.state_mutex, NULL);
    BoundedTask first = {&state, left};
    BoundedTask second = {&state, right};
    pthread_t threads[2];
    pthread_create(&threads[0], NULL, bounded_worker, &first);
    pthread_create(&threads[1], NULL, bounded_worker, &second);
    pthread_join(threads[0], NULL);
    pthread_join(threads[1], NULL);
    BoundedResult result = {state.total, state.peak};
    pthread_mutex_destroy(&state.state_mutex);
    sem_destroy(&state.permit);
    return result;
}

static void cc_increment(AtomicCounter *counter) {
    int_least64_t current = atomic_load(counter);
    int_least64_t desired;
    do {
        desired = current + 1;
    } while (!atomic_compare_exchange_weak(counter, &current, desired));
}

static void *increment_worker(void *argument) {
    IncrementTask *task = argument;
    for (int index = 0; index < task->iterations; index++) cc_increment(task->counter);
    return NULL;
}

int_least64_t cc_cas_increment(ConcurrencyExample *example, int per_worker) {
    (void)example;
    AtomicCounter counter = 0;
    atomic_init(&counter, 0);
    IncrementTask first = {&counter, per_worker};
    IncrementTask second = {&counter, per_worker};
    pthread_t threads[2];
    pthread_create(&threads[0], NULL, increment_worker, &first);
    pthread_create(&threads[1], NULL, increment_worker, &second);
    pthread_join(threads[0], NULL);
    pthread_join(threads[1], NULL);
    return atomic_load(&counter);
}

static void *schedule_worker(void *argument) {
    ScheduleState *state = argument;
    pthread_mutex_lock(&state->state_mutex);
    size_t job_index = state->completed++;
    pthread_mutex_unlock(&state->state_mutex);
    int64_t total = 0;
    for (size_t index = state->jobs[job_index].start; index < state->jobs[job_index].end; index++) {
        total += state->values[index];
    }
    state->results[job_index] = total;
    return NULL;
}

int64_t cc_schedule_sum(ConcurrencyExample *example) {
    ScheduleState state = {0};
    state.values = example->values;
    state.jobs[0] = (EventJob){example->values, 0, example->length / 2};
    state.jobs[1] = (EventJob){example->values, example->length / 2, example->length};
    pthread_mutex_init(&state.state_mutex, NULL);
    pthread_t threads[2];
    for (size_t index = 0; index < 2; index++) {
        pthread_create(&threads[index], NULL, schedule_worker, &state);
    }
    for (size_t index = 0; index < 2; index++) pthread_join(threads[index], NULL);
    int64_t total = state.results[0] + state.results[1];
    pthread_mutex_destroy(&state.state_mutex);
    return total;
}

int64_t cc_vectorized_sum(ConcurrencyExample *example) {
    int64_t lanes[4] = {0, 0, 0, 0};
    size_t vector_end = example->length - example->length % 4;
    for (size_t index = 0; index < vector_end; index += 4) {
        lanes[0] += example->values[index];
        lanes[1] += example->values[index + 1];
        lanes[2] += example->values[index + 2];
        lanes[3] += example->values[index + 3];
    }
    long total = lanes[0] + lanes[1] + lanes[2] + lanes[3];
    for (size_t index = vector_end; index < example->length; index++) total += example->values[index];
    return total;
}
```

{{< /tab >}}
{{< tab name="Python" >}}
```python
import asyncio
import threading


class BoundedResult:
    def __init__(self, total, peak_concurrency):
        self.total = total
        self.peak_concurrency = peak_concurrency


class ConcurrencyExample:
    def __init__(self, values):
        self._values = list(values)

    def run_bounded(self, left, right):
        permit = threading.BoundedSemaphore(1)
        state_lock = threading.Lock()
        state = {"total": 0, "active": 0, "peak": 0}

        def add(value):
            with permit:
                with state_lock:
                    state["active"] += 1
                    state["peak"] = max(state["peak"], state["active"])
                    state["total"] += value
                    state["active"] -= 1

        first = threading.Thread(target=add, args=(left,))
        second = threading.Thread(target=add, args=(right,))
        first.start()
        second.start()
        first.join()
        second.join()
        return BoundedResult(state["total"], state["peak"])

    def cas_increment(self, per_worker):
        counter_lock = threading.Lock()
        counter = {"value": 0}

        def increment():
            for _ in range(per_worker):
                while True:
                    expected = counter["value"]
                    with counter_lock:
                        if counter["value"] == expected:
                            counter["value"] = expected + 1
                            break

        first = threading.Thread(target=increment)
        second = threading.Thread(target=increment)
        first.start()
        second.start()
        first.join()
        second.join()
        return counter["value"]

    async def schedule_sum(self):
        middle = len(self._values) // 2

        async def range_sum(values):
            await asyncio.sleep(0)
            return sum(values)

        parts = await asyncio.gather(
            range_sum(self._values[:middle]),
            range_sum(self._values[middle:]),
        )
        return parts[0] + parts[1]

    def vectorized_sum(self):
        lanes = [0, 0, 0, 0]
        vector_end = len(self._values) - len(self._values) % 4
        for index in range(0, vector_end, 4):
            lanes[0] += self._values[index]
            lanes[1] += self._values[index + 1]
            lanes[2] += self._values[index + 2]
            lanes[3] += self._values[index + 3]
        total = sum(lanes)
        for index in range(vector_end, len(self._values)):
            total += self._values[index]
        return total
```

{{< /tab >}}
{{< tab name="Rust" >}}
```rust
use std::future::Future;
use std::pin::Pin;
use std::sync::atomic::{AtomicI64, Ordering};
use std::sync::{Arc, Condvar, Mutex};
use std::task::{Context, Poll};
use std::thread;

pub struct BoundedResult {
    pub total: i64,
    pub peak_concurrency: i32,
}

pub struct ConcurrencyExample {
    values: Vec<i32>,
}

struct EventJob {
    values: Arc<Vec<i32>>,
    start: usize,
    end: usize,
    yielded: bool,
}

struct EventLoop {
    jobs: [EventJob; 2],
    completed: [Option<i64>; 2],
    total: i64,
}

struct BoundedSemaphore {
    permits: Mutex<usize>,
    available: Condvar,
}

struct SemaphorePermit<'a> {
    semaphore: &'a BoundedSemaphore,
}

impl BoundedSemaphore {
    fn new(permits: usize) -> Self {
        Self { permits: Mutex::new(permits), available: Condvar::new() }
    }

    fn acquire(&self) -> SemaphorePermit<'_> {
        let mut permits = self.permits.lock().unwrap();
        while *permits == 0 {
            permits = self.available.wait(permits).unwrap();
        }
        *permits -= 1;
        SemaphorePermit { semaphore: self }
    }
}

impl Drop for SemaphorePermit<'_> {
    fn drop(&mut self) {
        let mut permits = self.semaphore.permits.lock().unwrap();
        *permits += 1;
        self.semaphore.available.notify_one();
    }
}

impl Future for EventJob {
    type Output = i64;

    fn poll(mut self: Pin<&mut Self>, context: &mut Context<'_>) -> Poll<Self::Output> {
        if !self.yielded {
            self.yielded = true;
            context.waker().wake_by_ref();
            return Poll::Pending;
        }
        Poll::Ready(self.values[self.start..self.end].iter().map(|value| i64::from(*value)).sum())
    }
}

impl Future for EventLoop {
    type Output = i64;

    fn poll(mut self: Pin<&mut Self>, context: &mut Context<'_>) -> Poll<Self::Output> {
        let mut remaining = 0;
        for index in 0..2 {
            if self.completed[index].is_none() {
                if let Poll::Ready(value) = Pin::new(&mut self.jobs[index]).poll(context) {
                    self.completed[index] = Some(value);
                    self.total += value;
                } else {
                    remaining += 1;
                }
            }
        }
        if remaining == 0 {
            Poll::Ready(self.total)
        } else {
            Poll::Pending
        }
    }
}

impl ConcurrencyExample {
    pub fn new(values: Vec<i32>) -> Self {
        Self { values }
    }

    pub fn run_bounded(&self, left: i64, right: i64) -> BoundedResult {
        let permit = Arc::new(BoundedSemaphore::new(1));
        let state = Arc::new(Mutex::new((left, 0_i32, 0_i32)));
        thread::scope(|scope| {
            for value in [left, right] {
                let permit = Arc::clone(&permit);
                let state = Arc::clone(&state);
                scope.spawn(move || {
                    let _guard = permit.acquire();
                    let mut current = state.lock().unwrap();
                    current.0 += value;
                    current.1 += 1;
                    current.2 = current.2.max(current.1);
                    current.1 -= 1;
                });
            }
        });
        let result = state.lock().unwrap();
        BoundedResult { total: result.0, peak_concurrency: result.2 }
    }

    pub fn cas_increment(&self, per_worker: usize) -> i64 {
        let counter = AtomicI64::new(0);
        thread::scope(|scope| {
            for _ in 0..2 {
                let counter = &counter;
                scope.spawn(move || {
                    for _ in 0..per_worker {
                        let mut current = counter.load(Ordering::Relaxed);
                        while counter
                            .compare_exchange_weak(current, current + 1, Ordering::Relaxed, Ordering::Relaxed)
                            .is_err()
                        {
                            current = counter.load(Ordering::Relaxed);
                        }
                    }
                });
            }
        });
        counter.load(Ordering::Relaxed)
    }

    pub fn schedule_sum(&self) -> Pin<Box<dyn Future<Output = i64> + Send>> {
        let values = Arc::new(self.values.clone());
        let middle = values.len() / 2;
        let right_values = Arc::clone(&values);
        Box::pin(EventLoop {
            jobs: [
                EventJob { values: Arc::clone(&values), start: 0, end: middle, yielded: false },
                EventJob { values: right_values, start: middle, end: values.len(), yielded: false },
            ],
            completed: [None, None],
            total: 0,
        })
    }

    pub fn vectorized_sum(&self) -> i64 {
        let mut lanes = [0_i64; 4];
        let vector_end = self.values.len() - self.values.len() % 4;
        for index in (0..vector_end).step_by(4) {
            lanes[0] += i64::from(self.values[index]);
            lanes[1] += i64::from(self.values[index + 1]);
            lanes[2] += i64::from(self.values[index + 2]);
            lanes[3] += i64::from(self.values[index + 3]);
        }
        let mut total = lanes.into_iter().sum::<i64>();
        for value in &self.values[vector_end..] {
            total += i64::from(*value);
        }
        total
    }
}
```

{{< /tab >}}
{{< tab name="TypeScript" >}}
```typescript
export interface BoundedResult {
  total: number;
  peakConcurrency: number;
}

export class ConcurrencyExample {
  private readonly values: number[];
  private permitAvailable = true;
  private readonly permitWaiters: Array<() => void> = [];

  constructor(values: number[]) {
    this.values = values.slice();
  }

  async runBounded(left: number, right: number): Promise<BoundedResult> {
    const state = { total: 0, active: 0, peak: 0 };
    const add = async (value: number) => {
      if (this.permitAvailable) {
        this.permitAvailable = false;
      } else {
        await new Promise<void>((resolve) => this.permitWaiters.push(resolve));
      }
      await Promise.resolve();
      state.active += 1;
      state.peak = Math.max(state.peak, state.active);
      state.total += value;
      state.active -= 1;
      const next = this.permitWaiters.shift();
      if (next) next();
      else this.permitAvailable = true;
    };
    await Promise.all([add(left), add(right)]);
    return { total: state.total, peakConcurrency: state.peak };
  }

  async casIncrement(perWorker: number): Promise<number> {
    const counter = { value: 0 };
    let available = true;
    const waiters: Array<() => void> = [];
    const increment = async () => {
      for (let index = 0; index < perWorker; index += 1) {
        if (available) {
          available = false;
        } else {
          await new Promise<void>((resolve) => waiters.push(resolve));
        }
        await Promise.resolve();
        counter.value += 1;
        const next = waiters.shift();
        if (next) next();
        else available = true;
      }
    };
    await Promise.all([increment(), increment()]);
    return counter.value;
  }

  async scheduleSum(): Promise<number> {
    const middle = Math.floor(this.values.length / 2);
    const rangeSum = async (start: number, end: number) => {
      await Promise.resolve();
      let total = 0;
      for (let index = start; index < end; index += 1) total += this.values[index];
      return total;
    };
    const parts = await Promise.all([rangeSum(0, middle), rangeSum(middle, this.values.length)]);
    return parts[0] + parts[1];
  }

  vectorizedSum(): number {
    const lanes = [0, 0, 0, 0];
    const vectorEnd = this.values.length - (this.values.length % 4);
    for (let index = 0; index < vectorEnd; index += 4) {
      lanes[0] += this.values[index];
      lanes[1] += this.values[index + 1];
      lanes[2] += this.values[index + 2];
      lanes[3] += this.values[index + 3];
    }
    let total = lanes.reduce((sum, lane) => sum + lane, 0);
    for (let index = vectorEnd; index < this.values.length; index += 1) total += this.values[index];
    return total;
  }
}
```

{{< /tab >}}
{{< tab name="Go" >}}
```go
package concurrency

import (
    "sync"
    "sync/atomic"
)

type BoundedResult struct {
    Total           int64
    PeakConcurrency int
}

type ConcurrencyExample struct {
    values []int
}

type BoundedState struct {
    mutex  sync.Mutex
    permit chan struct{}
    total  int64
    active int
    peak   int
}

type SumJob struct {
    start int
    end   int
}

func NewConcurrencyExample(values []int) *ConcurrencyExample {
    return &ConcurrencyExample{values: append([]int(nil), values...)}
}

func (example *ConcurrencyExample) RunBounded(left, right int64) BoundedResult {
    state := BoundedState{permit: make(chan struct{}, 1)}
    state.permit <- struct{}{}
    add := func(value int64) {
        <-state.permit
        state.mutex.Lock()
        state.active++
        if state.active > state.peak {
            state.peak = state.active
        }
        state.total += value
        state.active--
        state.mutex.Unlock()
        state.permit <- struct{}{}
    }
    var wait sync.WaitGroup
    wait.Add(2)
    go func() { defer wait.Done(); add(left) }()
    go func() { defer wait.Done(); add(right) }()
    wait.Wait()
    return BoundedResult{Total: state.total, PeakConcurrency: state.peak}
}

func increment(counter *atomic.Int64) {
    for {
        current := counter.Load()
        if counter.CompareAndSwap(current, current+1) {
            return
        }
    }
}

func (example *ConcurrencyExample) CasIncrement(perWorker int) int64 {
    var counter atomic.Int64
    var wait sync.WaitGroup
    wait.Add(2)
    go func() { defer wait.Done(); for index := 0; index < perWorker; index++ { increment(&counter) } }()
    go func() { defer wait.Done(); for index := 0; index < perWorker; index++ { increment(&counter) } }()
    wait.Wait()
    return counter.Load()
}

func (example *ConcurrencyExample) ScheduleSum() int64 {
    jobs := make(chan SumJob)
    results := make(chan int64, 2)
    done := make(chan struct{})
    go func() {
        defer close(done)
        for job := range jobs {
            total := int64(0)
            for index := job.start; index < job.end; index++ {
                total += int64(example.values[index])
            }
            results <- total
        }
    }()
    middle := len(example.values) / 2
    jobs <- SumJob{start: 0, end: middle}
    jobs <- SumJob{start: middle, end: len(example.values)}
    close(jobs)
    <-done
    close(results)
    total := int64(0)
    for result := range results {
        total += result
    }
    return total
}

func (example *ConcurrencyExample) VectorizedSum() int64 {
    lanes := [4]int64{}
    vectorEnd := len(example.values) - len(example.values)%4
    for index := 0; index < vectorEnd; index += 4 {
        lanes[0] += int64(example.values[index])
        lanes[1] += int64(example.values[index+1])
        lanes[2] += int64(example.values[index+2])
        lanes[3] += int64(example.values[index+3])
    }
    total := lanes[0] + lanes[1] + lanes[2] + lanes[3]
    for index := vectorEnd; index < len(example.values); index++ {
        total += int64(example.values[index])
    }
    return total
}
{{< /tab >}}
{{< /tabs >}}

## Complexity

For \(n\) values and \(p\) workers, source-level work and synchronization overhead must be considered separately. Actual runtime depends on the scheduler, available cores, contention, and whether a compiler emits vector instructions.

| Operation | Time | Space or coordination |
| --- | --- | --- |
| Bounded addition with two workers | O(1) work plus waiting for the permit | O(1) state and two worker contexts |
| Native-atomic CAS increment | O(1) per attempt; retry count depends on contention | O(1) shared-counter state |
| Portable Python or single-event-loop TypeScript increment | O(1) per increment plus critical-section waiting | O(1) shared state; neither example is lock-free or cross-worker atomic |
| Async scheduling of two fixed tasks | O(1) dispatch plus both task bodies and completion wait | O(1) per queued task in this example |
| Four-lane vectorized sum | O(n) source operations; about \(O(\lceil n/4 \rceil)\) lane groups | O(1) lane state |
| Hardware SIMD reduction with width \(w\) | About \(O(\lceil n/w \rceil)\) vector iterations plus tail work | O(1) vector state |

Amdahl's law explains why adding workers eventually stops helping: if a fraction \(s\) of the work remains serial, speedup approaches \(1/s\) as worker count grows. SIMD has a similar constraint because data movement and tail handling remain necessary. Thread creation, future creation, lock handoffs, and cache-coherence traffic can cost more than the useful work on short inputs.

## When to use
- You need to protect shared state that several workers can enter only under a strict admission limit.
- You need a bounded connection, device, or worker pool and must prevent unlimited concurrent access.
- You have a small contended counter for which a verified CAS loop is simpler than ownership by one worker.
- You need to keep many I/O waits in flight without dedicating one operating-system thread to every wait.
- You have regular numeric loops that a measured vector instruction path can accelerate.
- You need independent CPU tasks and enough available cores to repay coordination costs.

## Alternatives
- **Actor model** — assigns mutable state to one owner and communicates through messages, avoiding shared locks at the cost of message latency and ordering rules.
- **Immutable data and partitioning** — gives each worker private state, simplifying concurrency at the cost of copying or data movement.
- **GPU execution** — offers large data-parallel throughput for suitable arrays, but transfers and synchronization dominate small workloads.
- **Task pools and work stealing** — reuse workers and balance irregular jobs, adding scheduler state and less direct control.
- **File-descriptor readiness or async I/O runtimes** — scale many blocking operations efficiently, but they do not make synchronous CPU callbacks parallel.

## Related
- [Graph Representations and Graph Neural Network Data Structures](../04-graphs/01-graph-representations.md)
- [Amortized Analysis Techniques](05-amortized-analysis.md)
- [Divide-and-Conquer & Advanced Sorting](01-divide-and-conquer-sorting.md)
