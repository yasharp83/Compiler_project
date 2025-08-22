# Compiler Project - Phase 3

A complete compiler implementation for a C-like programming language, developed as part of a university compiler course. This project implements lexical analysis, syntax analysis, semantic analysis, and code generation phases of a compiler.

## Project Overview

This compiler translates a C-like programming language into intermediate code that can be executed by a virtual machine. The project is structured in phases:

- **Phase 1**: Lexical Analysis (Scanner)
- **Phase 2**: Syntax Analysis (Parser) 
- **Phase 3**: Semantic Analysis & Code Generation

### Authors
- Yashar Paymai (401100325)
- Pourya Erfanzadeh (401110918)
- Group: G3

## Language Features

### Supported Data Types
- `int` - Integer values
- `void` - For functions that don't return values

### Variable Declarations
```c
int x;           // Simple variable
int arr[10];     // Array declaration
```

### Function Declarations
```c
int add(int a, int b) {
    return a + b;
}

void printNumber(int x) {
    output(x);
}
```

### Control Structures

#### If-Else Statements
```c
if (condition) {
    // statements
} else {
    // statements
}
```

#### While Loops
```c
while (condition) {
    // statements
}
```

### Operators
- **Arithmetic**: `+`, `-`, `*`
- **Comparison**: `<`, `==`
- **Assignment**: `=`

### Built-in Functions
- `output(value)` - Prints a value to the output
- `return value` - Returns from a function

## Project Structure

```
Compiler_project/
├── scanner/                 # Lexical analyzer
│   ├── DFA.py              # Deterministic Finite Automaton
│   ├── buffer.py           # Input buffer management
│   ├── tokens.py           # Token definitions
│   └── symbol_table.py     # Symbol table implementation
├── parser/                  # Syntax analyzer
│   ├── parser.py           # Main parser implementation
│   ├── syntax_errors.py    # Syntax error handling
│   └── grammar_config/     # Grammar configuration files
├── code_gen/               # Code generation
│   ├── codeGen.py          # Main code generator
│   └── scopeFrame.py       # Scope frame management
├── Tests/                  # Test cases and virtual machine
│   └── phase3_tester/      # Phase 3 test suite
├── compiler.py             # Main compiler entry point
├── compile_and_exec.py     # Compile and execute script
└── execute.py              # Execution engine
```

## How to Use

### Prerequisites
- Python 3.x

### Basic Usage

1. **Write your code** in a text file (e.g., `input.txt`)

2. **Compile and execute** using one of these methods:

#### Method 1: Using the main compiler
```bash
python compiler.py
```

#### Method 2: Using the compile and execute script
```bash
python compile_and_exec.py
```

#### Method 3: With custom file paths
```bash
python compile_and_exec.py -i input.txt -o expected.txt -e error.txt
```

### Output Files
The compiler generates several output files:
- `tokens.txt` - List of tokens with line numbers
- `parse_tree.txt` - Parse tree representation
- `symbol_table.txt` - Symbol table contents
- `output.txt` - Generated intermediate code
- `semantic_errors.txt` - Semantic analysis errors
- `syntax_errors.txt` - Syntax analysis errors
- `lexical_errors.txt` - Lexical analysis errors

## Code Example

Here's a complete example demonstrating various language features:

```c
// Function to calculate factorial
int factorial(int n) {
    if (n <= 1) {
        return 1;
    } else {
        return n * factorial(n - 1);
    }
}

// Function to print array
void printArray(int arr[], int size) {
    int i;
    i = 0;
    while (i < size) {
        output(arr[i]);
        i = i + 1;
    }
}

// Main function
void main(void) {
    int result;
    int numbers[5];
    int i;
    
    // Calculate factorial of 5
    result = factorial(5);
    output(result);
    
    // Initialize array
    i = 0;
    while (i < 5) {
        numbers[i] = i + 1;
        i = i + 1;
    }
    
    // Print array
    printArray(numbers, 5);
}
```

### How to run this example:

1. Save the code above to `input.txt`
2. Run: `python compile_and_exec.py`
3. Check `expected.txt` for the output

## Testing

The project includes comprehensive test cases in the `Tests/` directory:

- **Phase 3 tests**: Located in `Tests/phase3_tester/test/testcases/`
- **Test categories**:
  - T1-T10: Basic functionality tests
  - R1-R4: Regression tests
  - S1-S4: Semantic analysis tests

To run tests:
```bash
cd Tests/phase3_tester
python test/runner.py
```

## Virtual Machine

The generated code is executed by a custom virtual machine that supports:
- Memory management
- Stack operations
- Arithmetic and logical operations
- Function calls and returns
- Control flow instructions

## Error Handling

The compiler provides detailed error reporting for:
- **Lexical errors**: Invalid tokens, unterminated strings/comments
- **Syntax errors**: Grammar violations, missing semicolons, brackets
- **Semantic errors**: Type mismatches, undefined variables, scope violations

## Technical Details

### Grammar
The language follows a context-free grammar defined in `parser/grammar_config/grammar.txt` with semantic actions for code generation.

### Code Generation
The compiler generates intermediate code in a three-address format that can be executed by the virtual machine. The code generator handles:
- Variable allocation and scope management
- Function calls and parameter passing
- Control flow (if-else, while loops)
- Expression evaluation
- Memory management

### Symbol Table
Maintains information about:
- Variable declarations and types
- Function signatures
- Scope hierarchy
- Memory addresses

## Contributing

This is an academic project. For questions or issues, please refer to the course materials or contact the authors.

## License

This project is developed for educational purposes as part of a university compiler course. 