# C-Minus Compiler

A compiler for the C-Minus language, built using modern Python with SOLID principles.

## Project Structure

The project is organized following architecture:

```
compiler_project/
├── src/                   # Source code
│   ├── lexer/             # Lexical analyzer components
│   │   ├── dfa.py         # DFA implementation
│   │   ├── dfa_builder.py # DFA construction
│   │   ├── lexer.py       # Main lexer
│   │   ├── lexical_errors.py # Lexical error handler
│   │   └── token_scanner.py # Token scanner
│   ├── parser/            # Parser components
│   │   ├── parser.py      # Main parser
│   │   ├── parser_base.py # Base parser interface
│   │   ├── parse_tree.py  # Parse tree implementation
│   │   ├── recursive_descent_parser.py # Grammar implementation
│   │   └── syntax_errors.py # Syntax error handler
│   ├── semantic/          # Semantic analysis (future)
│   ├── common/            # Shared data structures
│   │   ├── error_handler.py # Error handling base
│   │   ├── language_specs.py # Language specification
│   │   ├── symbol_table.py # Symbol table
│   │   ├── token.py      # Token definition
│   │   └── token_registry.py # Token management
│   └── utils/             # Utility functions
│       └── buffer.py      # Input buffer
├── tests/                 # Test files
├── docs/                  # Documentation
└── main.py                # Entry point
```

## Usage

### Prerequisites

- Python 3.7 or higher

### Running the Compiler

```sh
# Basic usage with default filenames
python main.py

# Specify input and output files
python main.py -i my_program.c -t my_tokens.txt -le my_errors.txt -s my_symbols.txt -p my_parse_tree.txt

# Get help
python main.py --help
```

### Command Line Options

- `-i, --input`: Input source code file (default: input.txt)
- `-t, --tokens`: Output tokens file (default: tokens.txt)
- `-le, --lexical-errors`: Output lexical errors file (default: lexical_errors.txt)
- `-s, --symbol-table`: Output symbol table file (default: symbol_table.txt)
- `-se, --syntax-errors`: Output syntax errors file (default: syntax_errors.txt)
- `-p, --parse-tree`: Output parse tree file (default: parse_tree.txt)
- `--verbose`: Enable verbose output


## Authors

- Pourya Erfanzadeh
- Yashar Paymai 