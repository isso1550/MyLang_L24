from collections import deque

class LLVMGenerator:
    def __init__(self):
        #Storage for information about variables
        #Array to allow use of same name local vars in different functions
        #Array of lists, varData[x][y] x - func depth y - variable
        self.varData = [{}]

        #Local tmp label counter
        #Array to allow use in functions, regc[x][y] x - func depth y - current label
        self.regc = [1]

        #Stack for expression evaluations -> evaluate most important part, put to stack, continue
        #Also used for loading values before calls etc...
        self.regStack = deque()

        #storage for information about function arguments in its declaration
        #Necessary because correct declarations and assignments ought to be added to the beginning of func block
        self.funcArgsStack = deque()

        #storage for information about called functions, using stack to allow calls within calls (Test7, Test8)
        self.callStack = deque()

        #storage for info about functions
        self.funcData = {}

        #information which function is currently analyzed to get its data and print errors
        self.analyzedFunc = None 
        
        #Indicates function depth 0 if parsed lines in main, 1 if lines in func definition
        #Nested functions not allowed!
        self.func_depth = 0

        #Line counter for exception messages
        self.lc = 0

        #Count if block to assign numbered labels
        self.ifcounter = 0
        #Help with nested ifs (holds label numbers)
        self.ifstack = deque()
        #Help with transporting information whether if block has else block or not
        self.if_with_else = False

        #Count loops to assing numbered labels     
        self.loopcounter = 0
        #Help with nested loops
        self.loopstack = deque()

        #Allowed number types
        self.number_types = ['i32','double']
    
    def incLine(self, lc):
        self.lc = lc

    def nextReg(self):
        regc = self.regc[self.func_depth]
        self.regc[self.func_depth] += 1
        return '%'+ str(regc)
    
    def raiseException(self, message):
        raise Exception(message + f" : {self.lc}")

    def generateHeader(self):
        txt = "target triple = \"x86_64-w64-windows-gnu\"\n"
        txt += "@.str = private unnamed_addr constant [4 x i8] c\"\\0A%d\\00\", align 1\n"
        txt += "@.str.1 = private unnamed_addr constant [4 x i8] c\"\\0A%f\\00\", align 1\n"
        txt += "declare dso_local i32 @printf(ptr noundef, ...) #1\n"
        main_start = "define dso_local i32 @main() #0 {\n"
        return txt, main_start

    def generateDeclaration(self, dtype, vname, g=False, gval=None):
        #Verify
        match dtype:
            case 'int' | 'i32':
                dtype = 'i32'
            case 'bool' | 'i1':
                dtype = 'i1'
            case 'double':
                dtype = 'double'
            case _:
                raise Exception(f"Unknown var type {dtype}")
            
        if vname in self.varData[self.func_depth].keys():
            raise Exception(f"Already declared {vname}")
        #Add
        
        if (g):
            if self.func_depth > 0:
                raise Exception(f"Cannot declare global variable {vname} inside a function: {self.lc}")
            #@x = dso_local global i32 0, align 4
            regc = '@' + vname
            if gval == None:
                if dtype == 'double':
                    gval = '0.0'
                else:
                    gval = 0
            
            txt = f"{regc} = dso_local global {dtype} {gval}\n"
            self.varData[0][vname] = {"dtype":dtype, "reg":regc, "init":False, "global":g}
        else:
            regc = self.nextReg()
            txt = f"\t{regc} = alloca {dtype}\n"
            self.varData[self.func_depth][vname] = {"dtype":dtype, "reg":regc, "init":False, "global":g}
        return txt

    def generateAssignment(self, vname):
        try:
            data = self.varData[self.func_depth][vname]
        except:
            try:
                data = self.varData[0][vname]
                if data['global']==False:
                    raise Exception(f"Assignment error")
            except:
                raise Exception(f"Assignment error")
        dtype = data['dtype']
        varreg = data['reg']

        (dtype1, reg) = self.regStack.pop()

        #Auto conversions

        #if (dtype1=='number') & (dtype in self.number_types):
        #    dtype1 = dtype
        #    if dtype == 'double':
        #        if not '.' in reg:
        #            reg = reg + '.0'

        if (dtype != dtype1):
            raise Exception(f"Cannot assign {dtype1} to {dtype} {vname}: {self.lc}")

        txt = f"\tstore {dtype} {reg}, ptr {varreg}\n"
        data['init'] = True
        return txt


    def generateLoadVar(self, vname):
        regc = self.nextReg()

        try:
            data = self.varData[self.func_depth][vname]
        except: 
            try:
                data = self.varData[0][vname]
                if data['global']==False:
                    raise Exception(f"Unknown variable {vname}: {self.lc}")
            except:
                raise Exception(f"Unknown variable {vname}")
        dtype = data['dtype']
        varreg = data['reg']
        varinit = data['init']
        g = data['global']
        
        if not varinit:
            raise Exception(f"Trying to load uninitialized variable {vname}: {self.lc}")

        txt = f"\t{regc} = load {dtype}, ptr {varreg}\n"
        self.regStack.append((dtype,regc))

        return txt

    def generateConvert(self, target):
        regc = self.nextReg()
        (dtype,reg) = self.regStack.pop()
        txt = f"\t{regc} = zext i1 {reg} to {target}\n"
        self.regStack.append((target, regc))
        return txt

    def generatePrint(self):
        regc = self.nextReg()
        (dtype,reg) = self.regStack.pop()

        #Auto conversions

        #if (dtype == 'number'):
        #    if '.' in reg:
        #        dtype = 'double'
        #    else: dtype = 'i32'
        match(dtype):
            case 'i32':
                txt = f"\t{regc} = call i32 (ptr, ...) @printf(ptr noundef @.str, {dtype} noundef {reg})\n"
            case 'i1':
                #Convert i1 to i32
                txt = f"\t{regc} = zext i1 {reg} to i32\n"
                dtype = 'i32'

                reg1 = regc
                regc = self.nextReg()
                txt += f"\t{regc} = call i32 (ptr, ...) @printf(ptr noundef @.str, {dtype} noundef {reg1})\n"
            case 'double':
                txt = f"\t{regc} = call i32 (ptr, ...) @printf(ptr noundef @.str.1, {dtype} noundef {reg})\n"
            case _:
                raise Exception("Unknown type")

        return txt

    def generateFooter(self):
        txt = "\tret i32 0\n}"
        return txt
    
    def pushValToStack(self, val, dtype):
        #Pushing pure value to stack
        #Auto conversions

        if (dtype == 'number'):
            if '.' in val:
                dtype = 'double'
            else:
                dtype = 'i32'
        self.regStack.append((dtype, val))

    def prepareExpressionEvaluation(self, op=""):
        regc = self.nextReg()
        dtype2, regc2 = self.regStack.pop()
        dtype1, regc1 = self.regStack.pop()

        #Auto conversions

        #if (dtype1=='number') & (dtype2 in self.number_types):
        #    dtype1 = dtype2
        #    if (dtype2 == 'double'):
        #        if not '.' in regc1:
        #            regc1 = regc1 + '.0'
        #elif (dtype2=='number') & (dtype1 in self.number_types):
        #    dtype2 = dtype1
        #    if (dtype1 == 'double'):
        #        if not '.' in regc2:
        #            regc2 = regc2 + '.0'
    
        #Is it necessary?
        #if (dtype2 == 'number'): 
        #    dtype2 = 'double' if '.' in regc2 else 'i32'
        #if (dtype1 == 'number'):
        #    dtype1 = 'double' if '.' in regc1 else 'i32'

        if dtype1 != dtype2:
            raise Exception(f"Cannot perform operation '{op}' on different types {dtype1} {dtype2}: {self.lc}")

        return regc, dtype2, regc2, dtype1, regc1   


    def generateCalculation(self, op):
        regc, dtype2, regc2, dtype1, regc1  = self.prepareExpressionEvaluation(op)
        
        commands = {}
        commands['i32'] = {}
        commands['i32']['+'] = 'add'
        commands['i32']['-'] = 'sub'
        commands['i32']['*'] = 'mul'
        commands['i32']['/'] = 'sdiv'

        commands['double'] = {}
        commands['double']['+'] = 'fadd'
        commands['double']['-'] = 'fsub'
        commands['double']['*'] = 'fmul'
        commands['double']['/'] = 'fdiv'

        dtype = dtype1

        if dtype not in commands.keys():
            self.raiseException(f"Unknown type {dtype} or operation {op} not allowed")

        if op not in commands[dtype].keys():
            self.raiseException(f"Unknown operation {op} for type {dtype}")
        
        command = commands[dtype][op]
        txt = f"\t{regc} = {command} {dtype} {regc1}, {regc2}\n"
        self.regStack.append((dtype1, regc))
        return txt
    
    def generateCompare(self, op):
        #%10 = icmp eq i32 %6, %9
        regc, dtype2, regc2, dtype1, regc1  = self.prepareExpressionEvaluation(op=op)

        commands = {}
        commands['i32'] = {}
        commands['i32']['=='] = 'icmp eq'
        commands['i32']['>'] = 'icmp sgt'
        commands['i32']['>='] = 'icmp sge'
        commands['i32']['<'] = 'icmp slt'
        commands['i32']['<='] = 'icmp sle'
        commands['i32']['!='] = 'icmp ne'
        commands['i1'] = commands['i32']

        commands['double'] = {}
        commands['double']['=='] = 'fcmp oeq'
        commands['double']['>'] = 'fcmp ogt'
        commands['double']['>='] = 'fcmp oge'
        commands['double']['<'] = 'fcmp olt'
        commands['double']['<='] = 'fcmp ole'
        commands['double']['!='] = 'fcmp une'

        if dtype1 not in commands.keys():
            self.raiseException("Unknown type {dtype1}")
        if op not in commands[dtype1].keys():
            self.raiseException("Unknown comparison operator {op} for type {dtype1}")

        command = commands[dtype1][op]

        txt = f"\t{regc} = {command} {dtype1} {regc1}, {regc2}\n"

        dtype = 'i1'
        self.regStack.append((dtype, regc))
        return txt
    
    def generateBoolBinary(self, operator):
        #%10 = or i1 %6, %9
        regc, dtype2, regc2, dtype1, regc1  = self.prepareExpressionEvaluation(op=operator)
        dtype = 'i1'

        match operator:
            case '|':
                op = 'or'
            case '&':
                op = 'and'
            case '^':
                """
                #XOR TRUE IF AND=0 and OR=1
                # a xor b
                #t1 = a and b stack:t1
                #t2 = a or b  s:t1,t2
                #t3 = t1 = 0   s:t3
                #t4 = t2 = 1    s:t3,t4
                #t5 = t3 and t4
                op = "and"
                txt = f"\t{regc} = {op} {dtype1} {regc1}, {regc2}\n"
                self.regStack.append((dtype, regc))

                op = "or"
                regc = self.nextReg()
                txt += f"\t{regc} = {op} {dtype1} {regc1}, {regc2}\n"
                self.regStack.append((dtype, regc))

                regc, dtype2, regc2, dtype1, regc1  = self.prepareExpressionEvaluation(op=operator)
                txt += f"\t{regc} = icmp eq {dtype1} {regc1}, 0" 
                self.regStack.append((dtype,regc))

                regc = self.nextReg()
                txt += f"\t{regc} = icmp eq {dtype1} {regc2}, 1"
                self.regStack.append((dtype,regc))

                regc, dtype2, regc2, dtype1, regc1  = self.prepareExpressionEvaluation(op=operator)
                op = "and"
                txt += f"\t{regc} = {op} {dtype1} {regc1}, {regc2}\n"
                self.regStack.append((dtype, regc))
                return txt
                """
                op = 'xor'
            
            case _:
                raise Exception("Unknown compare operator")

        txt = f"\t{regc} = {op} {dtype1} {regc1}, {regc2}\n"

        
        self.regStack.append((dtype, regc))
        return txt
    
    def generateNegation(self):
        regc = self.nextReg()

        dtype1, regc1 = self.regStack.pop()
        if (dtype1 != 'i1'):
            raise Exception(f"Cannot negate non-bool values {dtype1, regc1}")
        txt = f"\t{regc} = add nsw i1 {regc1}, 1\n"
        self.regStack.append((dtype1, regc))
        return txt
    
    def generateEnterFunctionDefinition(self, rettype, fname):
        #Entering function definition (name, args...)
        #define dso_local i32 @fun(i32 noundef %0, i32 noundef %1) #0 {
        #}

        if self.func_depth > 0:
            raise Exception(f"Cannot create nested functions: {fname}")

        match rettype:
            case 'int':
                rettype = 'i32'
            case 'bool':
                rettype = 'i1'
            case 'double':
                rettype = 'double'
            case _:
                raise Exception(f"Unknown return type for function {fname} : {rettype}")

        txt = f"define dso_local {rettype} @{fname}("

        self.func_depth += 1
        if (len(self.varData) <= self.func_depth):
            self.varData.append({})
        else:
            self.varData[self.func_depth] = {}

        if (len(self.regc) <= self.func_depth):
            self.regc.append(0)
        else:
            self.regc[self.func_depth] = 0

        self.funcData[fname] = {"rettype" : rettype, "argtypes":[]}
        self.analyzedFunc = fname

        self.func_arg_list = []
        return txt
    
    def generateEnterFunctionDefinitionNoArgs(self, rettype, fname):
        #Enter function definition (special case with 0 args)
        txt = self.generateEnterFunctionDefinition(rettype, fname)
        txt += f") {'{'}\n"

        self.nextReg() #Artificialy increase next temp reg to %1
        return txt

    def generateFunctionArgument(self, dtype, vname):
        #Add function argument declaration to stack and log
        #Verify
        if (dtype == 'int'):
            dtype = 'i32'
        elif (dtype == 'bool'):
            dtype = 'i1'
        elif (dtype =='double'):
            dtype = 'double'
        else:
            raise Exception(f"Unknown var type {dtype}")
        if vname in self.varData[self.func_depth].keys():
            raise Exception(f"Already declared {vname}")
        #Add
        regc = self.nextReg()

        
        txt = f"{dtype} noundef {regc}"
        self.func_arg_list.append(txt)

        self.funcData[self.analyzedFunc]['argtypes'].append(dtype)
        self.funcArgsStack.append((dtype, vname, regc))
        #return txt
    
    def generateExitFunctionDefinition(self):
        #Exiting function definition (first line with name, args...)
        txt = ', '.join(self.func_arg_list)
        txt += f") {'{'}\n"
        self.nextReg()
        while (self.funcArgsStack):
            dtype, vname, regc = self.funcArgsStack.pop()
            self.regStack.append((dtype, regc))
            txt += self.generateDeclaration(dtype, vname)
            txt += self.generateAssignment(vname)
        self.func_arg_list = []
        return txt
    
    

    def exitFunctionDeclaration(self):
        #Exiting ENTIRE function declaration
        dtype = self.funcData[self.analyzedFunc]['rettype']
        default_val = 0.0 if dtype == 'double' else 0
        txt = f'\n\tret {dtype} {default_val}'
        self.func_depth -= 1
        return txt

    def generateReturn(self):
        self.nextReg()
        (dtype, reg) = self.regStack.pop()
        expected_ret = self.funcData[self.analyzedFunc]['rettype']

        if (dtype != expected_ret):
            self.raiseException(f"Function must return type of its declaration got: {dtype} expected {expected_ret}")
        
        txt = f'\tret {dtype} {reg}\n'
        return txt
    
    def generateEnterCall(self, fname):
        #call i32 @fun(i32 noundef 1, i32 noundef 2)
        #Prepare to handle call
        self.callStack.append((0, fname, []))
        #call_arg_n, calledFunc, call_arg_list = self.callStack.pop()

    def generateCallArg(self):
        dtype, reg = self.regStack.pop()
        call_arg_n, calledFunc, call_arg_list = self.callStack.pop()
        try:
            expected_type = self.funcData[calledFunc]['argtypes'][call_arg_n]
        except IndexError as e:
            raise Exception(f"Passed too many arguments to {calledFunc}: {self.lc}")
        call_arg_n += 1

        #Auto conversions

        #if (dtype=='number') and (expected_type in self.number_types):
        #    dtype = expected_type
        #    if expected_type == 'double':
        #        if not '.' in reg:
        #            reg = reg + '.'

        if (dtype != expected_type):
            raise Exception(f"Wrong argument type {dtype} expected {expected_type} function {calledFunc}: {self.lc}")
        txt = f"{dtype} {reg}"
        
        call_arg_list.append(txt)
        self.callStack.append((call_arg_n, calledFunc, call_arg_list))

    def generateExitCall(self):
        call_arg_n, calledFunc, call_arg_list = self.callStack.pop()
        #Start
        fname = calledFunc
        try:
            data = self.funcData[fname]
        except:
            raise Exception(f"Unknown function {fname}: {self.lc}")
        rettype = data['rettype']
        regc = self.nextReg()
        txt = f"\t{regc} = call {rettype} @{fname}("
        self.regStack.append((rettype, regc))
        #Args
        txt += ', '.join(call_arg_list)
        #End
        txt += ')\n'
        return txt
    
    def enterIf(self, with_else):
        self.if_with_else = with_else
    
    def generateEnterIf(self):
        #br i1 %4, label %5, label %8
        (dtype, regc) = self.regStack.pop()

        if dtype != 'i1':
            self.raiseException(f"If condition has to return boolean value")

        self.ifcounter = self.ifcounter + 1
        self.ifstack.append(self.ifcounter)

        label_true = f"ifblock{self.ifstack[-1]}"
        label_exit = f"elseblock{self.ifstack[-1]}" if self.if_with_else else f"exitif{self.ifstack[-1]}"
        txt = f"\tbr i1 {regc}, label %{label_true}, label %{label_exit}\n"
        txt += f"{label_true}:\n"
        return txt

    def generateEnterElseBlock(self):
        label = f"elseblock{self.ifstack[-1]}"
        txt = f"{label}:\n"
        return txt
    
    def generateExitIfBlock(self):
        label_exit = f"exitif{self.ifstack[-1]}"
        txt = f"\tbr label %{label_exit}\n"
        return txt
    
    def generateExitIf(self):
        label_exit = f"exitif{self.ifstack[-1]}"
        txt = f"{label_exit}:\n"

        self.if_with_else = False
        self.ifstack.pop()
        return txt



    def generateEnterWhileLoop(self):
        #   br label %3
        #3:
        self.loopcounter = self.loopcounter + 1
        self.loopstack.append(self.loopcounter)

        cond_label = f"whileloop_cond{self.loopstack[-1]}"
        txt = f"\tbr label %{cond_label}\n"
        txt += f"{cond_label}:\n"
        return txt
    
    def generateEnterWhileBlock(self):
        #br i1 %5, label %6, label %9
        (dtype, regc) = self.regStack.pop()
        if (dtype != 'i1'):
            self.raiseException("While loop condition has to resolve to bool value")
        block_label = f"whileloop_block{self.loopstack[-1]}"
        exit_label = f"whileloop_exit{self.loopstack[-1]}"
        txt = f"\tbr i1 {regc}, label %{block_label}, label %{exit_label}\n"
        txt += f"{block_label}:\n"
        return txt

    def generateExitWhileBlock(self):
        #   br label %3, !llvm.loop !5
        cond_label = f"whileloop_cond{self.loopstack[-1]}"
        txt = f"\tbr label %{cond_label}\n"
        exit_label = f"whileloop_exit{self.loopstack[-1]}"
        txt += f"{exit_label}:"
        self.loopstack.pop()
        return txt
    
    def negativeValue(self):
        #Converting last loaded number to negative
        (dtype, regc) = self.regStack.pop()
        self.regStack.append((dtype, '-'+regc))