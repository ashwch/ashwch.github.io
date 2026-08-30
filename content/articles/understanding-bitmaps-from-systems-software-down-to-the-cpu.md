Title: Understanding Bitmaps
Date: 2026-08-30
Modified: 2026-08-30
Status: published
Category: Programming
Tags: bitmaps, bitwise-operations, systems-programming, databases, filesystems, garbage-collection, linux, cpu
Slug: understanding-bitmaps-from-systems-software-down-to-the-cpu
Authors: Ashwini Chaudhary
Summary: A bitmap is a compact array of yes or no. The position tells you what each answer refers to, and the same idea appears in images, filesystems, garbage collection, database indexes, CPU sets, and CPU instructions.

## Where the word bit came from

The likely source of the modern term is Claude Shannon's 1948 paper, [*A Mathematical Theory of Communication*](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf).

While describing base-2 units of information, Shannon wrote that they "may be called binary digits, or more briefly bits," and credited John W. Tukey with suggesting the word.

I also recommend watching David Senra's video, [How Claude Shannon Invented The Future](https://youtu.be/I2nCGnoNCvk).

As the name suggests, a bitmap is a compact array of yes or no, where the position tells you what answer each position refers to.

```text
position  0 1 2 3 4 5
bit       1 0 1 0 0 1
```

Here, position is the identity and bit is the state. In different contexts, `1` and `0` could mean different things:

```text
0 = free          1 = occupied
0 = unreachable   1 = reachable
0 = off           1 = on
0 = white         1 = black
```

Why "map"? It is because every bit position is mapped to something in another domain:

```text
seat map   bit 0 -> seat 1
           bit 1 -> seat 2
           bit 2 -> seat 3

GC         bit 0 -> object slot 0
           bit 1 -> object slot 1
           bit 2 -> object slot 2

image      bit 0 -> pixel (0, 0)
           bit 1 -> pixel (1, 0)
           bit 2 -> pixel (2, 0)
```

## A bitmap is an ideal representation of a subset

Suppose the complete set is:

```text
U = {0, 1, 2, 3, 4, ..., 8}
```

And our subset is:

```text
S = {1, 2, 5}
```

The bitmap of `S` is:

```text
item     0 1 2 3 4 5 6 7 8
present  0 1 1 0 0 1 0 0 0
```

This makes them very suitable for systems programming:

- Which pages are free?
- Which objects are reachable?
- Which rows match a condition?
- Which pixels are covered by a shape?

A CPU does not normally load one bit directly from memory, though. It loads bytes and words. A word used for bitmap operations is commonly 64 bits, or 8 bytes, on a 64-bit system. Memory is normally addressed in bytes. A CPU request for bit 138 alone would still require the word that contains it, so it loads the whole word and inspects the bit.

Suppose a bitmap has 192 bits, stored as three 64-bit words:

```text
word 0  -> bits   0-63
word 1  -> bits  64-127
word 2  -> bits 128-191
```

```text
138 / 64   -> word 2
138 mod 64 -> bit position 10
```

So load word 2 and check its tenth bit position.

## How does a CPU check whether that bit is set?

It uses a mask.

A mask is another binary number where we put a `1` in the position we care about. If we only care about bit 3, create `00001000`.

```text
value  10110110
mask   00001000
AND    00000000
```

The zero means bit 3 was missing from the value.

A mask is usually represented using `1 << n`.

Start with one:

```text
00000001
```

Shift the one left by the target position:

```text
1 << 1 -> 00000010
1 << 2 -> 00000100
1 << 3 -> 00001000
```

AND with a mask lets the selected value through if it was present; otherwise it does not.

How to turn on a bit? Use OR with the mask. `0 OR 1 -> 1`; `1 OR 1 -> 1`. This forces the selected bit to `1`, and the other bits are left as they were because the mask has zeroes there.

How to turn off a bit? Use AND with the NOT of the mask. At the selected bit, zero clears the value. Everywhere else, one preserves it.

How to toggle a bit? XOR the word with the mask.

```text
1 XOR 1 -> 0
0 XOR 1 -> 1
0 XOR 0 -> 0
1 XOR 0 -> 1
```

A one in the mask toggles the selected position. Apply the same XOR mask again and it toggles back.

Here are the same operations in Go:

```go
wordIndex := position / 64
bitOffset := position % 64
mask := uint64(1) << bitOffset

isSet := bitmap[wordIndex]&mask != 0 // check
bitmap[wordIndex] |= mask            // turn on
bitmap[wordIndex] &^= mask           // turn off
bitmap[wordIndex] ^= mask            // toggle
```

Go's [`&^` operator](https://go.dev/ref/spec#Arithmetic_operators) means bit clear. It performs `word AND NOT mask`.

<figure>
  <img
    src="{static}/images/articles/understanding-bitmaps-diagrams/bitmap-positions-and-masks.svg"
    alt="A 192-bit bitmap split into three 64-bit words, with position 138 mapped to word 2 and offset 10 before one mask is used to test, set, clear, or toggle the bit."
    style="width:100%;height:auto;display:block;"
  />
  <figcaption>The CPU loads the whole word and inspects the bit.</figcaption>
</figure>

Now, back to where we were.

## A bitmap image is one special bitmap

Consider a monochrome image as rows and columns. Its width is the number of columns.

```text
         x
       0 1 2 3 4

y = 0  0 0 1 0 0
y = 1  0 1 0 1 0
y = 2  1 0 0 0 1
y = 3  1 1 1 1 1
```

Memory is not going to store the image as a table, so it is stored as a one-dimensional bitmap.

For an image of width `W`, the pixel at `(x, y)` is at:

```text
position = y * W + x
```

For width 5, `(1, 1)` is at `5 * 1 + 1 = 6`, as expected.

Monochrome images have one bit per pixel, so two possible values: `0` and `1`.

- **8 bits per pixel:** 256 possible values
- **24 bits per pixel:** 16,777,216 RGB combinations
- **32 bits per pixel:** often RGB plus transparency

The exact channel layout depends on the image format.

## Application: storage allocation

Imagine a disk with blocks 0, 1, 2, 3, 4, 5, 6, and so on. A bitmap lets the filesystem immediately tell that a block is occupied or free.

```text
block     0 1 2 3 4 5 6 7
in use    1 1 0 1 0 1 0 0
```

To allocate a block, change its zero bit to one. To release the block, change it back to zero.

In Linux's ext4 filesystem, a data-block bitmap tracks which data blocks in a block group are in use, while an inode bitmap tracks which inode-table entries are in use.

A **block group** is a region that keeps related filesystem data and metadata together. An **inode** is the filesystem record that stores metadata about a file or directory, including its type, permissions, size, and where its data lives. The [ext4 bitmap documentation](https://www.kernel.org/doc/html/latest/filesystems/ext4/bitmaps.html) describes the one-bit-per-block and one-bit-per-inode mapping.

A bitmap lookup for a known block is constant time once the relevant word is available. Finding any free block may require scanning words until a zero is found. Real filesystems can keep other allocation data and hints so they do not always start a blind scan from the beginning.

## Application: garbage collection

This is particularly relevant to Go. Suppose a span contains eight object slots. Allocation and marking can each be represented by bits:

```text
slot       0 1 2 3 4 5 6 7
allocated  1 1 1 0 1 0 0 0
marked     1 0 1 0 1 0 0 0
```

An allocated object that was not marked can be swept and its memory reclaimed. In this example, that is the object in slot 1.

This is a great example of several bitmaps maintained over the same memory to decide various things:

- **Allocation bitmap:** Is there an object in this slot?
- **Mark bitmap:** Was the object found reachable during the GC cycle?
- **Scan bitmap:** Have the object's outgoing pointers been scanned?
- **Pointers bitmap:** Which fields inside an object may contain pointers?

These bitmaps do not always live for the same amount of time or map the same unit. Allocation, mark, and scan bits can map object slots. Pointer-layout bits map locations inside an object.

Go's runtime has an `allocBits` bitmap for the allocation state of objects in a span and `gcmarkBits` for marking. The comments in [`runtime/mheap.go`](https://go.dev/src/runtime/mheap.go) describe the exact mapping: object `n` uses bit `n`, and its address can be calculated from the span base, object index, and object size.

In the Green Tea collector, eligible small-object spans have separate `marks` and `scans` arrays. The runtime calculates `marks &^ scans` to find reachable objects whose pointers still need scanning. Pointer-layout masks then tell the scanner which words inside those objects are pointers. The implementation is in [`runtime/mgcmark_greenteagc.go`](https://go.dev/src/runtime/mgcmark_greenteagc.go).

I covered the complete marking flow in [How Green Tea Made Go's Garbage Collector More Cache-Friendly](/how-green-tea-made-go-garbage-collection-more-cache-friendly.html).

## Application: database indexes

Suppose a table has eight rows. A bitmap can represent each condition:

```text
row              0 1 2 3 4 5 6 7
country = CA     1 0 0 1 0 1 0 0
active = true    1 1 0 1 0 1 1 0
plan = premium   0 0 1 1 0 1 0 0
```

A condition like `country = CA AND active = true AND plan = premium` is an AND over all three bitmaps:

```text
country = CA      1 0 0 1 0 1 0 0
active = true     1 1 0 1 0 1 1 0
plan = premium    0 0 1 1 0 1 0 0
                  -----------------
result             0 0 0 1 0 1 0 0
```

Only rows 3 and 5 match.

These diagrams list position 0 on the left so each bit sits under its row ID. When a binary integer is printed as a number, bit 0 is normally shown on the right. That display choice does not change the mapping.

<figure>
  <img
    src="{static}/images/articles/understanding-bitmaps-diagrams/bitmap-index-intersection.svg"
    alt="Three eight-row database bitmaps for country, active status, and plan combined with bitwise AND, leaving only row IDs 3 and 5."
    style="width:100%;height:auto;display:block;"
  />
  <figcaption>A condition like this is an AND over all three bitmaps. Only rows 3 and 5 match.</figcaption>
</figure>

It is time to look at bitmap indexes a bit.

Suppose we have a customers table with row ID, name, and gender. Gender only ever has two possible values in this simplified example, `M` or `F`:

```text
row ID  name      gender
0       Alice     F
1       Bob       M
2       Carol     F
3       Dan       M
4       Shrey     M
5       Saurabh   M
6       Daksh     M
7       Surbhi    F
```

If we used a B-tree index, each value would lead to row IDs. `F` leads to rows 0, 2, and 7. `M` leads to rows 1, 3, 4, 5, and 6.

Given that both `F` and `M` occur often, everyone is at the leaf. In other words, either value leads to a large range of leaf entries. The tree finds the value quickly, but the scan is still heavily sequential and may not provide much benefit because many table rows still need to be fetched.

<figure>
  <img
    src="{static}/images/articles/understanding-bitmaps-diagrams/low-cardinality-b-tree.svg"
    alt="A simplified B-tree index on gender, where an internal page separates F and M leaf ranges and a query for F still fetches rows 0, 2, and 7."
    style="width:100%;height:auto;display:block;"
  />
  <figcaption>The tree finds the value quickly, but many table rows still need to be fetched.</figcaption>
</figure>

A bitmap index looks at it differently:

```text
row  0 1 2 3 4 5 6 7
F    1 0 1 0 0 0 0 1
M    0 1 0 1 1 1 1 0
```

The bitmap position tells us instantly whether row 4 has `F = 0` or `1`.

Bitmap indexes create a separate bitmap for each unique value. Hence, it makes sense to use them when the number of unique values is low but the row count is high. The number of unique values is also called **cardinality**.

You may argue this is still a lot of scanning. Nevertheless, compare it to a B-tree index when we add more conditions.

Add a country column with `CA` and `US`.

Now there are bitmaps for `F`, `M`, `CA`, and `US`.

Query: where `gender = F AND country = CA`.

AND the `F` and `CA` bitmaps. The CPU can load these bitmaps in chunks and AND them.

Add more columns and conditions, and it still remains the same bitmap arithmetic.

With B-tree indexes, one option is to use one index first, fetch matching row IDs, then inspect those rows for the other condition. Another option is to scan multiple B-tree indexes and build bitmap sets from their results.

For example:

```text
gender B-tree  -> rows 0, 2, 7
country B-tree -> rows 0, 3, 4
```

The database intersects those sets.

<figure>
  <img
    src="{static}/images/articles/understanding-bitmaps-diagrams/combining-separate-b-tree-indexes.svg"
    alt="Separate gender and country B-tree indexes returning row ID sets that the database intersects to find row 0."
    style="width:100%;height:auto;display:block;"
  />
  <figcaption>The database scans both B-tree indexes, builds bitmap sets from their results, and intersects those sets.</figcaption>
</figure>

The B-tree structure itself has no intrinsic support for `index A AND index B` across separate single-column indexes. A database can build temporary bitmap sets as described above. A multicolumn B-tree can help for a known combination.

Oracle documents the direct bitmap case clearly: [`AND` and `OR` conditions can be performed on the bitmaps before converting the result to row IDs](https://docs.oracle.com/en/database/oracle/oracle-database/19/dwhsg/data-warehouse-optimizations-techniques.html#GUID-7BD561A9-6B28-43A6-A5E0-B9AF196CF251).

Coming back to how bitmaps are stored by a database, Oracle does not store the entire table as one giant bitmap where bit 1038 means row ID 1038. It stores chunks, and each chunk is tied to a range of actual Oracle row IDs.

A simplified chunk can have a start row ID, an end row ID, and a bitmap. The bitmap only describes rows within that range, where each bit is an offset:

```text
key:          Stock Clerk
start rowid:  AAAPzRAAFAAAABSAAd
end rowid:    AAAPzRAAFAAAABSAAt
bitmap:       0101001001
```

This row ID representation is an oversimplification because Oracle does more to find the actual row from a row ID. The same key can also have several chunks for different row ID ranges, and Oracle compresses their bitmaps. The [Oracle bitmap storage documentation](https://docs.oracle.com/en/database/oracle/oracle-database/19/cncpt/indexes-and-index-organized-tables.html#GUID-AB4829E0-C1B7-4554-9ECB-7CCB7A992FE9) goes into those details.

Updating a bitmap index: a single row change from `M` to `F` requires toggling it in both the `M` and `F` bitmaps. Such things are rarely ever done bit by bit. Oracle locks the relevant bitmap-index entry, and that entry covers a range of rows. Another transaction trying to update other rows covered by that entry can be affected until the first transaction commits.

This is why bitmap indexes fit data warehouses, where queries are common and concurrent updates are relatively rare. [Oracle says](https://docs.oracle.com/en/database/oracle/oracle-database/19/dwhsg/data-warehouse-optimizations-techniques.html#GUID-76BAA645-A219-4FF5-AFD4-B6FA8C1473FB) they are not suitable for many high-concurrency OLTP workloads.

## Application: OS CPU sets

Linux's `cpumask` is a bitmap whose indices correspond to CPUs. The kernel uses CPU masks for identifying CPU affinity, scheduling, online state, idle state, and similar sets.

For example, CPU 2 and CPU 4 may be available choices for performing a task:

```text
CPU             0 1 2 3 4 5 6 7
online          1 1 1 1 1 0 0 0
allowed for job 0 0 1 0 1 0 0 0
```

The kernel keeps system CPU maps such as `cpu_possible_mask`, `cpu_present_mask`, and `cpu_online_mask`. A thread also has a CPU-affinity mask. Its actual choices are the intersection of that mask, the CPUs currently available to the scheduler, and any further cpuset restrictions. The [Linux CPU hotplug documentation](https://www.kernel.org/doc/html/latest/core-api/cpu_hotplug.html#cpu-maps) and [`sched_setaffinity(2)` manual page](https://man7.org/linux/man-pages/man2/sched_setaffinity.2.html) describe those masks.

Linux stores CPU masks as arrays of 64-bit `unsigned long` values on typical 64-bit systems, or 32-bit words on typical 32-bit systems. A 256-CPU mask can look like:

```text
word 0 -> CPUs   0-63
word 1 -> CPUs  64-127
word 2 -> CPUs 128-191
word 3 -> CPUs 192-255
```

## How do things actually work at CPU level?

We briefly touched on the fact that in Linux, `cpumask` and other bitmaps are essentially arrays of `unsigned long` integers. Now it is time to understand how the operations happen under the hood.

A 256-bit bitmap on a 64-bit machine can be stored as four 64-bit integers:

```text
bitmap[0] -> bits   0-63
bitmap[1] -> bits  64-127
bitmap[2] -> bits 128-191
bitmap[3] -> bits 192-255
```

For word-wise bitmap operations, a CPU does not perform one instruction per bit. Inside one 64-bit word, the CPU processes all 64 bit positions together.

```text
result[63] = left[63] AND right[63]
result[62] = left[62] AND right[62]
...
result[0]  = left[0]  AND right[0]
```

All 64 bit positions are processed together. Hence, operations like `bitmap_and`, `bitmap_or`, and `bitmap_xor` operate over words in Linux and other systems.

For a bitmap longer than one word, software can loop over the words:

```go
for wordIndex := range result {
    result[wordIndex] = left[wordIndex] & right[wordIndex]
}
```

The RISC-V specification gives us one concrete example. In RV64I, integer registers are 64 bits. Its `AND`, `OR`, and `XOR` instructions perform bitwise logical operations on two source registers and write the result to a destination register. See the [RV64I register width](https://docs.riscv.org/reference/isa/v20260120/unpriv/rv64.html#3-1-1-register-state) and [base integer logical instructions](https://docs.riscv.org/reference/isa/v20260120/unpriv/rv32.html#1-1-4-2-integer-register-register-instructions).

## A simple ALU and multiplexer

At a lower level, a processor contains transistors arranged to perform AND, OR, XOR, addition, and so on.

Imagine a very simple one-bit ALU with AND, OR, XOR, and ADD circuits. In a simple design, when `A` and `B` arrive, it may produce all four results. We are looking for only one of them, so a multiplexer circuit selects one result.

A MUX is an electrically controlled selector. It accepts the AND, OR, XOR, and ADD results, and an operation-select input chooses the result.

Where does this information come from, though?

Assume this encoding for our simple example:

```text
00 -> AND
01 -> OR
10 -> XOR
11 -> ADD
```

An instruction in memory has fields such as operation, destination, input A, and input B. The CPU fetches the instruction and sends its operation bits into an instruction decoder. The decoder produces control signals. For operation `10`, XOR selected is `1` and the others are `0`.

The decoder itself is nothing but gates. For four supported instruction codes, selection signals can be constructed from `op1` and `op0`:

```text
AND selected = NOT op1 AND NOT op0
OR selected  = NOT op1 AND op0
XOR selected = op1 AND NOT op0
ADD selected = op1 AND op0
```

For XOR, operation bits are `10`:

```text
1 AND NOT 0
= 1 AND 1
= 1
```

The decoder outputs `AND=0`, `OR=0`, `XOR=1`, and `ADD=0`, and the MUX selects the XOR output.

This is a teaching model, not a claim that every modern processor has four complete results waiting behind one literal MUX. The instruction set defines the required result. The CPU designer decides how to build it.

Suppose the requested operation was AND on a 64-bit machine:

```text
AND register C, register A, register B
C = A AND B
```

The instruction decoder tells the execution unit this is an AND operation, and the logical result is routed to the destination register.

All 64 positions are ANDed at once in the processor.

Do modern CPUs calculate all results regardless of what the multiplexer picks? They can. A small textbook ALU may calculate all four candidates and simply not select the unused results. A real CPU can share circuitry, split the work into stages, or use a different design. There is no general rule that every CPU calculates all four results every time.

## Step-by-step path for `word & mask`

```text
result = word AND mask
```

Assume the operands are runtime values and the compiler cannot remove the operation. The compiler turns it into an AND machine instruction.

1. CPU fetches the instruction bits.
2. Decoder recognizes the AND opcode.
3. Source-register numbers identify `word` and `mask`.
4. Register file supplies the two 64-bit values.
5. Scheduler sends the operation to an ALU capable of AND.
6. Control signals select logical-AND behaviour.
7. A 64-bit result appears.
8. A register captures the result.

<figure>
  <img
    src="{static}/images/articles/understanding-bitmaps-diagrams/cpu-bitwise-and-path.svg"
    alt="A simplified CPU path from machine instruction through decoder, register file, scheduler, available ALU, a 64-bit AND operation, and the destination register."
    style="width:100%;height:auto;display:block;"
  />
  <figcaption>The instruction scheduler sends the decoded AND operation to an available ALU.</figcaption>
</figure>

Modern CPUs can have several execution units: ALUs, multiply units, load/store units, vector units, and floating-point units.

After decoding, an instruction may become an internal operation, often called a [micro-operation](https://en.wikipedia.org/wiki/Micro-operation), or `µop` (`uop` in plain text).

For a decoded AND operation, an instruction scheduler may find ALU 0 busy, ALU 1 available, and ALU 2 busy, then send it to ALU 1.

Inside the chosen execution unit, operation-control signals select the correct behaviour. For inputs `A` and `B`, every bit pair goes through a logical AND at once, and the output is sent to the destination register.

An x86 instruction may decode into one or more micro-operations, while a simpler instruction in another architecture may map more directly to an execution operation. The exact path depends on the processor.

## References

- [Go specification: arithmetic and bitwise operators](https://go.dev/ref/spec#Arithmetic_operators)
- [Linux ext4: block and inode bitmaps](https://www.kernel.org/doc/html/latest/filesystems/ext4/bitmaps.html)
- [Go runtime span allocation and mark bitmaps](https://go.dev/src/runtime/mheap.go)
- [Go runtime Green Tea mark and scan bitmaps](https://go.dev/src/runtime/mgcmark_greenteagc.go)
- [Go runtime heap pointer-layout metadata](https://go.dev/src/runtime/mbitmap.go)
- [Oracle: data warehousing optimizations and bitmap indexes](https://docs.oracle.com/en/database/oracle/oracle-database/19/dwhsg/data-warehouse-optimizations-techniques.html#GUID-76BAA645-A219-4FF5-AFD4-B6FA8C1473FB)
- [Oracle: bitmap index storage structure](https://docs.oracle.com/en/database/oracle/oracle-database/19/cncpt/indexes-and-index-organized-tables.html#GUID-AB4829E0-C1B7-4554-9ECB-7CCB7A992FE9)
- [Linux CPU hotplug: CPU maps](https://www.kernel.org/doc/html/latest/core-api/cpu_hotplug.html#cpu-maps)
- [Linux `sched_setaffinity(2)` manual page](https://man7.org/linux/man-pages/man2/sched_setaffinity.2.html)
- [Claude Shannon: A Mathematical Theory of Communication](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf)
- [RISC-V RV64I base integer instruction set](https://docs.riscv.org/reference/isa/v20260120/unpriv/rv64.html)
- [RISC-V integer register-register instructions](https://docs.riscv.org/reference/isa/v20260120/unpriv/rv32.html#1-1-4-2-integer-register-register-instructions)

<div class="article-subtext article-subtext--ai">
  <p class="article-subtext-label">AI writing disclaimer</p>
  <ul>
    <li>I used Codex with OCR to convert my handwritten notes into text and check the grammar, then reviewed the article.</li>
    <li>Technical details were checked against Go runtime sources, Linux kernel documentation, Oracle documentation, Shannon's paper, and the RISC-V specification.</li>
    <li>The diagrams were created with the tldraw offline canvas with help from Codex.</li>
  </ul>
</div>
