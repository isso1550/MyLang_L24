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

        #Used to find out whether array index value is currently on stack
        #Helps avoid popping from empty or popping other values
        self.arr_idx_depth = 0

        #Structures data object
        self.structData = {}

        #Switch counter to get ids
        self.switchcounter = 0
        #Switch data array
        self.switchdata = [-1]
    
    def increaseIndexDepth(self):
        self.arr_idx_depth = self.arr_idx_depth + 1

    def incLine(self, lc):
        self.lc = lc

    def printRegStack(self):
        print(self.regStack)

    def popStack(self):
        self.regStack.pop()

    def nextReg(self):
        regc = self.regc[self.func_depth]
        self.regc[self.func_depth] += 1
        return '%'+ str(regc)
    
    def raiseException(self, message):
        raise Exception(message + f" : line {self.lc}")

    def sendWarning(self, message):
        WARNING = '\033[93m'
        ENDC = '\033[0m'
        print(WARNING + "WARNING: " + message + f" : {self.lc}" + ENDC)

    def generateHeader(self):
        txt = "target triple = \"x86_64-w64-windows-gnu\"\n"
        txt += "@.str = private unnamed_addr constant [4 x i8] c\"\\0A%d\\00\", align 1\n"
        txt += "@.str.1 = private unnamed_addr constant [4 x i8] c\"\\0A%f\\00\", align 1\n"
        txt += "@.str.2 = private unnamed_addr constant [3 x i8] c\"%d\\00\", align 1\n"
        txt += "@.str.3 = private unnamed_addr constant [4 x i8] c\"%lf\\00\", align 1\n"
        txt += "declare dso_local i32 @printf(ptr noundef, ...) #1\n"
        txt += "declare dso_local i32 @scanf(ptr noundef, ...) #1\n"
        main_start = "define dso_local i32 @main() #0 {\n"
        return txt, main_start

    def generateDeclaration(self, dtype, vname, g=False, gval=None, arr=False, size=1):
        #Verify
        match dtype:
            case 'int' | 'i32':
                dtype = 'i32'
            case 'bool' | 'i1':
                dtype = 'i1'
            case 'double':
                dtype = 'double'
            case _:
                self.raiseException(f"Unknown var type {dtype}")

        #Var already declared as local
        if vname in self.varData[self.func_depth].keys():
            self.raiseException(f"Already declared {vname} as variable or function")
        
        #Var already declared as global
        if self.func_depth > 0:
            if vname in self.varData[0].keys():
                if self.varData[0][vname]['global'] == True:
                    self.raiseException(f"Already declared {vname} as global variable")

        if vname in self.funcData.keys():
            self.raiseException(f"Variable name {vname} already used as function name")
        
        if (arr):
            if (self.func_depth>0):
                pass
                #self.raiseException("Cannot declare arrays in functions")
            elem_dtype = dtype
            dtype = f"[{size} x {dtype}]"
            gval = 'zeroinitializer'
        
        if (g):
            if self.func_depth > 0:
                self.raiseException(f"Cannot declare global variable {vname} inside a function")
            #@x = dso_local global i32 0, align 4
            regc = '@' + vname
            if gval == None:
                if dtype == 'double':
                    gval = '0.0'
                else:
                    gval = 0
            
            txt = f"{regc} = dso_local global {dtype} {gval}\n"
        else:
            regc = self.nextReg()
            txt = f"\t{regc} = alloca {dtype}\n"
        #UWAGA INIT ARR
        if (arr): dtype = elem_dtype + "[]"

        depth = 0 if g else self.func_depth
        self.varData[depth][vname] = {"dtype":dtype, "reg":regc, "init":arr, "global":g, "array": arr, "size": size, "is_param": False}
        return txt
    
    def generateStructDeclaration(self, sname, struct_arg_list):
        #%struct.myType = type { i32, i32 }
        types = [x[0] for x in struct_arg_list]
        field_names = [x[1] for x in struct_arg_list]
        for i in range(len(types)):
            t = types[i]
            match t:
                case 'int':
                    types[i] = 'i32'
                case 'bool':
                    types[i] = 'i1'
                case 'double':
                    pass
                case _:
                    self.raiseException(f"Unknown type {t} in struct declaration")

        self.structData[sname] = {"types" : types, "field_names" : field_names}
        txt = f"%struct.{sname} = type {'{'} {', '.join(types)} {'}'}\n"
        
        return txt
    
    def generateStructObjectDeclaration(self, sname, vname, g=False):
        if not sname in self.structData.keys():
            self.raiseException(f"Unknown struct type {sname}")

        #%2 = alloca %struct.myType, align 4
        
        if (vname in self.varData[self.func_depth].keys()):
            self.raiseException(f"Var {vname} already declared")
        elif (vname in self.varData[0].keys()):
            if self.varData[0][vname]['global'] == True:
                self.raiseException(f"Var {vname} already declared")

        if (g):
            #@s1 = dso_local global %struct.myType zeroinitializer, align 4
            regc = "@"+vname
            txt = f"\t{regc} = dso_local global %struct.{sname} zeroinitializer\n"
        else:
            regc = self.nextReg()
            txt = f"\t{regc} = alloca %struct.{sname}\n"

        depth = 0 if g else self.func_depth
        self.varData[depth][vname] = {"dtype":"struct."+sname, "reg":regc, "init":True, "global":g, "array": False, "size": 1, "is_param": False}
        return txt




    def searchVarData(self, vname):
        try:
            data = self.varData[self.func_depth][vname]
        except:
            #Not found in local context
            try:
                data = self.varData[0][vname]
                if data['global']==False:
                    self.raiseException(f"Unknown assigment error for var {vname}")
            except Exception as e:
                #Not found in global context
                self.raiseException(f"Cannot assign to unknown variable {vname}")
        return data

    def generateAssignment(self, vname):
        txt = ""
        data = self.searchVarData(vname)
        dtype = data['dtype']

        (valdtype, valreg) = self.regStack.pop()
        varreg = data['reg']

        if '[]' in dtype:
            #Get pointer to element
            try:
                txt = self.generateLoadArrayElemPtr(dtype, varreg)
                (dtype, varreg) = self.regStack.pop()
            except IndexError:
                #Trying to assign array
                self.raiseException("Cannot assign to entire array. Use brackets to initialize the entire array")
                pass

        if (dtype != valdtype):
            if (valdtype == 'i64' and 'struct' in dtype):
                #Special case: assigning structures
                pass
            else:
                self.raiseException(f"Cannot assign {valdtype} to {dtype} {vname}")

        if 'struct.' in dtype:
            dtype = 'i64'
        txt += f"\tstore {dtype} {valreg}, ptr {varreg}\n"
        data['init'] = True
        return txt
    
    
    
    def generateArrayAssignment(self, vname, len):

        data = self.searchVarData(vname)
        if not (data['array']):
            self.raiseException(f"Tuple assignment can only be used on arrays (var {vname} is not an array)")
        txt = ""
        elem_dtype = data['dtype'][:-2]

        if (len < int(data['size'])):
            self.raiseException(f"Not enough elements to assing to array")
        if (len > int(data['size'])):
            self.raiseException(f"Too many values in array assignment")
            
        for i in range(len-1, -1, -1):
            
            (valdtype, valreg) = self.regStack.pop()
            self.regStack.append(('i32', i))
            self.increaseIndexDepth()
            #Get pointer to element
            txt += self.generateLoadArrayElemPtr(data['dtype'], data['reg'])
            (_, varreg) = self.regStack.pop()
            

            if (valdtype != elem_dtype):
                self.raiseException(f"Cannot assign {valdtype} to {elem_dtype} {vname}")

            txt += f"\tstore {elem_dtype} {valreg}, ptr {varreg}\n"

        return txt
    
    def generateStructAssigment(self, vname, field_name):
        data = self.searchVarData(vname)
        stype = data['dtype'].split('.')[1]

        sdata = self.structData[stype]
        field_names = sdata['field_names']
        if not field_name in field_names:
            self.raiseException(f"Unknown field name {field_name} for struct type {stype}")
        field_idx = field_names.index(field_name)
        field_type = sdata['types'][field_idx]
        (valdtype, valreg) = self.regStack.pop()
        if valdtype != field_type:
            self.raiseException(f"Wrong type in struct field assignment. Got {valdtype} expected {field_type}")

        sreg = data['reg']
        txt = self.generateLoadStructFieldPointer(stype, sreg, field_idx)
        (dtype, regc) = self.regStack.pop()
        txt += f"\tstore {valdtype} {valreg}, ptr {regc}\n"
        return txt
    
    def generateLoadStructField(self, vname, field_name):
        data = self.searchVarData(vname)
        stype = data['dtype'].split('.')[1]

        sdata = self.structData[stype]
        field_names = sdata['field_names']
        if not field_name in field_names:
            self.raiseException(f"Unknown field name {field_name} for struct type {stype}")
        field_idx = field_names.index(field_name)
        field_type = sdata['types'][field_idx]

        txt = self.generateLoadStructFieldPointer(stype, data['reg'], field_idx)
        (ptrdtype, ptrregc) = self.regStack.pop()
        #%8 = load i32, ptr %7, align 4
        regc = self.nextReg()
        txt += f'\t{regc} = load {field_type}, ptr {ptrregc}\n'
        self.regStack.append((field_type, regc))
        return txt
    
    def generateLoadStructFieldPointer(self, stype, sreg, index):
        #%2 = getelementptr inbounds %struct.myType, ptr %1, i32 0, i32 0
        regc = self.nextReg()
        txt = f"\t{regc} = getelementptr inbounds %struct.{stype}, ptr {sreg}, i32 0, i32 {index}\n"
        self.regStack.append(('struct_field_ptr', regc))
        return txt
    
    def generateLoadVar(self, vname):
        try:
            data = self.varData[self.func_depth][vname]
        except: 
            try:
                data = self.varData[0][vname]
                if data['global']==False:
                    self.raiseException(f"Unknown variable {vname}")
            except Exception as e:
                self.raiseException(f"Unknown variable {vname}")
        dtype = data['dtype']
        varreg = data['reg']
        varinit = data['init']
        g = data['global']
        if not varinit:
            self.raiseException(f"Trying to load uninitialized variable {vname}")

        arr = data['array']
        txt = ""
        if (arr):
            if self.arr_idx_depth > 0:
                #Get pointer to element
                txt += self.generateLoadArrayElemPtr(data['dtype'], data['reg'])
                (dtype, varreg) = self.regStack.pop()
                regc = self.nextReg()
                #Load value from pointer
                txt += f"\t{regc} = load {dtype}, ptr {varreg}\n"
                self.regStack.append((dtype,regc))
            else:
                #No index on stack, get entire array
                txt = self.generateLoadArrayPtr(data)
        elif '.' in dtype:
            #%4 = load i64, ptr %1, align 4
            if dtype.split('.')[1] in self.structData.keys():    
                #regc = self.nextReg()
                #txt += f"\t{regc} = load %{dtype}, ptr {varreg}\n"
                #self.regStack.append((dtype, regc))
                txt += self.loadEntireStruct(varreg)
        else:
            regc = self.nextReg()
            txt += f"\t{regc} = load {dtype}, ptr {varreg}\n"
            self.regStack.append((dtype,regc))
        return txt
    def loadEntireStruct(self, varreg):
        regc = self.nextReg()
        txt = f"\t{regc} = load i64, ptr {varreg}\n"
        self.regStack.append(('i64', regc))
        return txt

    def generateLoadArrayElemPtr(self, arr_dtype, arr_varreg):
        
        varreg = arr_varreg
        dtype = arr_dtype
        try:
            (idxdtype, index) = self.regStack.pop()
            self.arr_idx_depth = self.arr_idx_depth - 1
            #print(f"Lowered index to {self.arr_idx_depth}")
        except Exception as e:
            #No index on stack -> load pointer to array
            raise IndexError(f"{e} No index -> load pointer")
        if (idxdtype != 'i32'):
            self.raiseException(f"Array index must be int")

        txt = ""
        if (self.func_depth > 0):
            #Load value of pointer to input param -> only in func

            #%4 = alloca ptr, align 8
             #   store ptr %0, ptr %3, align 8
             #   store ptr %1, ptr %4, align 8
             #   %5 = load ptr, ptr %4, align 8
             #   %6 = getelementptr inbounds i32, ptr %5, i64 1
             #   store i32 -1, ptr %6, align 4
            regc = self.nextReg()
            txt = f"\t{regc} = load ptr, ptr {varreg}\n"
            ptr_reg = regc
        else:
            ptr_reg = varreg
        regc = self.nextReg()
        elem_dtype = dtype[:-2]
        txt += f"\t{regc} = getelementptr inbounds {elem_dtype}, ptr {ptr_reg}, i32 {index}\n"

        #regc = self.nextReg()
        #%7 = load i32, ptr %6, align 4
        #txt += f"\t{regc} = load {elem_dtype}, ptr {regc}\n"
        self.regStack.append((elem_dtype, regc))
        return txt
    
    def generateLoadArrayPtr(self, data):
        varreg = data['reg']
        dtype = data['dtype']
        size = data['size']
        

        elem_dtype = dtype[:-2]
        #txt = f"\t{regc} = getelementptr inbounds [{size} x {elem_dtype}], ptr {varreg}, i64 0,  i64 0\n"
        txt = ""
        if (self.func_depth > 0):
            #Load value of pointer to input param -> only in func

            #%4 = alloca ptr, align 8
             #   store ptr %0, ptr %3, align 8
             #   store ptr %1, ptr %4, align 8
             #   %5 = load ptr, ptr %4, align 8
             #   %6 = getelementptr inbounds i32, ptr %5, i64 1
             #   store i32 -1, ptr %6, align 4
            regc = self.nextReg()
            txt += f"\t{regc} = load ptr, ptr {varreg}\n"
            ptr_reg = regc
        else:
            ptr_reg = varreg
            regc = self.nextReg()
            txt += f"\t{regc} = getelementptr inbounds {elem_dtype}, ptr {ptr_reg}, i32 0\n"
        
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

        if (dtype[-2:] == '[]'):
            self.raiseException("Cannot print entire array, choose one element.")
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
            case 'i64':
                #Struct
                self.raiseException(f"Cannot print entire structure")
            case _:
                self.raiseException(f"Unknown type {dtype}")
        self.regStack.append(('i32',0))
        return txt
    
    def generateRead(self, target, read_double=False):
        #%2 = call i32 (ptr, ...) @scanf(ptr noundef @.str, ptr noundef %1)
        data = self.searchVarData(target)
        regc = self.nextReg()
        targetdtype = data['dtype']
        if (targetdtype == 'i1'):
            self.raiseException("Cannot read bool values. Use temporary int variable to read bool.")
        if not read_double:
            if targetdtype != 'i32':
                self.sendWarning(f"Using read (reads int) to assign to type {targetdtype}")
            txt = f"\t{regc} = call i32 (ptr, ...) @scanf(ptr noundef @.str.2, ptr noundef {data['reg']})\n"
        else:
            if targetdtype != 'double':
                self.sendWarning(f"Using read (reads double) to assign to type {targetdtype}")
            txt = f"\t{regc} = call i32 (ptr, ...) @scanf(ptr noundef @.str.3, ptr noundef {data['reg']})\n"
        data['init'] = True
        self.regStack.append(('i32',0))
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
            self.raiseException(f"Cannot perform operation '{op}' on different types {dtype1} {dtype2}")

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
                op = 'xor'
            
            case _:
                self.raiseException("Unknown boolean operator")

        txt = f"\t{regc} = {op} {dtype1} {regc1}, {regc2}\n"

        
        self.regStack.append((dtype, regc))
        return txt
    
    def generateNegation(self):
        regc = self.nextReg()

        dtype1, regc1 = self.regStack.pop()
        if (dtype1 != 'i1'):
            self.raiseException(f"Cannot negate non-bool values {dtype1, regc1}")
        txt = f"\t{regc} = add nsw i1 {regc1}, 1\n"
        self.regStack.append((dtype1, regc))
        return txt
    
    def generateEnterFunctionDefinition(self, rettype, fname):
        #Entering function definition (name, args...)
        #define dso_local i32 @fun(i32 noundef %0, i32 noundef %1) #0 {
        #}
        if fname in self.varData[0].keys():
            self.raiseException(f"Variable or function with name {fname} already exists")

        if self.func_depth > 0:
            self.raiseException(f"Cannot create nested functions: {fname}")

        retstruct = False
        match rettype:
            case 'int':
                rettype = 'i32'
            case 'bool':
                rettype = 'i1'
            case 'double':
                rettype = 'double'
            case _:
                if 'struct.' in rettype:
                    #Block struct returns
                    self.raiseException(f"Functions cannot return structures. Func: {fname}")
                    if rettype.split('.')[1] in self.structData.keys():
                        retstruct = True
                        
                    else:
                        pass
                else:        
                    self.raiseException(f"Unknown return type for function {fname} : {rettype}")

        if retstruct:
            txt = f"define dso_local i64 @{fname}("
        else:
            txt = f"define dso_local {rettype} @{fname}("

        self.func_depth += 1
        if (len(self.varData) <= self.func_depth):
            self.varData.append({})
        else:
            #Clear func_depth's variable storage to allow reassigning local variables in other functions
            self.varData[self.func_depth] = {}  

        if (len(self.regc) <= self.func_depth):
            self.regc.append(0)
        else:
            #Clear func_depth's reg counter to allow starting from 0 in other funcctions
            self.regc[self.func_depth] = 0

        self.funcData[fname] = {"rettype" : rettype, "argtypes":[]}
        self.analyzedFunc = fname

        self.varData[0][fname] = {"dtype":'function', "reg":None, "init":True, "global":False}

        self.func_arg_list = []
        return txt
    
    def generateEnterFunctionDefinitionNoArgs(self, rettype, fname):
        #Enter function definition (special case with 0 args)
        txt = self.generateEnterFunctionDefinition(rettype, fname)
        txt += f") {'{'}\n"

        self.nextReg() #Artificialy increase next temp reg to %1
        return txt

    def generateFunctionArgument(self, dtype, vname, array=False, struct=False):
        #Add function argument declaration to stack and log
        #Verify
        if (array):
            dtype = dtype[:-2]
            if (dtype == 'int'):
                dtype = 'i32'
            elif (dtype == 'bool'):
                dtype = 'i1'
            elif (dtype =='double'):
                dtype = 'double'
        
        elif (struct):
            if not (dtype in self.structData.keys()):
                self.raiseException(f"Unknown struct type {dtype}")

        else:
            if (dtype == 'int'):
                dtype = 'i32'
            elif (dtype == 'bool'):
                dtype = 'i1'
            elif (dtype =='double'):
                dtype = 'double'
            else:
                self.raiseException(f"Unknown var type {dtype}")
            
        if vname in self.varData[self.func_depth].keys():
            self.raiseException(f"Already declared {vname}")
        #Add
        

        regc = self.nextReg()

        if (array):
            txt = f"ptr noundef {regc}"
        elif (struct):
            txt = f"i64 {regc}"
        else:
            txt = f"{dtype} noundef {regc}"
        self.func_arg_list.append(txt)

        if (array):
            dtype = dtype + '[]'
        elif(struct):
            dtype = "struct." + dtype
        self.funcData[self.analyzedFunc]['argtypes'].append(dtype)
        self.funcArgsStack.append((dtype, vname, regc))
        #return txt
    
    def generateExitFunctionDefinition(self):
        #Exiting function definition (first line with name, args...)
        txt = ', '.join(self.func_arg_list)
        txt += f") {'{'}\n"
        self.nextReg()
        while (self.funcArgsStack):
            dtype, vname, regc = self.funcArgsStack.popleft()
            if (dtype[-2:] == "[]"):
                #%2 = alloca ptr, align 8
                #store ptr %0, ptr %2, align 8
                alloca_reg = self.nextReg()
                txt += f"\t{alloca_reg} = alloca ptr\n"
                txt += f"\tstore ptr {regc}, ptr {alloca_reg}\n"
                #dtype = dtype[:-2]
                self.varData[self.func_depth][vname] = {"dtype":dtype, "reg":alloca_reg, "init":True, "global":False, "array": True, "size": None, "is_param": True}
            elif ('struct.' in dtype):
                #%2 = alloca %struct.myType, align 4
                alloca_reg = self.nextReg()
                txt += f"\t{alloca_reg} = alloca %{dtype}\n"
                #store i64 %0, ptr %2, align 4
                txt += f"\tstore i64 {regc}, ptr {alloca_reg} \n"
                self.varData[self.func_depth][vname] = {'dtype':dtype, 'reg':alloca_reg, 'init': True, 'global': False, 'array':False, 'size': None, 'is_param':True}
            else:
                self.regStack.append((dtype, regc))
                txt += self.generateDeclaration(dtype, vname)
                txt += self.generateAssignment(vname)
        self.func_arg_list = []
        return txt
    
    

    def exitFunctionDeclaration(self):
        #Exiting ENTIRE function declaration
        dtype = self.funcData[self.analyzedFunc]['rettype']
        default_val = 0.0 if dtype == 'double' else 0
        if ('struct.' in dtype):
            dtype = 'i64'
        txt = f'\n\tret {dtype} {default_val}'
        self.func_depth -= 1
        return txt

    def generateReturn(self):
        
        (dtype, reg) = self.regStack.pop()

        txt = ""
        if ('[]' in dtype):
            #Get pointer
            try:
                txt += self.generateLoadArrayElemPtr(dtype, reg)
            except IndexError as e:
                self.raiseException("Cannot return entire array")
            
            dtype, el_reg = self.regStack.pop()
            reg = self.nextReg()
            #Load value
            txt += f"\t{reg} = load {dtype}, ptr {el_reg}\n"
        else:
            self.nextReg()
            pass
            
        expected_ret = self.funcData[self.analyzedFunc]['rettype']

        if (dtype != expected_ret):
            if (dtype == 'i64') and ('struct.' in expected_ret):
                dtype = 'i64'
            else:
                self.raiseException(f"Function must return type specified in declaration got: {dtype} expected {expected_ret}")
        
    
        txt += f'\tret {dtype} {reg}\n'
        return txt
    
    def generateEnterCall(self, fname):
        #call i32 @fun(i32 noundef 1, i32 noundef 2)
        #Prepare to handle call
        self.callStack.append((0, fname, []))
        #call_arg_n, calledFunc, call_arg_list = self.callStack.pop()

    def generateCallArg(self):
        dtype, reg = self.regStack.pop()

        call_arg_n, calledFunc, call_arg_list = self.callStack.pop()

        if calledFunc not in self.funcData.keys():
            self.raiseException(f"Calling function {calledFunc} without definition or before it's definition")

        try:
            expected_type = self.funcData[calledFunc]['argtypes'][call_arg_n]
        except IndexError as e:
            self.raiseException(f"Too many arguments passed to {calledFunc} call. Expected {len(self.funcData[calledFunc]['argtypes'])}")
        call_arg_n += 1

        if (dtype != expected_type):
            if (dtype == "ptr" and "[]" in expected_type):
                pass
            elif (dtype == "i64" and "struct." in expected_type):
                pass
            else:
                self.raiseException(f"Wrong argument type {dtype} expected {expected_type} function {calledFunc}")
        
        if ('[]' in dtype):
            dtype = "ptr noundef"

        #if ('.' in dtype):
        #    dtype = 'i64'

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
            self.raiseException(f"Unknown function {fname}")
        rettype = data['rettype']

        if (len(call_arg_list) < len(self.funcData[fname]['argtypes'])):
            self.raiseException(f"Not enough arguments passed to {fname} call. Got {len(call_arg_list)} Expected {len(self.funcData[fname]['argtypes'])}")
        
        regc = self.nextReg()

        if 'struct' in rettype:
            txt = f"\t{regc} = call i64 @{fname}("
        else:
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

    
    def generateEnterSwitchbody(self, case_count):
        (switchdtype, switchreg) = self.regStack.pop()
        #Rolling registers
        regstart = self.regc[self.func_depth]

        self.switchcounter = self.switchcounter + 1
        self.switchdata.append({'switchdtype': switchdtype, 'switchreg': switchreg, 'switchvals' : [], "current_reg": regstart, "firstreg":regstart})


    def generateEnterCaseblock(self):
        switch_id = self.switchcounter
        case_number = str(switch_id) + "_" + str(len(self.switchdata[switch_id]['switchvals']))
        label = "case" + case_number
        txt = f"{label}:\n"
        return txt
    
    def generateEnterCase_value(self):
        switch_id = self.switchcounter

        #Set current reg to continue switch header
        current_reg = self.switchdata[switch_id]['current_reg']
        self.continue_reg = self.regc[self.func_depth]
        self.regc[self.func_depth] = current_reg

    def generateExitCase_value(self):
        switch_id = self.switchcounter
        (valdtype, valregc) = self.regStack.pop()
        self.switchdata[switch_id]['switchvals'].append((valdtype,valregc))

        #Save current reg to use later
        self.switchdata[switch_id]['current_reg'] = self.regc[self.func_depth] 
        #Set main reg to remembered value
        #Reg order is most important, its values will be later fixed using fixRegs()
        self.regc[self.func_depth] = self.continue_reg

        
    
    def generateExitCaseblock(self):
        switch_id = self.switchcounter
        label = "switchend" + str(switch_id)
        txt = f"\tbr label %{label}\n"
        return txt
    
    def generateEnterDefaultblock(self):
        switch_id = self.switchcounter
        label = "default" + str(switch_id)
        txt = f"{label}:\n"
        return txt
    
    def generateExitDefaultblock(self):
        switch_id = self.switchcounter
        end_label = "switchend" + str(switch_id)
        txt = f"\tbr label %{end_label}\n"
        return txt
    
    def generateExitSwitchbody(self):
        switch_id = self.switchcounter
        switchdata = self.switchdata[switch_id]
        switchvals = switchdata['switchvals']
        switchdtype = switchdata['switchdtype']
        switchreg = switchdata['switchreg']
        switchregstart = switchdata['current_reg']

        txt = ""
        case_id = 0

        current_main_reg = self.regc[self.func_depth]
        switch_first_reg = self.switchdata[switch_id]['firstreg']

        self.regc[self.func_depth] = switchregstart

        for pair in switchvals:
            #%8 = icmp eq i32 %7, 5
	        #br i1 %8, label %ifblock1, label %exitif1
            casedtype, casereg = pair
            if (casedtype != switchdtype):
                self.raiseException(f"Cannot compare case value type {casedtype} to switch value type {switchdtype}")

            regc = self.nextReg()
            txt += f"\t{regc} = icmp eq {switchdtype} {switchreg}, {casereg}\n"
            label = "case" + str(switch_id) + "_" + str(case_id)
            continue_label = "continue" + str(switch_id) + "_" + str(case_id)
            txt += f"\tbr i1 {regc}, label %{label}, label %{continue_label}\n"
            txt += f"{continue_label}:\n"
            case_id += 1
        def_label = "default" + str(switch_id)
        txt += f"\tbr label %{def_label}\n"

        end_label = "switchend" + str(switch_id)
        end_txt = f"{end_label}:\n"
        
        switch_last_reg = self.regc[self.func_depth]

        n_ops = current_main_reg - switch_first_reg
        self.regc[self.func_depth] = switch_last_reg + n_ops

        return txt, end_txt, current_main_reg, switch_first_reg, switch_last_reg
            
        