# Scanner (Lexer)

Table‑driven DFA scanner that converts source code into a token stream, records lexical errors, and maintains a symbol table of identifiers/keywords.

## Inputs
- Source file (default: `input.txt`)
- Alphabet/keywords config in `scanner/alphabet_config.py`

## Core Components
- `scanner/scanner.py`: High‑level `scanner(...)` function that iterates `get_next_token`
- `scanner/get_next_token.py`: Steps DFA, emits tokens, logs errors, and updates symbol table
- `scanner/DFA.py` and `scanner/init_dfa.py`: Automaton and transition initialization
- `scanner/buffer.py`: Buffered file reader with position tracking
- `scanner/tokens.py`, `scanner/lexical_errors.py`, `scanner/symbol_table.py`: Output writers and symbol table

## Outputs
- `tokens.txt`: One token per line with line numbers
- `lexical_errors.txt`: Grouped lexical errors per line
- `symbol_table.txt`: Indexed list of identifiers/keywords

## Usage
Run end‑to‑end via the compiler:
```bash
python3 compiler.py
```
Run the scanner alone:
```python
from scanner.scanner import scanner
scanner("input.txt")
```

## Notes
- Whitespace tokens are filtered from `tokens.txt`
- Comments are recognized and skipped by the DFA
- Keywords are normalized as `KEYWORD`, identifiers as `ID` 