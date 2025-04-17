error_massages = {
    "ERROR_INVALID_NUMBER" : "Invalid number" , 
    "ERROR_INVALID_INPUT" : "Invalid input" , 
    "ERROR_UNMATCHED_COMMENT" : "Unmatched comment" , 
    "ERROR_UNCLOSED_COMMENT" : "Unclosed comment" , 
}

class LexicalErrors:
    def __init__(self,file_path="lexical_errors.txt"):
        self.file_path = file_path
        self.errors ={}
        self.error_occured = False
        try:
            with open(file_path, 'a'):
                pass 
        except:
            print(f"an error occurred while creating the file{self.file_path}")
    def add(self,no_line,error):
        self.error_occured = True
        #TODO
        try:
            self.errors[no_line].append(error)
        except:
            self.errors[no_line] = []
            self.errors[no_line].append(error)

    def update_file(self):
        try:
            with open(self.file_path, 'w') as f:
                if not self.error_occured : 
                    f.write("There is no lexical error\n")
                for line in self.errors.keys():
                    f.write(f"{line}\t")
                    for error in self.errors[line]:
                        f.write(f" ({error[1]}, {error_massages[error[0]]})")
                    f.write("\n")
        except:
            print(f"an error occurred while updating the file{self.file_path}")

    #TODO : next phase
    def read_file(self,file_path):
        pass