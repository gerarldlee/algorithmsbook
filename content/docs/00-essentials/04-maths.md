---
title: "Maths"
weight: 4
---

These mathematical tools explain the bounds, indexing, and numeric transformations used throughout
the book. Learn the operation and its cost, not just the name.

## Fundamentals

1. **Binary exponentiation** — compute \(a^b\) in \(O(\log b)\) multiplications by repeatedly squaring.
2. **Number representation** — convert between binary, decimal, hexadecimal, signed, and unsigned values.
3. **Bit shifting** — multiply or divide powers of two when the operation preserves the intended sign and range.
4. **Logarithms and bases** — count how many times an input can be halved or how many levels a branching process creates.

## Prime numbers

1. **Sieve of Eratosthenes** — find all primes up to \(n\) in \(O(n \log\log n)\) time and \(O(n)\) space.

## Algebra

1. **Fibonacci numbers** — a recurrence used for dynamic programming and recurrence analysis.
2. **Golden ratio** — the limiting ratio in Fibonacci growth and several divide-and-conquer bounds.
3. **Euclidean algorithm** — compute a greatest common divisor with repeated remainders.
4. **Euler’s totient function** — count integers relatively prime to a given integer.
5. **Catalan numbers** — count recursively defined structures such as binary trees and valid parentheses.

## Identities to remember

- \(\log_a n = \frac{\log_b n}{\log_b a}\), so changing a constant logarithm base does not change a Big-O class.
- \(1 + 2 + \dots + n = \frac{n(n+1)}{2} = \Theta(n^2)\).
- \(1 + 2 + 4 + \dots + 2^k = 2^{k+1}-1 = \Theta(2^k)\).
- \(\gcd(a,b)=\gcd(b,a\bmod b)\), which is the basis of the Euclidean algorithm.
