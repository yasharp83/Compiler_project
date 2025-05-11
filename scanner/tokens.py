class Tokens:
    def __init__(self,file_path="tokens.txt"):
        self.file_path = file_path
        self.tokens ={}
        try:
            with open(file_path, 'a'):
                pass 
        except:
            print(f"an error occurred while creating the file{self.file_path}")
    
    def add(self,no_line , token):
        try : 
            self.tokens[no_line].append(token)
        except:
            self.tokens[no_line] = []
            self.tokens[no_line].append(token)
    
    def update_file(self):
        try:
            with open(self.file_path, 'w') as f:
                for line in self.tokens.keys():
                    f.write(f"{line}.\t")
                    for token in self.tokens[line]:
                        f.write(f" ({token[0]}, {token[1]})")
                    f.write("\n")
                
        except:
            print(f"an error occurred while updating the file{self.file_path}")

    def read_file(self, file_path=None):
        """
        Read tokens from a file formatted as:
        line_num.    (token_type, token_lexeme) (token_type, token_lexeme) ...
        """
        if file_path is None:
            file_path = self.file_path
            
        try:
            print(f"Reading tokens from file: {file_path}")
            self.tokens = {}
            with open(file_path, 'r') as f:
                lines = f.readlines()
                print(f"Number of lines in token file: {len(lines)}")
                for line in lines:
                    if not line.strip():
                        continue
                    
                    parts = line.strip().split('\t')
                    if len(parts) < 2:
                        print(f"Skipping malformed line: {line.strip()}")
                        continue
                    
                    try:
                        line_num = int(parts[0].rstrip('.'))
                        tokens_str = parts[1].strip()
                        
                        self.tokens[line_num] = []
                        
                        # Special handling for malformed SYMBOL tokens like "(SYMBOL, ()"
                        # First replace problematic patterns
                        import re
                        tokens_str = re.sub(r'\(SYMBOL, \(', '(SYMBOL, "("', tokens_str)
                        tokens_str = re.sub(r'\(SYMBOL, \)', '(SYMBOL, ")"', tokens_str)
                        tokens_str = re.sub(r'\(SYMBOL, {', '(SYMBOL, "{"', tokens_str)
                        tokens_str = re.sub(r'\(SYMBOL, }', '(SYMBOL, "}"', tokens_str)
                        tokens_str = re.sub(r'\(SYMBOL, <', '(SYMBOL, "<"', tokens_str)
                        tokens_str = re.sub(r'\(SYMBOL, >', '(SYMBOL, ">"', tokens_str)
                        tokens_str = re.sub(r'\(SYMBOL, =', '(SYMBOL, "="', tokens_str)
                        tokens_str = re.sub(r'\(SYMBOL, \+', '(SYMBOL, "+"', tokens_str)
                        tokens_str = re.sub(r'\(SYMBOL, -', '(SYMBOL, "-"', tokens_str)
                        tokens_str = re.sub(r'\(SYMBOL, ;', '(SYMBOL, ";"', tokens_str)
                        
                        # Now use regex to parse tokens properly
                        token_pattern = r'\(\s*([^,]+)\s*,\s*([^)]*)\s*\)'
                        for match in re.finditer(token_pattern, tokens_str):
                            token_type = match.group(1).strip()
                            token_lexeme = match.group(2).strip()
                            # Remove quotes if they were added
                            if token_lexeme.startswith('"') and token_lexeme.endswith('"'):
                                token_lexeme = token_lexeme[1:-1]
                            self.tokens[line_num].append((token_type, token_lexeme))
                            print(f"Parsed token: ({token_type}, '{token_lexeme}') at line {line_num}")
                    except Exception as e:
                        print(f"Error parsing line: {line.strip()}, error: {e}")
                        continue
                            
            print(f"Total lines with tokens: {len(self.tokens)}")
            token_count = sum(len(tokens) for tokens in self.tokens.values())
            print(f"Total tokens parsed: {token_count}")
            return True
        except Exception as e:
            print(f"An error occurred while reading the file {file_path}: {e}")
            return False