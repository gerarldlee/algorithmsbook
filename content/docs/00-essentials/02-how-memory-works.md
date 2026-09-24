---
title: "How Memory Works"
weight: 2
---


Programs store values in memory and use addresses to find those values. Data structures organize
those values so common operations require fewer moves, comparisons, or allocations.

An address identifies a location in an address space; it does not guarantee that the same amount of
physical RAM is installed. A 32-bit address space can represent at most \(2^{32}\) distinct byte
addresses (4 GiB), while a 64-bit address space can represent far more. Operating systems, hardware,
permissions, and available physical memory limit what a process can actually use.
Think of memory as numbered byte locations. An array stores adjacent elements, so the address of an
element can be calculated from its start address and index. A linked list stores nodes wherever space
is available and follows references from one node to the next.

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

## Allocation and access

Java normally manages allocation and reclamation for you. A declaration gives a variable a type, and
an array allocation reserves space for a fixed number of elements:

```java
// Declare an integer variable.
int i;

// Allocate an array with ten integer elements.
int[] array = new int[10];
```

To access the variable and store something:

```java
i = 32;

array[9] = 32;
```

`array[9]` is the tenth element because Java indexes arrays from zero. Accessing an index outside
the array bounds raises an exception instead of silently reading unrelated memory.
