# Code Generation

Generates intermediate code for a simple stack/three‑address‑style VM, with semantic checks during parsing.

## Entry Points
- `code_gen/codeGen.py: CodeGen` — orchestrates semantic stack, symbol table, and emits IR lines
- Invoked by `parser/Parser` via semantic action hooks

## IR/VM Format
- Each line in `output.txt` has a line number then an instruction tuple:
  - `(OP, R1, R2, R3)` where operands may be addresses, immediate `#n`, or `@addr` for indirect
- Important ops: `ASSIGN`, `ADD`, `SUB`, `MULT`, `EQ`, `LT`, `JP`, `JPF`, `PRINT`
- A small runtime template is emitted to support `output(int)`

## Registers and Memory
- Virtual registers stored in data block: `sp`, `fp`, `ra`, `rv`
- Data block grows from `data_address` upward; temporaries from `temp_address`
- A simple stack is implemented with `sp` and helpers: push/pop/allocate

## Semantic Actions (subset)
- Expression: push ids/nums, push operand, `operand_exec` produces temp results
- Assignment: `assign` with type checking
- Control flow: `label`, `hold` + `if_decide`, `while_jump`
- Functions: define, pass/collect args, call/return; `main_function` and `set_exec_block("main")`
- Arrays: base + index to indirect addresses; size tracked on stack

See `sub_routines` mapping in `CodeGen` for the full list.

## Semantic Checks
- Undefined identifiers
- Type mismatches in operands and assignments
- Void misuse in variable declarations
- Function argument count/type mismatches
- `break` outside of `while`

## Outputs
- `output.txt`: IR listing (or "The code has not been generated." if semantic errors exist)
- `semantic_errors.txt`: Human‑readable semantic diagnostics (or "The input program is semantically correct.")

## Execute on VM
The VM under `Tests/phase3_tester/test/vm.py` runs the generated IR.

```bash
python3 execute.py
```

This reads `output.txt`, writes program output to `expected.txt`, and VM errors to `error.txt`. 