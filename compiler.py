# Yashar Paymai (401100325)
# Pouria Erfanzadeh (401011180)
# Group: G3


from scanner.scanner import scanner
import os

file_path = "input.txt"
print(f"Current working directory: {os.getcwd()}")
print(f"Input file exists: {os.path.exists(file_path)}")
print(f"Input file path: {os.path.abspath(file_path)}")


scanner(code_file_path=file_path)

try:
    # Phase 1: Scanner
    print("Starting scanner phase...")
    scanner(code_file_path=file_path)
    print("Scanner phase completed.")
    
    # Phase 2: Parser
    # print("Starting parser phase...")
    # parser(tokens_file_path="tokens.txt", 
    #        symbol_table_file_path="symbol_table.txt",
    #        syntax_errors_file_path="syntax_errors.txt", 
    #        parse_tree_file_path="parse_tree.txt")
    # print("Parser phase completed.")
except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()