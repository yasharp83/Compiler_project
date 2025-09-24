# Mini C-like Compiler 

A three-phase educational compiler for a C-like subset that performs lexical analysis, transition‑diagram top‑down parsing, semantic checks, and intermediate code generation to a simple stack-based VM.

## Project Structure

- `scanner/`: DFA-based lexer producing `tokens.txt`, `lexical_errors.txt`, `symbol_table.txt`
- `parser/`: Transition‑diagram predictive parser building parse tree (`parse_tree.txt`) and reporting `syntax_errors.txt`
- `code_gen/`: Semantic actions + IR generation to `output.txt` and `semantic_errors.txt`
- `compiler.py`: Wires all phases; default input `input.txt`
- `compile_and_exec.py`: CLI to compile and execute on bundled VM
- `execute.py`: Runs `output.txt` on test VM and writes results/errors
- `Tests/phase3_tester/`: Test harness and VM

## Quick Start


1) Put your source program in `input.txt` (or point to another file).
2) Compile:

```bash
python3 compiler.py
```

This generates:
- `tokens.txt`, `lexical_errors.txt`, `symbol_table.txt`
- `parse_tree.txt`, `syntax_errors.txt`
- `output.txt` (IR/VM code), `semantic_errors.txt`

3) Run the generated code on the VM:

```bash
python3 execute.py
```

The VM writes program output to `expected.txt` and runtime errors to `error.txt`.

### One‑shot compile + execute

```bash
python3 compile_and_exec.py -i input.txt -o expected.txt -e error.txt
```

Flags are optional; defaults are shown above.

## Samples

Sample program :

```c
int fib(int n) {
    int f;
    if (n < 2) {
	f = 1;
    } else {
        f = fib(n - 1) + fib(n - 2);
    }
    return f;
}

void main(void)
{
     output(fib(3));
}
```

Expected artifacts after compile and run:
- `semantic_errors.txt`: "The input program is semantically correct." (if no issues)
- `output.txt`: VM instructions with line numbers
- `expected.txt`: contains `3` on its own line

More examples are available under `Tests/phase3_tester/testcases/`.

## Implementation Notes

- Lexer: Table‑driven DFA; keywords recognized in `scanner/alphabet_config.py`
- Parser: Transition diagrams generated from grammar in `parser/grammar_config/{grammar,first,follow}.txt`
- CodeGen: Generates IR consumed by `Tests/phase3_tester/test/vm.py`; includes semantic checks (type match, arg counts, undefined ids, void misuse, break scoping)

## Useful Commands


- Run a test input file directly:
```bash
python3 compile_and_exec.py -i Tests/phase3_tester/test/testcases/T1/input.txt
```
