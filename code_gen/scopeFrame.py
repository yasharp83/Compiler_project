class ScopeFrame:
    def __init__(self , codeGen):
        self.codeGen=codeGen
        self.adress_stack=[]
        self.pending_jumps=[]
    
    def add_scope(self):
        self.adress_stack.append(self.codeGen.temp_addres)
        self.adress_stack.append(self.codeGen.data_address)
        self.pending_jumps.append("#")
    
    def remove_scope(self):
        self.codeGen.data_address=self.adress_stack.pop()
        self.codeGen.temp_addres=self.adress_stack.pop()

        while self.pending_jumps[-1] != "#" : 
            self.backpatch_jump()
        self.pending_jumps.pop()
    
    def create_jump_placeholder(self):
        self.pending_jumps.append(len(self.codeGen.program_block))
        self.codeGen.add_code(op="PLACE_HOLDER")
    
    def backpatch_jump(self):
        break_address=len(self.codeGen.program_block)
        place_holder_address=self.pending_jumps.pop()
        self.codeGen.add_code(op="JP" , r1=f"{break_address}" , line=place_holder_address)