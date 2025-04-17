
Keywords = ["if" , "else" , "void" , "int" , "while" , "break" , "return"]
Symbols = [';' , ':' , ',' , '[' , ']' , '(' , ')' , '{' , '}' , '+' , '-' , '*' , '/' , '\\' , '=' , '=' , '>' , '<']
White_spaces = [chr(32),chr(10),chr(9),chr(13),chr(11),chr(12)]
Digits = [chr(i) for i in range(48,58)]
English_aphabet = [chr(i) for i in (list(range(65,91)) + list(range(97,123)))]
Illegal = []
for i in range(256):
    if (chr(i) not in Symbols) and (chr(i) not in White_spaces) and (chr(i) not in Digits) and (chr(i) not in English_aphabet) :
        Illegal.append(chr(i))
sigma = [chr(i) for i in range(256)]


def is_keyword(token): 
    return token in Keywords