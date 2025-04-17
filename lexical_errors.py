class LexicalErrors:
    def __init__(self,file_path="lexical_errors.txt"):
        self.file_path = file_path
        self.errors ={}
        try:
            with open(file_path, 'a'):
                pass 
        except:
            print(f"an error occurred while creating the file{self.file_path}")
    def add(self,no_line,error):
        #TODO
        try:
            self.errors[no_line].append(error)
        except:
            self.errors[no_line] = []
            self.errors[no_line].append(error)

    def update_file(self):
        try:
            with open(self.file_path, 'w') as f:
                for line in self.errors.keys():
                    f.write(f"{line}\t")
                    for error in self.errors[line]:
                        f.write(f" {error}")
                    f.write("\n")
        except:
            print(f"an error occurred while updating the file{self.file_path}")

    #TODO : next phase
    def read_file(self,file_path):
        pass