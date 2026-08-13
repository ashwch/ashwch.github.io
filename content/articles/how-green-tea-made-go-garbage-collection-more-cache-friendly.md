Title: How Green Tea Made Go's Garbage Collector More Cache-Friendly
Date: 2026-08-12
Modified: 2026-08-12
Status: published
Category: Programming
Tags: go, golang, garbage-collection, performance, runtime, green-tea, memory, safepoints
Slug: how-green-tea-made-go-garbage-collection-more-cache-friendly
Authors: Ashwini Chaudhary
Summary: How Go finds live heap objects, why safepoints and compiler pointer maps matter, and how Green Tea changes the marking worklist from objects to memory spans.

I recently watched Michael Knyszek's GopherCon 2025 talk, [Advancing Go Garbage Collection with Green Tea](https://www.youtube.com/watch?v=gPJkM95KpKo). Green Tea makes much more sense once the normal graph flood is clear, so let's start with objects, pointers, and mark-and-sweep.

## Objects, pointers, and mark-and-sweep

GC in Go concerns itself with objects and pointers.

An **object** is a Go value whose underlying memory is allocated from the heap. A **pointer** is a value containing the memory address of another value.

Before going further, it helps to separate the **stack** from the **heap**. Each goroutine has a stack. It holds active function calls and their immediate working data. The part belonging to one function call is its **stack frame**, and when the function returns, that frame is no longer needed. Go can grow and shrink a goroutine's stack while the program is running.

The heap is the area used for values that cannot live only inside one stack frame. Heap storage is managed by the runtime and shared across the program. The garbage collector needs to find heap storage that the program can no longer reach.

Go uses a mark-and-sweep algorithm.

### Mark

Walk the object graph from well-defined roots. Objects are nodes, and pointers are edges.

A **root** is a pointer-bearing location the runtime can inspect directly, without first following another heap object. Marking an object means it has been visited. It also helps prevent going around in cycles forever.

### Sweep

Iterate over all objects. Marked objects are still in use. The unused area occupied by unmarked objects can be returned to the **allocator**, the runtime part that hands out and reuses blocks of memory.

<figure>
  <img
    src="{static}/images/articles/go-green-tea-garbage-collector-diagrams/mark-and-sweep.svg"
    alt="Mark-and-sweep diagram with global and stack roots reaching four live objects, while an unreachable two-object cycle is reclaimed."
    style="width:100%;height:auto;display:block;"
  />
  <figcaption>Marking follows pointers from roots. Sweep reclaims the objects that were not reached.</figcaption>
</figure>

Let's jump a bit more into mark-and-sweep.

Roots are nothing but places the mark phase can use to start the process and find all objects that are reachable. Unlike reference counting, this algorithm is not aware at all times of what needs to be collected. It has to figure it out.

This is basically a **graph flood**. Start from one or more nodes, visit their neighbours, then the neighbours of those neighbours, until there is nowhere new to go. Depth-first search and breadth-first search are two common ways to do it.

## Program work and GC work

To simplify things, there are two things a program is doing:

1. Actual development code being run in one or more threads.
2. Running GC.

The first runs in **mutator threads**, while garbage-collection work runs in GC threads. A mutator is simply the code that mutates the object graph by allocating objects or changing pointers. In Go, this application work normally runs as goroutines scheduled by the runtime onto operating-system threads.

```text
mutator thread -> application code
GC thread      -> GC work
```

In a **stop-the-world** approach, all mutator threads pause and only GC work runs. Go uses short stop-the-world steps, but most marking runs **concurrently**, which means application code and GC work overlap in time. GC work can also run **in parallel**, with several GC workers marking at the same time. Concurrent and parallel mean different things here.

If application code changes a pointer after the GC has inspected part of the graph, it could hide a live object. Go uses a **write barrier**, a small bit of bookkeeping attached to pointer writes, to preserve correctness while pointers change. The exact hybrid barrier is described in [`runtime/mbarrier.go`](https://go.dev/src/runtime/mbarrier.go).

CPython, for example, has a cyclic GC that runs when objects allocated minus objects deallocated reaches a threshold. It also has reference counting, so if an object's reference count goes to zero it can be deallocated immediately. [Python's GC documentation](https://docs.python.org/3.14/library/gc.html) explains the threshold mechanism. The exact defaults vary between CPython releases and collector implementations.

Reference counting stores a count of references to an object. A cycle can keep its own counts above zero even after the rest of the program has lost access to it, so CPython also needs the cyclic collector. Go does not keep a reference count on every object. When a GC cycle begins, it has to find the live objects by tracing from roots.

## Finding the roots

The first step in the mark phase is to find all possible root objects.

Now, this is a bit tricky, as we do not want to do this naively and check everything out there. The runtime starts from locations it already knows may contain pointers:

- **goroutine stacks**, where compiler stack maps say which locations may contain live pointers,
- **global variables**, where compiler and linker metadata says which locations contain pointers,
- **runtime-owned roots**, which are explicitly known to the runtime, such as pointers held by the scheduler or finalizer machinery.

A **stack map** is metadata, often stored compactly as bits, that classifies stack locations as pointers or non-pointers at a particular point in a function. The **linker** is the tool that combines compiled packages into the final executable. It also has the information needed to describe pointer-containing global data.

The compiler identifies memory locations where live pointers may exist at GC safepoints. At runtime, the garbage collector reads the pointer values currently stored in those locations and follows them to the heap.

So, the compiler provides a map of where to look. It does not provide a list of heap objects that will be alive during some future execution.

Consider this example:

```go
type Person struct {
    friend *Person
    age    int
}

var current *Person

func work() {
    x := 42
    p := &Person{age: 42}
    current = p
    use(x, p)
}
```

After `work()` returns, `current` still holds a reference to the `Person`, so it cannot live only in `work`'s stack frame. Otherwise, when that frame goes away, `current` would be left pointing to invalid memory.

Go's **escape analysis** checks whether a value may still be referenced outside the function call that created it. If the compiler cannot prove that the value dies with the call, it can place the value on the heap. The [Go FAQ explains this stack-versus-heap decision](https://go.dev/doc/faq#stack_or_heap).

Escape analysis answers where the value has to be allocated. **Pointer-liveness analysis** answers which pointer-containing locations are still live at a particular point in the program.

Before we dig into it further, we need to talk about safepoints a bit.

## What is a safepoint?

A safepoint is a precise moment or location where a runtime knows enough about a running thread to safely pause, inspect, or modify its execution state. The system knows exactly which memory addresses hold data and which ones hold pointers.

### Why are safepoints needed?

If you think in terms of web apps, there are things we do in the background that are not part of the normal request-response cycle, and usually we have a dedicated cron or machine for them.

Now, for programming languages to perform certain background tasks, they don't have the option of a cron or worker. They do such things by pausing the current application code, and they need to do so safely and reliably.

Some examples:

- **GC:** The GC must scan memory to delete unused items. If a thread modifies memory pointers while GC is scanning, GC might make a decision that could result in a crash.
- **Stack resizing:** When a goroutine runs out of space on its stack, the runtime may pause it, allocate a larger stack, and copy data.
- **Code optimization:** A JIT-based runtime may pause a thread to swap out unoptimized code with highly optimized, freshly compiled machine code.
- **Scheduling:** The runtime may need to preempt a thread or goroutine that has been running for too long.

A **JIT**, or just-in-time compiler, compiles or recompiles code while the program is running, using information from the current execution to optimize it.

A processor executes a function as a sequence of **machine instructions**. While these instructions run, values move between CPU registers and memory. A **CPU register** is a small, very fast storage location inside the processor. A **stack slot** is a fixed location inside a function's stack frame.

Take this function:

```go
func work() {
    p := &Person{}
    process(p)
}
```

After compilation, `p` might currently live in:

- a CPU register,
- a stack slot,
- multiple locations,
- or nowhere.

"Nowhere" means the remaining code will never read `p` again. At that point it is **dead** and no longer needs to be treated as a root.

The GC needs to know which registers and stack slots contain pointers. This isn't possible to calculate at random locations, so at a safepoint it has metadata that may look like:

```text
current instruction: 0x1658
register R12: pointer to Person
register R13: integer, ignore
stack slot 8: pointer to Address
stack slot 9: integer, ignore
```

This metadata is often called a stack map or GC map. It lets the runtime distinguish pointers from **scalar values**, such as integers, which must not be followed as memory addresses. An integer's bits can accidentally look like an address, so this precise metadata matters.

A good comparison is a chess game. After every move, the board is in a valid and understandable state. But while a piece is physically moving, the board is in a temporary state. A safepoint is like waiting until the piece has landed.

## Safepoints and stop-the-world are related but different

When the runtime requests an operation, the sequence may look like this:

1. Threads notice the request.
2. Each thread reaches a safepoint or is already in a safe state.
3. Remaining threads are suspended.
4. The runtime performs the operation.
5. Threads resume.

A safepoint describes where one goroutine can be safely inspected or paused. Stop-the-world is a global application state where all application threads have been stopped or placed into safe states.

Go has three kinds of safepoints, described in [`runtime/preempt.go`](https://go.dev/src/runtime/preempt.go):

1. **Blocked safepoint:** The goroutine is blocked, descheduled, waiting on synchronization, or in a system call.
2. **Synchronous safepoint:** Running code checks whether the runtime has requested preemption.
3. **Asynchronous safepoint:** The runtime interrupts user code at an instruction where its stack and registers can be scanned safely. This can be done by sending a signal.

At blocked and synchronous safepoints, Go has enough information for a precise stack scan. At asynchronous safepoints, it may conservatively inspect stack and register values, meaning it can treat something that looks like a pointer as a possible pointer when it cannot prove otherwise.

Safepoints in Go do more than just GC. They also help the scheduler preempt a goroutine, so one compute-heavy goroutine cannot monopolize an OS thread.

## How HotSpot and V8 use the same idea

Java, Kotlin, Scala, and similar languages inherit safepoint behaviour from the JVM implementation. HotSpot defines a safepoint as a distinguished code location where a thread may block for GC and other VM operations.

The [HotSpot Runtime Overview](https://openjdk.org/groups/hotspot/docs/RuntimeOverview.html) describes a cooperative polling mechanism. A VM thread requests a safepoint, and different Java threads may reach a polling point, a call site, or native code. The JVM waits until all relevant threads are known to be in a safe state.

Java may use a thread-local poll. Keeping poll metadata thread-local simplifies the implementation and avoids shared-state contention.

These polling sites are inserted into generated machine instructions by the JIT compiler. In simple terms, they let a thread ping the VM and ask, "Do you need me for anything?" GC is one of those things.

Now you may ask, "Should I block for a safepoint?" Asking this efficiently is not so simple. Not all state transitions do this. A common interview question is what happens if a safepoint is requested during an extended native transition. The runtime needs enough metadata and rules around those transitions to know whether the thread can be considered safe.

JavaScript programmers do not see safepoints directly, but engines such as V8 use the same underlying concept. V8 maintains safepoint tables for compiled frames and can bring threads with heap access into an isolate-wide or global safepoint operation.

V8 performs significant GC work concurrently, including concurrent marking, but concurrent collection does not eliminate every pause. Some phases still need a consistent view of roots and heap state.

The V8 article [Concurrent marking in V8](https://v8.dev/blog/concurrent-marking) explains the graph-tracing problem using three colours:

- **white:** the object has not been discovered,
- **grey:** the object has been discovered and is waiting to be scanned,
- **black:** the object has been scanned and its outgoing pointers have been followed.

This is called **tri-colour marking**. These colours are logical states, usually stored as bits rather than literal colours. V8's write barrier makes sure pointer changes cannot hide a live white object behind something the collector has already scanned. In its benchmarks, V8 reported that concurrent marking reduced marking time on the main thread by 60-70%.

## Coming back to our code example

Now, coming back to our code example from where we jumped into safepoints:

```go
type Person struct {
    friend *Person
    age    int
}

var current *Person

func work() {
    x := 42
    p := &Person{age: 42}
    current = p
    use(x, p)
}
```

The compiler knows:

- `current` is a global pointer variable,
- `p` is a local pointer variable,
- `x` is a local non-pointer integer.

For each relevant GC safepoint, the compiler performs pointer-liveness analysis. It records which pointer-containing locations in a function frame are live at that point.

```text
location    x    p
is pointer  0    1
```

This does not mean the compiler knows the address pointed to by `p`. It means: at this point, inspect the location that belongs to `p` and do not interpret `x` as a pointer.

The compiler does not normally know the future address of this particular `Person`. This is a runtime property. At one moment:

```text
current -> Person A
Person A.friend -> nil
```

Later:

```text
current -> Person A
Person A.friend -> Person B
Person B.friend -> Person C
```

## The beginning of a GC cycle

Go uses a concurrent mark-and-sweep collector. At the beginning of marking, the runtime briefly stops application execution to establish the marking state and prepare root-scanning work.

Most marking work can then happen concurrently with application goroutines, with write barriers preserving correctness while pointers change.

Root scanning begins from:

- goroutine stacks,
- global variables,
- runtime-managed roots.

The runtime already knows where these regions are. It does not search every arbitrary word of process memory and guess whether it might be a pointer.

In our program, `current` is a global variable. Compiler metadata indicates that `current` is a pointer-containing location in global data.

Let's say at runtime `current` contains `0xA100`:

```text
Global data                Heap
current: 0xA100 ----------> Person at 0xA100
                              friend: nil
                              age: 20
```

If at GC start `current` points to `nil`, then from this root there is nothing to follow to the heap. The metadata says the location can hold a pointer; the current runtime value decides whether it leads anywhere.

The runtime also maintains information about every goroutine and its stack. For example:

```text
main()
  handler()
    work()
```

The goroutine's stack contains one frame for each active call. Each frame has its own pointer map. For each frame, the current **program counter**, the address of the machine instruction being executed, helps the runtime select the pointer map for that point in the function.

A function may have different maps at different points because a pointer can be live during one part of the function and dead later:

```go
p := new(Person)
use(p)

doSomethingElse()
```

While executing `doSomethingElse()`, the compiler may determine that `p` is dead if it is never used again. Its old stack location does not need to be treated as a root.

Returning to the original `work` example:

```text
p       = 0xA100  // inspect as a pointer
current = 0xA100  // inspect as a pointer
x       = 42      // ignore, it is an integer
```

The GC then reads the actual values. Both `p` and `current` lead to the same heap object, so the GC marks that object once.

## Scanning inside the heap object

After discovering the heap object `Person`, the GC must determine whether that object contains more pointers.

Every compiled Go type has **type metadata** describing facts the runtime needs, including which parts of a value contain pointers. The type's pointer-layout metadata says:

```text
field    pointer?
friend   yes
age      no
```

`age` is a scalar value, so the GC ignores it. `friend` may lead to another object.

Suppose later the program does this:

```go
bob := &Person{age: 21}
current.friend = bob
```

The graph is now:

```text
Global root current -> Person A -> friend -> Person B
```

During marking, the GC:

1. Reads `current`.
2. Discovers and marks `Person A`.
3. Scans A's `friend` field.
4. Reads the pointer to `Person B`.
5. Discovers and marks `Person B`.
6. Scans B's `friend` field.
7. Stops if it is `nil`.

Now, let's look at an unreachable cycle. Suppose two objects point to each other:

```text
Person X -> Person Y
    ^          |
    |----------|
```

But no global, stack, or runtime root can reach either object. The traversal never discovers them, so they remain unmarked and can be reclaimed during sweep. Reference counting alone would not reclaim this cycle because each object keeps the other's count above zero.

## The complete process

Now, the complete process has some work happening at compile time and some at runtime.

### Compile time

- Perform escape analysis.
  - Determine that the `Person` assigned to `current` cannot live only in `work`'s stack frame.
- Determine type layout.
  - `Person.friend` is a pointer.
  - `Person.age` is not a pointer.
- Perform pointer-liveness analysis.
  - Record which exact locations contain live pointers at GC safepoints.
- Produce metadata for stack and global pointer locations.

### Runtime: begin GC marking

- Prepare root-scanning work.
- Scan pointer-containing global locations.
  - Read the current value of `current`.
- Walk goroutine stacks.
  - Walk active frames.
  - Select each frame's pointer map.
  - Read the actual live pointer values.
- Include known runtime roots.
- Add discovered heap objects to the marking worklist.

### Runtime: trace the heap

- Mark each discovered object.
- Use its type metadata to find pointer-bearing fields.
- Read those fields.
- Discover additional heap objects.
- Repeat until no new objects remain.

### Sweep

- Marked objects: keep.
- Unmarked objects: reclaim.

Now, as you can see, in this approach we pick one object through a root and explore it end to end. You can imagine it doing so from each root. Hence, it is called graph flooding.

Newly discovered objects wait in a **worklist**. You can implement graph flooding with a stack or a queue:

- a **stack** is LIFO, last in, first out,
- a **queue** is FIFO, first in, first out.

Suppose a root discovers `A`, and scanning `A` discovers `B` and `C`. The GC puts those objects on the worklist. A worker then takes an item, scans it, follows its pointers, and discovers more objects. Go's classic object worklist is approximately stack-like, so the traversal is approximately depth-first.

## The problem with scanning one object at a time

The problem with this is that the next object may happen to live somewhere else in memory.

Imagine three heap pages:

```text
Page A           Page B           Page C
[A1][A2][  ]     [B1][B2][B3]     [C1][C2][  ]
```

A graph walk might jump like this:

```text
A1 -> B2 -> A2 -> C1 -> B3
```

And this is bad for CPU caches, as now the CPU has to fetch a separate memory block for one object and then another block for the next one. A **cache line** is the fixed-size block of nearby bytes moved into the CPU cache together. If the next piece of work uses those nearby bytes, the fetch was useful. If the GC immediately jumps elsewhere, much of that cache line may go unused.

The next address often depends on the pointer read from the current object. This makes it harder for the CPU to predict far enough ahead and hide the wait for memory.

Two terms are useful here:

- **spatial locality:** accessing data close to data that was just accessed,
- **temporal locality:** reusing data or metadata that was accessed recently.

So, the graph flood way pays little attention to where objects live, and substantial time is spent waiting for memory. The [Green Tea proposal](https://github.com/golang/go/issues/73581) reports that, on average, the scan loop used about 85% of GC time and more than 35% of its CPU cycles were spent stalled on memory access.

<figure>
  <img
    src="{static}/images/articles/go-green-tea-garbage-collector-diagrams/object-worklist-vs-span-worklist.svg"
    alt="Side-by-side comparison of a classic last-in-first-out object worklist scanning one object in changing spans and a Green Tea first-in-first-out span worklist scanning several nearby objects together."
    style="width:100%;height:auto;display:block;"
  />
  <figcaption>The classic worklist follows objects. Green Tea gives nearby work time to collect on a span.</figcaption>
</figure>

Let's take another example to understand how Green Tea does it differently.

## How Green Tea changes the worklist

Let's say we have two pages:

```text
Page A: [A1][A2][A3][A4]
Page B: [B1][B2][B3][B4]

Root -> A1 -> B2 -> A3 -> B4
```

The normal object worklist starts with `[A1]`.

Green Tea records work at the page or span level. Now, suppose the root discovers `A1`. Instead of queuing `[A1]`, it records `A1` as seen on Page A and queues Page A.

The talk uses the word **page** in its diagrams. The runtime calls this allocation unit a **span**. A span is a contiguous region managed by Go's heap allocator. It contains objects from one **size class**, meaning objects with the same rounded allocation size are grouped together.

A span is always a multiple of 8 KiB and aligned to 8 KiB. The small-object span path described by the Green Tea design uses spans that are exactly 8 KiB and contain objects up to 512 bytes. This is Go's runtime allocation page size, which does not have to match the operating system's page size.

Keeping one size class in a span gives the runtime a regular layout. Once it knows the span and object index, it can find the object and its metadata using simple address arithmetic.

So, Green Tea records:

```text
Span A
seen: A1
span queue: [Span A]
```

Then it processes Span A and scans `A1`. `A1` points to `B2`, so Green Tea records:

```text
Span B
seen: B2
span queue: [Span B]
```

So far, you'd say not much has changed. The improvement shows up when multiple reachable objects accumulate on the same span.

Suppose the roots and other scans discover `A1`, `A3`, `A4`, and `B2`:

```text
Span A: A1, A3, A4
Span B: B2
```

Green Tea uses a more queue-like scheduling strategy for spans. Suppose Span A is waiting in the queue. While it waits, other GC workers discover `A3`, `A4`, and `A7`. Instead of adding three new independent objects to a global worklist, Green Tea accumulates them on Span A. Then a worker can scan them in a single pass through the span.

Green Tea uses FIFO order for spans instead of the classic LIFO-like object order. It also tried LIFO, random, address-ordered, sparsest-first, and densest-first. FIFO accumulated the highest average amount of useful work by the time a span was taken from the queue.

Queuing spans also means there are fewer items to exchange between workers. If one span represents three pending objects, the shared work machinery tracks one span instead of three object pointers. This reduces **contention**, where workers delay one another because they need to update the same shared state, especially on systems with many CPU cores.

<figure>
  <img
    src="{static}/images/articles/go-green-tea-garbage-collector-diagrams/green-tea-span-flow.svg"
    alt="Flow diagram showing a discovered pointer setting a mark bit, queuing its 8 KiB span, accumulating nearby objects, computing marks minus scans, and scanning the pending objects together."
    style="width:100%;height:auto;display:block;"
  />
  <figcaption>A span is queued once, while more objects on it can be discovered before scanning.</figcaption>
</figure>

## What's seen versus scanned here?

Green Tea still needs to know the exact state of each object:

- **seen:** Have we discovered this object as reachable?
- **scanned:** Have we looked inside the object and followed its outgoing pointers?

Take this graph:

```text
Root -> A -> B -> C
```

At the beginning:

```text
object  seen  scanned
A       0     0
B       0     0
C       0     0
```

The root points to `A`, so the GC discovers `A`:

```text
A       1     0
```

`A` is alive but still has to be inspected. Then the GC scans `A` and finds a pointer to `B`:

```text
A       1     1
B       1     0
```

Then `B` leads to `C`, and so on. On a span, the difference between the seen and scanned bits tells Green Tea which objects still need work. In the tri-colour terms used by the implementation, these correspond to grey and black bits.

The GC can therefore batch nearby objects without losing the object-level state needed for a correct graph traversal.

There is also a case where only one object is ready when a span comes off the queue. Doing all the span bookkeeping for one object could cost more than the old object path. Green Tea tracks the object that caused the span to be queued as its **representative**. If no second object is marked while the span waits, the GC scans that representative directly. Larger objects continue through the classic object-scanning path.

## Where Green Tea stands now

At the time of this talk, Green Tea was available as an experiment in Go 1.25, and the plan was to enable it by default in Go 1.26. It is now enabled by default in [Go 1.26](https://go.dev/doc/go1.26#new-garbage-collector).

The release notes say that results depend on the workload, but for real-world programs that use GC heavily, Green Tea can reduce GC overhead by 10-40%.

So, overall, the way GC finds reachable objects has not changed. It still starts from roots, uses compiler and type metadata, and follows the pointers. What Green Tea changes is how that work is grouped. Instead of scanning one object at a time across different parts of memory, it accumulates objects on the same span and scans them together.

## References

- [GopherCon 2025: Advancing Go Garbage Collection with Green Tea](https://www.youtube.com/watch?v=gPJkM95KpKo)
- [Go 1.26 release notes: New garbage collector](https://go.dev/doc/go1.26#new-garbage-collector)
- [Green Tea design and implementation discussion](https://github.com/golang/go/issues/73581)
- [A Guide to the Go Garbage Collector](https://go.dev/doc/gc-guide)
- [Go runtime safepoint and preemption notes](https://go.dev/src/runtime/preempt.go)
- [Go runtime write-barrier notes](https://go.dev/src/runtime/mbarrier.go)
- [Go FAQ: stack or heap](https://go.dev/doc/faq#stack_or_heap)
- [Python 3.14 garbage-collector interface](https://docs.python.org/3.14/library/gc.html)
- [Concurrent marking in V8](https://v8.dev/blog/concurrent-marking)
- [OpenJDK HotSpot Runtime Overview](https://openjdk.org/groups/hotspot/docs/RuntimeOverview.html)

<div class="article-subtext article-subtext--ai">
  <p class="article-subtext-label">AI writing disclaimer</p>
  <ul>
    <li>I used Codex with OCR to convert my handwritten notes into text and check the grammar, then reviewed the article.</li>
    <li>Technical details were checked against the GopherCon talk, Go runtime sources, Go 1.26 release notes, V8 documentation, and the HotSpot runtime overview.</li>
    <li>The diagrams were created with the tldraw offline canvas with help from Codex.</li>
  </ul>
</div>
