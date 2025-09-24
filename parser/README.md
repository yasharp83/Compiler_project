# Parser

Transition‑diagram predictive parser that constructs a parse tree and triggers semantic actions for code generation.

## Inputs
- Grammar: `parser/grammar_config/grammar.txt`
- FIRST sets: `parser/grammar_config/first.txt`
- FOLLOW sets: `parser/grammar_config/follow.txt`
- Token stream from the scanner via `get_next_token(...)`

## Core Components
- `parser/parser.py`:
  - Builds a transition diagram (`TdGraph`) from the grammar
  - Performs top‑down parsing by traversing diagrams with lookahead and FIRST/FOLLOW
  - Emits parse tree (`PtNode`) and writes `parse_tree.txt`
  - Reports syntax errors to `syntax_errors.txt`
  - Invokes semantic actions on edges to drive `code_gen/CodeGen`

### Key Classes
- `TdGraph`/`TdNode`: Nonterminal diagram with edges labeled by terminals/nonterminals and optional actions
- `PtNode`: Parse tree node with pretty‑printer to file
- `Parser`: Orchestrates scanning, diagram traversal, error recovery, and codegen hooks

## Error Handling
- Illegal token: emits `syntax error, illegal <token>` and attempts recovery
- Missing construct: emits `syntax error, missing <symbol>`
- Unexpected EOF: emits `syntax error, Unexpected EOF`

## Outputs
- `parse_tree.txt`: ASCII tree of the parsed program
- `syntax_errors.txt`: Collected syntax errors (empty if none)

## Usage
The parser is driven by `compiler.py`. To run end‑to‑end:
```bash
python3 compiler.py
```
This will produce `parse_tree.txt` and `syntax_errors.txt` under project root.

## Notes
- CodeGen actions (phase3) are prefixed with `#` and attached to edges as start/finish actions
- FIRST/FOLLOW are precomputed and loaded from text files; ensure they match `grammar.txt` 