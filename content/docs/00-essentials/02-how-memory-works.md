---
title: "How Memory Works"
weight: 2
---


Everything that we do in computing (and algorithms), is just manipulations of the computer memory.  The data structure that we learn is a cleaner and human understandable representation of memory manipulation designed to make it easier for us to work through the memory.

Imagine you own a room full of mini storage boxes with label from 0 to 1,000. The room is the representation of a memory chip. The labels are the memory addresses.  Up to how much a memory address can be represented, depends on your CPU architecture 32-bits or 64-bits.  A 32-bit CPU can represent up to 32-bit memory address i.e.  \(2^{32}\) = 4 GB of memory.  A 64-bit can address up to \(2^{64}\) = 18 EB (exabytes) of memory.  Each storage box can store up to some \(x\) bytes, depending on your CPU architecture i.e. 32 bits (4 bytes) or 64 bits (8 bytes).

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

Each memory space can be represented by a data type.

| Data types | Java keyword or wrapper | Memory value | Java value | Explanation |
| --- | --- | --- | --- | --- |
| Boolean | boolean or Boolean | 1 bit | true or false | 1 bit can be either 1 or 0, or true or false |
| Byte (whole number) | byte or Byte | 1 byte (8 bits) | -128 to 127 | 8 bits signed = \(-2^7\) up to \(2^7 - 1\) |
| Short Integer | short or Short | 2 bytes (16 bits) | -32,768 to 32767 | 16 bits signed = \(-2^{15}\) up to \(2^{15} - 1\) |
| Character (letter or symbol representation) | char or Character | 2 bytes | single character ascii or Unicode values | 16 bits unsigned character representation |
| Integer (whole number) | int or Integer | 4 bytes (32 bits) | -2,147,483,648 to 2,147,483,647 | 32 bits signed = \(-2^{31}\) up to \(2^{31} - 1\) |
| Floating number | float or Float | 4 bytes | up to 6 to 7 decimal digits | 32 bits signed |
| Long (long integer whole number) | long or Long | 8 bytes (64 bits) | -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807 | 64 bits signed = \(-2^{63}\) up to \(2^{63} - 1\) |
| Double (double precision floating number) | double or Double | 8 bytes  | up to 15 decimal digits | 64 bits signed |

The key thing to remember here is that whenever we want to store something, we need to request which memory address we want (this is done automatically in Java) and by how many or how much to store (datatypes or in the case of arrays, sizes).

To request for memory storage in Java, we declare:

```java
// declare a variable i to be of integer type i.e. i will contain at most 4 bytes
int i;

// declare an array to be of integer type with 10 elements
int[] array = new int[10];
```

To access the variable and store something:

```java
i = 32;

array[9] = 32;
```
