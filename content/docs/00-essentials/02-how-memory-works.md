---
title: "How Memory Works"
weight: 2
---


Programs store values in memory and use addresses to find those values. Data structures organize
those values so common operations require fewer moves, comparisons, or allocations.

An address identifies a location in an address space; it does not guarantee that the same amount of
physical RAM is installed. A 32-bit address space can represent at most \(2^{32}\) distinct byte
addresses (4 GiB), while a 64-bit address space can represent far more. [Operating systems](../05-cloud-devops/03-operating-systems-kernel-mechanics/02-virtual-memory-kernel-traps.md), hardware,
permissions, and available physical memory limit what a process can actually use.
Think of memory as numbered byte locations. An [array](../01-algorithms/01-linear-data-structures/01-dynamic-arrays.md) stores adjacent elements, so the address of an
element can be calculated from its start address and index. A [linked list](../01-algorithms/01-linear-data-structures/02-linked-lists.md) stores nodes wherever space
is available and follows references from one node to the next.

![Vertical process memory layout showing stack, heap, static data, literals, instructions, and a stack pointer referencing heap memory](/images/memory-layout.svg)

| Power of 2 | Size |
| --- | --- |
| \(2^1\) | 2 |
| \(2^2\) | 4 |
| \(2^3\) | 8 |
| \(2^4\) | 16 |
| \(2^5\) | 32 |
| \(2^6\) | 64 |
| \(2^7\) | 128 |
| \(2^8\) | 256 |
| \(2^9\) | 512 |
| \(2^{10}\) | 1024 |
| \(2^{11}\) | 2048 |
| \(2^{12}\) | 4096 |
| \(2^{13}\) | 8192 |
| \(2^{14}\) | 16,384 |
| \(2^{15}\) | 32,768 |
| \(2^{16}\) | 65,536 |

Powers of two are useful because binary address calculations and capacity growth naturally use them.
For example, \(2^{10}=1024\) bytes and \(2^{20}=1,048,576\) bytes.

## Common Java value types

| Data types | Java keyword or wrapper | Memory value | Java value | Explanation |
| --- | --- | --- | --- | --- |
| Boolean | boolean or Boolean | language-dependent | true or false | `Boolean` is a reference type; object layout is not one bit |
| Byte (whole number) | byte or Byte | 1 byte (8 bits) | -128 to 127 | 8 bits signed = \(-2^7\) up to \(2^7 - 1\) |
| Short Integer | short or Short | 2 bytes (16 bits) | -32,768 to 32767 | 16 bits signed = \(-2^{15}\) up to \(2^{15} - 1\) |
| Character (UTF-16 code unit) | char or Character | 2 bytes for `char` | 0 to 65,535 | A Unicode code point may require one or two UTF-16 code units |
| Integer (whole number) | int or Integer | 4 bytes (32 bits) | -2,147,483,648 to 2,147,483,647 | 32 bits signed = \(-2^{31}\) up to \(2^{31} - 1\) |
| Floating number | float or Float | 4 bytes | about 6 to 7 decimal digits | IEEE 754 binary32 approximation |
| Long (long integer whole number) | long or Long | 8 bytes (64 bits) | -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807 | 64 bits signed = \(-2^{63}\) up to \(2^{63} - 1\) |
| Double (double precision floating number) | double or Double | 8 bytes | about 15 to 16 decimal digits | IEEE 754 binary64 approximation |

Primitive sizes describe the value representation, not necessarily the full memory consumed by an
object. Object headers, references, alignment, and the garbage collector add runtime overhead.

## Common value types by language

```java
boolean flag    = true;    // JVM-dependent size, true to false
byte    small   = 1;       // 1 byte, -128 to 127
short   medium  = 100;     // 2 bytes, -32,768 to 32,767
int     whole   = 1000;    // 4 bytes, -2,147,483,648 to 2,147,483,647
long    large   = 100000L; // 8 bytes, -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807
float   ratio   = 0.5f;    // 4 bytes, about -3.4e38 to 3.4e38
double  precise = 0.5;     // 8 bytes, about -1.8e308 to 1.8e308
char    letter  = 'A';     // 2 bytes, 0 to 65,535 UTF-16 code units

Boolean    flagObject    = Boolean.TRUE;             // wrapper object, true to false; total size runtime-dependent
Byte       smallObject   = Byte.valueOf((byte) 1);    // 1-byte value, -128 to 127; object overhead runtime-dependent
Short      mediumObject  = Short.valueOf((short) 100); // 2-byte value, -32,768 to 32,767; object overhead runtime-dependent
Integer    wholeObject   = Integer.valueOf(1000);    // 4-byte value, -2,147,483,648 to 2,147,483,647; object overhead runtime-dependent
Long       largeObject   = Long.valueOf(100000L);    // 8-byte value, -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807; object overhead runtime-dependent
Float      ratioObject   = Float.valueOf(0.5f);     // 4-byte value, about -3.4e38 to 3.4e38; object overhead runtime-dependent
Double     preciseObject = Double.valueOf(0.5);      // 8-byte value, about -1.8e308 to 1.8e308; object overhead runtime-dependent
Character  letterObject  = Character.valueOf('A');  // 2-byte value, 0 to 65,535 UTF-16 code units; object overhead runtime-dependent
String     textObject    = "value";                  // object, implementation-dependent size; not a numeric wrapper
```

```c
#include <stdbool.h>
#include <stdint.h>

bool          flag    = true;    // 1 byte, false to true
int8_t        small   = 1;       // 1 byte, -128 to 127
int16_t       medium  = 100;     // 2 bytes, -32,768 to 32,767
int32_t       whole   = 1000;    // 4 bytes, -2,147,483,648 to 2,147,483,647
int64_t       large   = 100000;   // 8 bytes, -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807
float         ratio   = 0.5f;    // 4 bytes, about -3.4e38 to 3.4e38
double        precise = 0.5;     // 8 bytes, about -1.8e308 to 1.8e308
unsigned char letter  = 'A';     // 1 byte, 0 to 255
```

```python
flag: bool     = True    # runtime-dependent size, False to True
small: int     = 1       # runtime-dependent size, unbounded integer
whole: int     = 1000    # runtime-dependent size, unbounded integer
ratio: float   = 0.5     # usually 24 bytes, about -1.8e308 to 1.8e308
precise: float = 0.5     # usually 24 bytes, about -1.8e308 to 1.8e308
text: str      = "value" # runtime-dependent size, no numeric range
```

```rust
let flag: bool    = true;    // 1 byte, false to true
let small: i8     = 1;       // 1 byte, -128 to 127
let medium: i16   = 100;     // 2 bytes, -32,768 to 32,767
let whole: i32    = 1000;    // 4 bytes, -2,147,483,648 to 2,147,483,647
let large: i64    = 100000;  // 8 bytes, -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807
let ratio: f32    = 0.5;     // 4 bytes, about -3.4e38 to 3.4e38
let precise: f64  = 0.5;     // 8 bytes, about -1.8e308 to 1.8e308
let letter: char  = 'A';     // 4 bytes, 0 to 1,114,111 Unicode scalar values
```

```typescript
const flag: boolean    = true;     // runtime-dependent size, false to true
const small: number    = 1;        // usually 8 bytes, safe integer -9,007,199,254,740,991 to 9,007,199,254,740,991
const whole: number    = 1000;     // usually 8 bytes, safe integer -9,007,199,254,740,991 to 9,007,199,254,740,991
const large: bigint    = 100000n;  // runtime-dependent size, arbitrary signed integer
const ratio: number    = 0.5;      // usually 8 bytes, about -1.8e308 to 1.8e308
const text: string     = "value";  // runtime-dependent size, no numeric range
```

```go
var flag    bool    = true     // 1 byte, false to true
var small   int8    = 1        // 1 byte, -128 to 127
var medium  int16   = 100      // 2 bytes, -32,768 to 32,767
var whole   int32   = 1000     // 4 bytes, -2,147,483,648 to 2,147,483,647
var large   int64   = 100000   // 8 bytes, -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807
var ratio   float32 = 0.5      // 4 bytes, about -3.4e38 to 3.4e38
var precise float64 = 0.5      // 8 bytes, about -1.8e308 to 1.8e308
var letter  rune    = 'A'      // 4 bytes, 0 to 1,114,111 Unicode scalar values
```

## Allocation and access

These examples declare a variable and allocate an array with space for a fixed number of elements:

```java
// Declare an integer variable.
int i;

// Allocate an array with ten integer elements.
int[] array = new int[10];
```

```c
int i;
int array[10];
```

```python
i: int
array = [0] * 10
```

```rust
let i: i32;
let mut array = [0i32; 10];
```

```typescript
let i: number;
let array: number[] = new Array(10);
```

```go
var i int
var array [10]int
```

To access the variable and store something:

```java
i = 32;
array[9] = 32;
```

```c
i = 32;
array[9] = 32;
```

```python
i = 32
array[9] = 32
```

```rust
i = 32;
array[9] = 32;
```

```typescript
i = 32;
array[9] = 32;
```

```go
i = 32
array[9] = 32
```

`array[9]` is the tenth element because these examples index arrays from zero. Out-of-bounds access
varies by language: Java raises an exception, Rust panics, and C behavior is undefined.
