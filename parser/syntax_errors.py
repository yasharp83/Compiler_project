class SyntaxErrors:
    def __init__(self , file_path="syntax_errors.txt"):
        self.file_path = file_path
        self.errors = []
        self.error_occured = False
        try : 
            with open(file_path , 'a') : 
                pass
        except : 
            print(f"an error occurred while creating the file{self.file_path}")

    def add(self,no_line,error):
        self.error_occured = True
        self.errors.append(f"#{no_line} : {error}")
    
    def update_file(self):
        try : 
            with open(self.file_path ,'w') as f : 
                if not self.error_occured : 
                    f.write("There is no syntax error.\n")
                for error in self.errors : 
                    f.write(error+"\n")
        except : 
            print(f"an error occurred while updating the file{self.file_path}")