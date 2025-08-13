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
        self.function_input_pointers = []

        self.function_data_pointer = 0
        self.function_temp_pointer = 0

        self.is_main_declared=False

        self.add_template()


        self.operands_map = {
            "+" : "ADD" , 
            "-" : "SUB" , 
            "*" : "MULT" , 
            "==" : "EQ" , 
            "<" : "LT" ,
        }

        self.sub_routines = {
            "push_num" : self.code_gen_push_num , 
            "push_id" : self.code_gen_push_id,
            "push_rv" : self.code_gen_push_rv ,
            "push_array" : self.code_gen_push_array ,
            "push_operand" : self.code_gen_push_operand ,
            "push_zero" : self.code_gen_push_zero ,

            "pop" : self.code_gen_pop ,
            "hold" : self.code_gen_hold ,
            "if_decide" : self.code_gen_if_decide , 
            "while_jump" : self.code_gen_while_jump ,
            "label" : self.code_gen_label , 
            "assign_stack" : self.code_gen_assign_stack ,
            
        
            "operand_exec" : self.code_gen_operand_exec , 

            "define_id" : self.code_gen_define_id , 
            "define_array" : self.code_gen_define_array , 
            "define_function" : self.code_gen_define_function ,

            "main_function" : self.code_gen_main_function , 

            "scope_start" : self.code_gen_scope_start , 
            "scope_finish" : self.code_gen_scope_finish ,

            "function_input_start" : self.code_gen_function_input_start ,
            "function_input_finish" : self.code_gen_function_input_finish , 
            "function_input_pass" : self.code_gen_function_input_pass , 
            "function_call" : self.code_gen_function_call , 

            "function_return" : self.code_gen_function_return , 

            "jump_placeholder" : self.code_gen_jump_placeholder , 
            "backpatch_jump" : self.code_gen_backpatch_jump ,


        }
    



    def code_gen_pop(self , token:Token , param=None):
        self.semantic_stack.pop()
    
    def code_gen_hold(self , token:Token , param:None):
        self.semantic_stack.append(len(self.program_block))
        self.program_block.append("PLACE_HOLDER_HOLD")
    
    def code_gen_if_decide(self , token:Token , param:None):
        print(self.semantic_stack)
        addr = self.semantic_stack.pop()
        stmt = self.semantic_stack.pop()
        cur_line = len(self.program_block)
        self.add_code(op="JPF" , r1=stmt , r2 =cur_line , line=int(addr))
    
    def code_gen_while_jump(self , token:Token , param:None):
        s1 , s2 , s3 = self.semantic_stack.pop() , self.semantic_stack.pop() , self.semantic_stack.pop()
        self.add_code(op="JP" , r1=s3)
        self.semantic_stack.append(s2)
        self.semantic_stack.append(s1)

    def code_gen_label(self , token:Token , param:None):
        self.semantic_stack.append(len(self.program_block))

    def code_gen_assign_stack(self , token:Token , param:None):
        self.add_code(op="ASSIGN" , r1=self.semantic_stack.pop() , r2 = self.semantic_stack[-1])

    def code_gen_push_operand(self , token:Token , param:None):
        self.semantic_stack.append(self.operands_map[token.lexeme])

    def code_gen_operand_exec(self , token:Token , param:None):
        r2 , op , r1 = self.semantic_stack.pop() , self.semantic_stack.pop() , self.semantic_stack.pop()
        r3 = self.get_tempblock_var()
        self.semantic_stack.append(r3)
        self.add_code(op=op , r1=r1 , r2=r2 , r3=r3)



    def code_gen_push_id(self , token:Token , param=None):
        record = self.symbol_table.find_record_by_id(token.lexeme)
        self.semantic_stack.append(record.address)

    def code_gen_push_num(self , token:Token , param=None):
        self.semantic_stack.append(f"#{token.lexeme}")

    def code_gen_push_rv(self , token:Token , param=None):
        self.semantic_stack.append(self.registers["rv"])

    def code_gen_push_array(self , token:Token , param=None):
        size = self.semantic_stack.pop()
        temp = self.get_tempblock_var()
        self.add_code(op="MULT" , r1=f"#{self.word_size}" , r2=size , r3=temp)
        ind = self.semantic_stack.pop()
        self.add_code(op="ADD" , r1=ind , r2=temp , r3=temp)
        self.semantic_stack.append(f"@{temp}")
        
    def code_gen_push_zero(self , token:Token , param:None):
        self.semantic_stack.append("#0")


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

    def code_gen_function_input_pass(self , token:Token , param=None):
        self.function_input_pointers.append(len(self.semantic_stack))

    def code_gen_function_call(self , token:Token , param=None):
        for d in range(self.function_data_pointer , self.data_address , self.word_size):
            self.stack_push(d)
        for d in range(self.function_temp_pointer , self.temp_addres  , self.word_size):
            self.stack_push(d)
        self.stack_store_registers()
        
        pointer = self.function_input_pointers.pop()
        for f_i in range(pointer , len(self.semantic_stack)):
            self.stack_push(self.semantic_stack.pop())

        self.add_code(op="ASSIGN" , r1=f"#{len(self.program_block)+2}" , r2=self.registers["ra"] )
        self.add_code(op="JP" , r1=self.semantic_stack.pop())

        self.stack_load_registers()
        for d in range(self.temp_addres , self.function_temp_pointer , -self.word_size):
            self.stack_pop(d - self.word_size)
        for d in range(self.data_address , self.function_data_pointer, -self.word_size):
            self.stack_pop(d - self.word_size)

        res = self.get_tempblock_var()
        self.add_code(op="ASSIGN" , r1=self.registers["rv"] , r2=res)
        self.semantic_stack.append(res)


    def code_gen_jump_placeholder(self , token:Token , param=None):
        self.scope_manage_create_jump_placeholder(scope_type=param[0])

    def code_gen_backpatch_jump(self , token:Token , param:None):
        self.scope_manage_backpatch_jump(scope_type=param[0])


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

    
    def scope_manage_create_jump_placeholder(self , scope_type):
        self.scopeFrames[scope_type].create_jump_placeholder()
    
    def scope_manage_backpatch_jump(self , scope_type):
        self.scopeFrames[scope_type].backpatch_jump()
    
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

    def add_template(self):
        self.symbol_table.add(Token("ID" , "output"))
        self.symbol_table.find_record_by_id("output").address=5
        self.add_code(op="ASSIGN" , r1=f"#{self.stack_address}" , r2=self.registers["sp"])
        self.add_code(op="ASSIGN" , r1=f"#{self.stack_address}" , r2=self.registers["fp"])

        self.add_code(op="ASSIGN" , r1=f"#9999" , r2=self.registers["ra"])
        self.add_code(op="ASSIGN" , r1=f"#9999" , r2=self.registers["rv"])
        self.add_code(op="JP" , r1=f"{len(self.program_block)+5}")
        self.stack_pop(self.registers["rv"])
        self.add_code(op="PRINT" , r1=self.registers["rv"])
        self.add_code(op="JP" , r1=f"@{self.registers["ra"]}")

        self.get_datablock_var()

    def set_exec_block(self , name):
        record = self.symbol_table.find_record_by_id(name)
        line = int(self.semantic_stack[0])
        print(line)
        self.add_code(op="JP" , r1=record.address , line=line)

    def add_code(self , op , r1="" , r2="" , r3="" , line=None):
        if line != None :
            self.program_block[line] = f"({op} ,{r1} ,{r2} ,{r3})"
        else :
            self.program_block.append(f"({op}, {r1}, {r2}, {r3})")

    def export(self , file_path="output.txt"):
        with open(file_path, "w") as f:
            for i, line in enumerate(self.program_block):
                if '(' not in line:
                    line = "(ASSIGN , 0, 0 , )"
                f.write(f"{i}\t{line}\n")
