# Code Generation Documentation

## Overview
The code generation module is a crucial part of the compiler project that translates the parsed and semantically analyzed code into target machine instructions. This module takes the processed input from earlier compiler phases (lexical analysis, syntax analysis, and semantic analysis) and generates executable code.

## Key Components

### 1. CodeGen Class
The main code generator class that handles the translation of source code into target machine code. It maintains several important components:

- **Symbol Table**: A data structure that stores information about all identifiers in the program
- **Program Block**: The list of generated instructions
- **Semantic Stack**: A stack used to manage code generation operations
- **Registers**: Special memory locations for key operations (sp, fp, ra, rv)
- **Scope Management**: Handles different types of scopes (simple, conditional, function, temporary)

### 2. ScopeFrame Class
A helper class that manages scope-related operations:
- Tracks address stacks for different scopes
- Handles pending jumps within scopes
- Manages memory allocation and deallocation for scopes

## Core Concepts

### Symbol Table
- Acts as a dictionary for all variables, functions, and identifiers
- Stores information like:
  - Variable addresses
  - Variable types
  - Function parameters
  - Scope information

### Scope Frame
- Manages different types of scopes:
  - 's': Simple scope
  - 'c': Conditional scope (if/while)
  - 'f': Function scope
  - 't': Temporary scope
- Handles memory management for each scope
- Manages jump instructions for control flow

### Memory Management
The code generator manages three main memory segments:
1. **Data Segment** (starts at 20000): For variables and static data
2. **Stack Segment** (starts at 40000): For function calls and local variables
3. **Temp Segment** (starts at 60000): For temporary calculations

## Key Operations

### 1. Stack Operations
```python
stack_push(): Push values onto the stack
stack_pop(): Pop values from the stack
stack_allocate(): Allocate stack space
stack_store_registers(): Save register values
stack_load_registers(): Restore register values
```

### 2. Code Generation Operations
```python
add_code(): Add instructions to program block
get_datablock_var(): Allocate space in data segment
get_tempblock_var(): Allocate space in temp segment
```

### 3. Scope Management
```python
scope_manage_add_scope(): Create new scope
scope_manage_remove_scope(): Remove current scope
scope_manage_create_jump_placeholder(): Handle conditional jumps
scope_manage_backpatch_jump(): Resolve jump addresses
```

## Code Generation Process

1. **Initialization**
   - Set up memory segments
   - Initialize registers
   - Create initial scope frames
   - Set up built-in functions (e.g., output)

2. **Code Generation**
   - Process input tokens
   - Generate appropriate instructions
   - Manage scopes and memory
   - Handle function calls and returns

3. **Output Generation**
   - Generate final program block
   - Write output to file
   - Handle semantic errors

## Error Handling
The code generator includes comprehensive error checking:
- Type mismatch detection
- Undefined variable usage
- Function argument mismatches
- Void type usage errors
- Break statement validation

## Technical Details

### Register Usage
- **sp (Stack Pointer)**: Points to top of stack
- **fp (Frame Pointer)**: Points to current function frame
- **ra (Return Address)**: Stores return address for functions
- **rv (Return Value)**: Stores function return values

### Memory Word Size
- Default word size: 4 bytes
- Used for memory allocation and address calculations

### Instruction Format
```
(Operation, Operand1, Operand2, Operand3)
```
Example:
```
(ADD, #100, #200, 1000)  // Add 100 and 200, store in address 1000
```

### Common Operations
- **ADD/SUB/MULT**: Arithmetic operations
- **EQ/LT**: Comparison operations
- **JP/JPF**: Jump instructions
- **ASSIGN**: Assignment operation
- **PRINT**: Output operation

## Usage Example

```python
# Initialize code generator
code_gen = CodeGen(symbol_table=SymbolTable())

# Generate code for variable declaration
code_gen.code_gen_define_id(token, param)

# Generate code for function call
code_gen.code_gen_function_call(token, param)

# Export generated code
code_gen.export("output.txt")
```

## Best Practices
1. Always manage scope entry and exit properly
2. Handle memory allocation carefully
3. Validate types before operations
4. Clean up resources when removing scopes
5. Maintain proper stack frame management

## Common Pitfalls
1. Incorrect scope management
2. Memory leaks in temporary variables
3. Unresolved jump addresses
4. Stack pointer misalignment
5. Register value corruption

## Debugging Tips
1. Check semantic errors output
2. Verify stack pointer operations
3. Monitor scope nesting levels
4. Validate jump address resolution
5. Review memory allocation patterns
