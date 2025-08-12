from scanner.symbol_table import SymbolTable
from code_gen.scopeFrame import ScopeFrame
from scanner.symbol_table import Token

class CodeGen:
    def __init__(self , 
                 symbol_table:SymbolTable ,
                 word_size=4 ,
                 data_address=1000 ,
                 stack_address=2000 ,
                 temp_address=3000 , 
                 ):
        
        self.symbol_table=symbol_table

        self.word_size=word_size
        self.data_address=data_address
        self.stack_address=stack_address
        self.temp_addres=temp_address


        self.program_block = []
        self.semantic_stack = []
        

        self.registers = {
            "sp" : self.get_datablock_var(), 
            "fp" : self.get_datablock_var(), 
            "ra" : self.get_datablock_var(), 
            "rv" : self.get_datablock_var(),
        }


        self.scope_type_stack = []
        self.scopeFrames : dict[str, ScopeFrame] = {
            "s": ScopeFrame(codeGen=self),
            "c": ScopeFrame(codeGen=self),
            "f": ScopeFrame(codeGen=self),
            "t": ScopeFrame(codeGen=self),
        }
        self.delete_scope_flag = False

        self.function_input_flag = False
        self.last_token = None

        self.function_data_pointer = 0
        self.function_temp_pointer = 0

        self.is_main_declared=False

        self.sub_routines = {
            "push_num" : self.code_gen_push_num , 
            "push_id" : self.code_gen_push_id,

            "pop" : self.code_gen_pop ,

            "define_id" : self.code_gen_define_id , 
            "define_array" : self.code_gen_define_array , 
            "define_function" : self.code_gen_define_function ,

            "main_function" : self.code_gen_main_function , 

            "scope_start" : self.code_gen_scope_start , 
            "scope_finish" : self.code_gen_scope_finish ,

            "function_input_start" : self.code_gen_function_input_start ,
            "function_input_finish" : self.code_gen_function_input_finish , 

            "function_return" : self.code_gen_function_return
        }
    



    def code_gen_pop(self , token:Token , param=None):
        self.semantic_stack.pop()

    def code_gen_push_id(self , token:Token , param=None):
        record = self.symbol_table.find_record_by_id(token.lexeme)
        self.semantic_stack.append(record.address)

    def code_gen_push_num(self , token:Token , param=None):
        self.semantic_stack.append(f"#{token.lexeme}")


    def code_gen_define_id(self , token:Token , param=None):
        self.last_token = token
        record = self.symbol_table.find_record_by_id(token.lexeme)
        record.address = self.get_datablock_var()
        if self.function_input_flag : 
            self.stack_pop(record.address)
        else:
            self.add_code(op="ASSIGN" , r1="#0" , r2=f"{record.address}")

    def code_gen_define_array(self , token:Token , param=None):
        self.add_code(op="ASSIGN" , r1=f"{self.registers["sp"]}" , r2=self.semantic_stack[-2])
        size = self.semantic_stack.pop()
        size = int(size[1:])
        self.stack_allocate(size=size)

    def code_gen_define_function(self , token:Token , param=None):
        self.function_data_pointer , self.function_temp_pointer = self.data_address , self.temp_addres
        record = self.symbol_table.find_record_by_id(self.last_token.lexeme)
        record.address = len(self.program_block)
        self.program_block[-1] = ""

    
    def code_gen_scope_start(self , token:Token , param=None):
        self.symbol_table.add_scope()
        self.scope_manage_add_scope(scope_type=param[0])

    def code_gen_scope_finish(self , token:Token , param=None):
        self.symbol_table.remove_scope()
        self.scope_manage_remove_scope(scope_type=param[0])

    def code_gen_function_input_start(self , token:Token , param=None):
        self.function_input_flag = True
    
    def code_gen_function_input_finish(self , token:Token , param=None):
        self.function_input_flag = False

    def code_gen_function_return(self , token:Token , param=None):
        self.add_code(op="JP" , r1=f"@{self.registers["ra"]}")


    def code_gen_main_function(self , token:Token , param=None):
        if self.is_main_declared : 
            return
        self.is_main_declared = True
        func = self.semantic_stack.pop()
        self.program_block.pop()
        self.semantic_stack.append(len(self.program_block))
        self.program_block.append("MAIN_PLACE_HOLDER")
        self.semantic_stack.append(func)

    def get_datablock_var(self , size=1):
        ret = self.data_address
        self.data_address+=self.word_size * size
        return ret
    
    def get_tempblock_var(self , size=1):
        ret = self.temp_addres
        self.temp_addres+=self.word_size * size
        return ret
    
    #ScopeManagement

    def scope_manage_push_scope_type(self , typ):
        self.scope_type_stack.append(typ)
    
    def scope_manage_create_jump_placeholder(self):
        self.scopeFrames[self.scope_type_stack.pop()].create_jump_placeholder()
    
    def scope_manage_backpatch_jump(self):
        self.scopeFrames[self.scope_type_stack.pop()].backpatch_jump()
    
    def scope_manage_add_scope(self , scope_type):
        #scope_type=self.scope_type_stack.pop()
        self.scopeFrames[scope_type].add_scope()
        if scope_type== "f":
            self.stack_add_scope()
        
    def scope_manage_remove_scope(self , scope_type):
        #self.delete_scope_flag=False
        #scope_type= self.scope_type_stack.pop()
        self.scopeFrames[scope_type].remove_scope()
        if scope_type=="f" : 
            self.stack_del_scope()
    
    

    #STACK ops
    
    def stack_push(self , val):
        self.add_code("ASSIGN" , val , f"@{self.registers["sp"]}")
        self.add_code("ADD" , f"{self.registers["sp"]}" , f"#{self.word_size}" , f"{self.registers["sp"]}")
    
    def stack_pop(self , val):
        self.add_code("SUB" , f"{self.registers["sp"]}" , f"#{self.word_size}" , f"{self.registers["sp"]}")
        self.add_code("ASSIGN" , f"@{self.registers["sp"]}" , val)

    def stack_add_scope(self):
        self.program_block.append("")
        self.stack_push(self.registers["fp"])
        self.add_code("ASSIGN" , f"{self.registers["sp"]}" , f"{self.registers["fp"]}")
    
    def stack_del_scope(self):
        self.add_code("ASSIGN" , f"{self.registers["fp"]}" , f"{self.registers["sp"]}")
        self.stack_pop(self.registers["fp"])
        self.program_block.append("")
    
    def stack_allocate(self , size=1):
        self.add_code("ADD" , f"#{self.word_size * size}" , f"{self.registers["sp"]}" ,f"{self.registers["sp"]}")

    def stack_store_registers(self , registers=["sp" , "fp" , "ra"]):
        for rg in registers : 
            self.stack_push(self.registers[rg])
    
    def stack_load_registers(self , registers=["ra" , "fp" , "sp"]):
        for rg in registers:
            self.stack_pop(self.registers[rg])


    def add_code(self , op , r1="" , r2="" , r3="" , line=None):
        if line != None :
            self.program_block[line] = f"({op} , {r1} , {r2} , {r3})"
        else :
            self.program_block.append(f"({op} , {r1} , {r2} , {r3})")
