# Alchemist front-end libraries
Front-end libraries and utilities for the Alchemist compiler infrastructure.

## Lexer
- String- and regex-based pattern matching;
- Regex-based list of ignorables, such as whitespaces, newlines or comments;
- First, longest match, with fine-tunable order of match;
- OO-based hierarchical token specialization/generalization;
- Incremental (TO DO) and on-demand lexing;
- Supports multiple independent consumers without re-lexing;

## Parser
The generated parser is a recursive descent parser based on [Frost & Hafiz (2006)](https://doi.org/10.1145/1149982.1149988), [Frost, Hafiz & Callaghan (2007)](https://doi.org/10.3115/1621410.1621425), [Frost, Hafiz & Callaghan (2008)](https://doi.org/10.1007/978-3-540-77442-6_12) and [Scott & Johnstone (2010)](https://doi.org/10.1016/j.entcs.2010.08.041), which:
- Is powerful enough to parse any CFG, including left-recursive (TO DO) and ambiguous grammars;
- Is efficient enough to parse most simple grammars in linear time, with cubic worst-case performance;
- Is stupidly simple to understand and customize;
- Builds the AST forest automatically (TO DO);
- Displays useful error messages (TO DO);
- Supports incremental parsing (TO DO);
