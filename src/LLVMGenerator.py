from collections import deque

class LLVMGenerator:
    def __init__(self):
        self.varData = {}
        self.regc = 1

        self.regStack = deque()
        pass

    def nextReg(self):
        regc = self.regc
        self.regc += 1
        return '%'+ str(regc)
    

    def generateHeader(self):
        txt = "target triple = \"x86_64-w64-windows-gnu\"\n"
        txt += "@.str = private unnamed_addr constant [4 x i8] c\"\\0A%d\\00\", align 1\n"
        txt += "declare dso_local i32 @printf(ptr noundef, ...) #1\n"
        txt += "define dso_local i32 @main() #0 {\n"
        return txt

    def generateDeclaration(self, dtype, vname):
        #Verify
        if (dtype == 'int'):
            dtype = 'i32'
        elif (dtype == 'bool'):
            dtype = 'i1'
        else:
            raise Exception(f"Unknown var type {dtype}")
        if vname in self.varData.keys():
            raise Exception(f"Already declared {vname}")
        #Add
        regc = self.nextReg()

        self.varData[vname] = {"dtype":dtype, "reg":regc, "init":False}
        txt = f"\t{regc} = alloca {dtype}\n"
        #if val != None:
        #    txt += f"\tstore {dtype} {val}, ptr {regc}\n"
        #    self.varData[vname]['init'] = True
        return txt

    def generateAssignment(self, vname):
        data = self.varData[vname]
        dtype = data['dtype']
        varreg = data['reg']

        (dtype, reg) = self.regStack.pop()

        txt = f"\tstore {dtype} {reg}, ptr {varreg}\n"
        data['init'] = True
        return txt


    def generateLoadVar(self, vname):
        regc = self.nextReg()
        
        data = self.varData[vname]
        dtype = data['dtype']
        varreg = data['reg']
        varinit = data['init']
        
        if not varinit:
            raise Exception(f"Trying to load uninitialized variable {vname}")

        txt = f"\t{regc} = load {dtype}, ptr {varreg}\n"

        print(f"    Pushing {(dtype, regc)} to stack")
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
        print(f"    print: Grabbing {(dtype, reg)} from stack")
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
            case _:
                raise Exception("Unknown type")

        return txt

    def generateFooter(self):
        txt = "\tret i32 0\n}"
        return txt
    
    def pushValToStack(self, val, dtype):
        print(f'    Pushing pure value to stack {val}')
        self.regStack.append((dtype, val))

    def prepareExpressionEvaluation(self, op=""):
        regc = self.nextReg()
        dtype2, regc2 = self.regStack.pop()
        dtype1, regc1 = self.regStack.pop()

        if dtype1 != dtype2:
            raise Exception(f"Cannot perform operation '{op}' on different types {dtype1} {dtype2}")

        return regc, dtype2, regc2, dtype1, regc1   

    def generateAddition(self):
        #%6 = add nsw i32 %4, %5
        regc, dtype2, regc2, dtype1, regc1  = self.prepareExpressionEvaluation()
        
        txt = f"\t{regc} = add nsw i32 {regc1}, {regc2}\n"
        print(f"    Pushing addition result to stack")
        self.regStack.append((dtype1, regc))
        return txt
    
    def generateMultiply(self):
        #%11 = mul nsw i32 5, %10
        regc, dtype2, regc2, dtype1, regc1  = self.prepareExpressionEvaluation()
        
        txt = f"\t{regc} = mul nsw i32 {regc1}, {regc2}\n"
        print(f"    Pushing addition result to stack")
        self.regStack.append((dtype1, regc))
        return txt
    
    def generateCompare(self, operator):
        #%10 = icmp eq i32 %6, %9
        regc, dtype2, regc2, dtype1, regc1  = self.prepareExpressionEvaluation(op=operator)

        match operator:
            case '==':
                op = 'eq'
            case '>':
                op = 'sgt'
            case '>=':
                op = 'sge'
            case '<':
                op = 'slt'
            case '<=':
                op = 'sle'
            case '!=':
                op = 'ne'
            case _:
                raise Exception("Unknown compare operator")

        txt = f"\t{regc} = icmp {op} {dtype1} {regc1}, {regc2}\n"

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