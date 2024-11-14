# Transmuter front-end

Front-end libraries and utilities for the Transmuter language processing infrastructure.

## Features

- Conditional declaration of language features

### Lexical Analyzer

- POSIX ERE-based language
- NFA-based implementation
- `O(n)` complexity
- Ignorable tokens (for eg. comments, newlines and whitespaces)
- On-demand and memoized tokenization
- Longest match tokenization
  - Ambiguous generalization as workaround
- Ambiguous tokenization
  - Precedence-based disambiguation

### Syntactic Analyzer

- Generalized CFG-based language (including ambiguities and left-recursion)
- Recursive Descent-based implementation (using backtracking instead of lookahead)
- `O(n^3)` complexity
- Efficient memoized parsing
- Syntax sugar for optionals and expression grouping
- Iteration-based efficient alternative to (left-)recursion
- Efficient (`SPACE(n^3)`) ambiguous BSR-based output
  - Ordered choice and longest match-based disambiguation

### Semantic Analyzer
