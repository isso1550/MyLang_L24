import sys
from antlr4 import *
import re
from ExprParser import ExprParser
from ExprListener import ExprListener
from LLVMGenerator import LLVMGenerator

from collections import deque

class ListenerInterp(ExprListener):
    def __init__(self):
        self.generator = LLVMGenerator()
        self.txt = ""
        self.pre_main_txt = ""

        self.switch_header_txt = [""]
        self.append_to_switch_header = False
        self.switch_body_txt = [""]
        self.append_to_switch_body = False
        self.switchdepth = 0


        self.func_depth = 0
        self.result = {}

        self.exprStack = deque() 

    def appendText(self, txt, append_to_premain=False):
        if (self.append_to_switch_header):
            self.switch_header_txt[self.switchdepth] += txt
        elif (self.append_to_switch_body):
            self.switch_body_txt[self.switchdepth] += txt
        elif (self.func_depth > 0) | (append_to_premain):
            self.pre_main_txt += txt
        else:
            self.txt += txt

    def exitProgram(self, ctx: ExprParser.ProgramContext):
        header, main_start = self.generator.generateHeader()
        self.txt = header + self.pre_main_txt + main_start + self.txt + self.generator.generateFooter()
        with open("mylang.ll",'w') as f:
            f.write(self.txt)
            f.close()
 
    def exitDeclaration_no_assign(self, ctx: ExprParser.Declaration_no_assignContext):
        g = type(ctx.getChild(0)) == ExprParser.GlobalContext
        type_child_idx = 1 if g else 0 
        arr = type(ctx.getChild(type_child_idx)) == ExprParser.Arr_typeContext
        if (arr):
            
            dtype = ctx.getChild(type_child_idx).getChild(0).getText() 
            size = ctx.getChild(type_child_idx).getChild(2).getText()
        else:
            dtype = ctx.getChild(type_child_idx).getText()
            size = 1
        name_child_idx = 2 if g else 1
        vname = ctx.getChild(name_child_idx).getText()
        txt = self.generator.generateDeclaration(dtype, vname, g=g, arr=arr, size=size)
        self.appendText(txt, append_to_premain=g)
        
        return vname

    def exitDeclaration_assign(self, ctx: ExprParser.Declaration_assignContext):
        vname = self.exitDeclaration_no_assign(ctx)
        txt = self.generator.generateAssignment(vname)
        self.appendText(txt)

    def exitDeclaration_assign_array(self, ctx: ExprParser.Declaration_assign_arrayContext):
        vname = self.exitDeclaration_no_assign(ctx)
        len = (ctx.getChild(3).getChildCount() - 2 + 1)/2 
        txt = self.generator.generateArrayAssignment(vname, int(len))
        self.appendText(txt)
    
    def exitClassic_assignment(self, ctx: ExprParser.Classic_assignmentContext):
        if type(ctx.getChild(0)) == ExprParser.Array_elemContext:
            vname = ctx.getChild(0).getChild(0).getText()
        else:
            vname = ctx.getChild(0).getText()
        txt = self.generator.generateAssignment(vname)
        self.appendText(txt)

    def exitStruct_declaration(self, ctx: ExprParser.Struct_declarationContext):
        sname = ctx.getChild(1).getText()
        struct_arg_list = []
        tctx = ctx.getChild(3)
        elem_dtype = tctx.getChild(0).getChild(0).getText()
        elem_name = tctx.getChild(0).getChild(1).getText()
        
        if (tctx.getChild(0).getChildCount()>2):
                if (tctx.getChild(0).getChild(0).getText() == 'struct'):
                    self.generator.raiseException("Cannot use structures as struct fields")
                self.generator.raiseException("Cannot use arrays as struct fields")

        struct_arg_list.append((elem_dtype, elem_name))


        while(type(tctx.getChild(2)) == ExprParser.Struct_fieldsContext):
            tctx = tctx.getChild(2)
            elem_dtype = tctx.getChild(0).getChild(0).getText()
            elem_name = tctx.getChild(0).getChild(1).getText()
            if (tctx.getChild(0).getChildCount()>2):
                if (tctx.getChild(0).getChild(0).getText() == 'struct'):
                    self.generator.raiseException("Cannot use structures as struct fields")
                self.generator.raiseException("Cannot use arrays as struct fields")
            
            struct_arg_list.append((elem_dtype, elem_name))
        txt = self.generator.generateStructDeclaration(sname, struct_arg_list)
        self.appendText(txt, append_to_premain=True)

    def exitStruct_object_declaration(self, ctx: ExprParser.Struct_object_declarationContext):
        if (type(ctx.getChild(0)) == ExprParser.GlobalContext):
            g = True
            sname = ctx.getChild(2).getText()
            vname = ctx.getChild(3).getText()
        else:
            g = False
            sname = ctx.getChild(1).getText()
            vname = ctx.getChild(2).getText()
        txt = self.generator.generateStructObjectDeclaration(sname, vname, g=g)
        self.appendText(txt, append_to_premain=g)

    def enterError_no_arr_size(self, ctx: ExprParser.Error_no_arr_sizeContext):
        self.generator.raiseException("No array size specified")
    
    def exitArray_assignment(self, ctx: ExprParser.Array_assignmentContext):
        vname = ctx.getChild(0).getText()
        len = (ctx.getChild(2).getChildCount() - 2 + 1)/2 
        txt = self.generator.generateArrayAssignment(vname, int(len))
        self.appendText(txt)

    def exitStruct_assignment(self , ctx: ExprParser.Struct_assignmentContext):
        vname = ctx.getChild(0).getChild(0).getText()
        field_name = ctx.getChild(0).getChild(2).getText()
        txt = self.generator.generateStructAssigment(vname, field_name)
        self.appendText(txt)

    def exitCall_print(self, ctx: ExprParser.Call_printContext):
        txt = self.generator.generatePrint()
        self.appendText(txt)

    def exitCall_read(self, ctx: ExprParser.Call_readContext, read_double = False):
        if (ctx.getChildCount() <= 3):
            self.generator.raiseException("Read function requires 1 argument: target.")
        elif (ctx.getChildCount() > 4):
            self.generator.raiseException("Too many arguments passed to read(arg) call")
        target = ctx.getChild(2).getText()
        txt = self.generator.generateRead(target, read_double)
        self.appendText(txt)

    def exitCall_read_double(self, ctx: ExprParser.Call_read_doubleContext):
        self.exitCall_read(ctx, read_double=True)

    def exitValue_id(self, ctx: ExprParser.Value_idContext):
        vname = ctx.getText()
        txt = self.generator.generateLoadVar(vname)
        self.appendText(txt)

    def exitValue_int(self, ctx: ExprParser.Value_intContext):
        val = ctx.getText()
        dtype = 'number'
        self.generator.pushValToStack(val, dtype)

    def exitValue_double(self, ctx: ExprParser.Value_doubleContext):
        val = ctx.getText()
        dtype = 'number'
        self.generator.pushValToStack(val, dtype)


    def exitValue_bool(self, ctx: ExprParser.Value_boolContext):
        val = ctx.getText()
        dtype = 'i1'
        val = 1 if val=='true' else 0
        self.generator.pushValToStack(val, dtype)

    def exitValue_negation(self, ctx: ExprParser.Value_negationContext):
        txt = self.generator.generateNegation()
        self.appendText(txt)
    
    def exitValue_negative(self, ctx: ExprParser.Value_negativeContext):
        val = '-' + ctx.getChild(1).getText()
        dtype = 'number'
        self.generator.pushValToStack(val, dtype)
        #self.generator.negativeValue()

    def exitValue_array_elem(self, ctx: ExprParser.Value_array_elemContext):
        arr_ctx = ctx.getChild(0)
        vname = arr_ctx.getChild(0).getText()
        txt = self.generator.generateLoadVar(vname)
        self.appendText(txt)

    def exitValue_struct_elem(self, ctx: ExprParser.Value_struct_elemContext):
        vname = ctx.getChild(0).getChild(0).getText()
        field_name = ctx.getChild(0).getChild(2).getText()
        txt = self.generator.generateLoadStructField(vname, field_name)
        self.appendText(txt)

    def exitArray_elem(self, ctx: ExprParser.Array_elemContext):
        self.generator.increaseIndexDepth()

    def exitExpression(self, ctx: ExprParser.ExpressionContext):
        pass

    def exitExpr0(self, ctx: ExprParser.Expr0Context):
        if (ctx.getChildCount() > 2):
            if (ctx.getChild(0).getText() == '('):
                #If parathesis - just skip, the expression will auto-evaluate later
                return
            #Calculations required
            op = ctx.getChild(1).getText()
            match op:
                case '+' | '-' | '*' | '/':
                    txt = self.generator.generateCalculation(op)
                case '==' | '>' | '>=' | '<' | '<=' | '!=':
                    txt = self.generator.generateCompare(op)
                case '|' | '&' | '^':
                    txt = self.generator.generateBoolBinary(op)
                case _:
                    self.generator.raiseException(f"Unknown operation {op}")
            self.appendText(txt)
        elif (ctx.getChildCount() > 1):
            if (ctx.getChild(0).getText() != '~'):
                self.generator.raiseException(f"Unknown situation {ctx.getText()}")
            txt = self.generator.generateNegation()
            self.appendText(txt)
        else:
            pass
    
    def exitExpr1(self, ctx: ExprParser.Expr1Context):
        return self.exitExpr0(ctx)
    def exitExpr2(self, ctx: ExprParser.Expr2Context):
        return self.exitExpr0(ctx)


    def enterFunction_definition(self, ctx: ExprParser.Function_definitionContext):
        self.func_depth += 1
        #rettype = ctx.getChild(1).getText()
        if type(ctx.getChild(1).getChild(0)) == ExprParser.TypeContext:
            rettype = ctx.getChild(1).getText()
        else:
            rettype = "struct." + ctx.getChild(1).getChild(1).getText()
        fname = ctx.getChild(2).getText()
        txt = self.generator.generateEnterFunctionDefinition(rettype, fname)
        self.appendText(txt)

    def enterFunc_def_with_args(self, ctx: ExprParser.Func_def_with_argsContext):
        return self.enterFunction_definition(ctx)
    def enterFunc_def_no_args(self, ctx: ExprParser.Func_def_no_argsContext):
        self.func_depth += 1
        if type(ctx.getChild(1).getChild(0)) == ExprParser.TypeContext:
            rettype = ctx.getChild(1).getText()
        else:
            rettype = "struct." + ctx.getChild(1).getChild(1).getText()
        fname = ctx.getChild(2).getText()
        txt = self.generator.generateEnterFunctionDefinitionNoArgs(rettype, fname)
        self.appendText(txt)

    def exitFunc_arg(self, ctx: ExprParser.Func_argContext):
        
        if (ctx.getChild(1).getText() == "[]"):
            arr = True
            struct = False
            dtype = ctx.getChild(0).getText()
            vname = ctx.getChild(2).getText()
            dtype = dtype + "[]"
        else:
            arr = False
            if ctx.getChild(0).getText() == 'struct':
                struct = True
                dtype = ctx.getChild(1).getText()
                vname = ctx.getChild(2).getText()
            else:
                struct = False
                dtype = ctx.getChild(0).getText()
                vname = ctx.getChild(1).getText()
        self.generator.generateFunctionArgument(dtype, vname, array=arr, struct=struct)

    def exitFunc_args(self, ctx: ExprParser.Func_argsContext):
        txt = self.generator.generateExitFunctionDefinition()
        self.appendText(txt)
        
        
    def exitFunction_definition(self, ctx: ExprParser.Function_definitionContext):
        txt = self.generator.exitFunctionDeclaration()
        txt += "\n}\n"
        self.appendText(txt)
        self.func_depth -= 1

    def exitFunc_def_with_args(self, ctx: ExprParser.Func_def_with_argsContext):
        return self.exitFunction_definition(ctx)
    def exitFunc_def_no_args(self, ctx: ExprParser.Func_def_no_argsContext):
        return self.exitFunction_definition(ctx)
    
    

    def exitReturn(self, ctx: ExprParser.ReturnContext):
        txt = self.generator.generateReturn()
        self.appendText(txt)

    def enterCall_func(self, ctx: ExprParser.Call_funcContext):
        self.generator.generateEnterCall(ctx.getChild(0).getText())

    def exitCall_func(self, ctx: ExprParser.Call_funcContext):
        txt = self.generator.generateExitCall()
        self.appendText(txt)

    def exitCall_arg(self, ctx: ExprParser.Call_argsContext):
        self.generator.generateCallArg()

    def enterLine(self, ctx: ExprParser.LineContext):
        self.generator.incLine(ctx.start.line)

    def exitLine(self, ctx: ExprParser.LineContext):
        if type(ctx.getChild(0)) in [ExprParser.Call_funcContext, ExprParser.Call_printContext]:
            self.generator.popStack()

    def enterGlobal_declaration_error(self, ctx: ExprParser.Global_declaration_errorContext):
        self.generator.raiseException(f"Global variable declaration without type {ctx.getChild(1).getText()}")
    def enterError_func_def_no_type(self, ctx: ExprParser.Error_func_def_no_typeContext):
        self.generator.raiseException(f"Function {ctx.getChild(1).getText()} error missing return type")
    def enterError_func_return_arr(self, ctx: ExprParser.Error_func_return_arrContext):
        self.generator.raiseException(f"Function cannot return array type.")
    
    def enterIfblock(self, ctx: ExprParser.IfblockContext):
        txt = self.generator.generateEnterIf()
        self.appendText(txt)
    def exitIfblock(self, ctx: ExprParser.IfblockContext):
        txt = self.generator.generateExitIfBlock()
        self.appendText(txt)
    
    def enterElseblock(self, ctx: ExprParser.ElseblockContext):
        txt = self.generator.generateEnterElseBlock()
        self.appendText(txt)
    def exitElseblock(self, ctx:ExprParser.ElseblockContext):
        self.exitIfblock(ctx)


    def enterIf_no_else(self, ctx: ExprParser.If_no_elseContext):
        self.generator.enterIf(with_else=False)
    def enterIf_else(self, ctx: ExprParser.If_elseContext):
        self.generator.enterIf(with_else=True)

    def exitIf_no_else(self, ctx: ExprParser.If_no_elseContext):
        txt = self.generator.generateExitIf()
        self.appendText(txt)
    def exitIf_else(self, ctx: ExprParser.If_elseContext):
        self.exitIf_no_else(ctx)
    


    def enterWhileloop(self, ctx: ExprParser.WhileloopContext):
        txt = self.generator.generateEnterWhileLoop()
        self.appendText(txt)

    def enterWhileblock(self, ctx: ExprParser.WhileblockContext):
        txt = self.generator.generateEnterWhileBlock()
        self.appendText(txt)

    def exitWhileblock(self, ctx: ExprParser.WhileblockContext):
        txt = self.generator.generateExitWhileBlock()
        self.appendText(txt)

    def exitError_func_def(self, ctx: ExprParser.Error_func_defContext):
        self.generator.raiseException(f"Syntax errors in function definition")


    def enterSwitchbody(self, ctx: ExprParser.SwitchbodyContext):
        if self.switchdepth > 0:
            self.generator.raiseException("Cannot nest switchcases")
        self.switchdepth += 1
        if len(self.switch_body_txt) == self.switchdepth:
            self.switch_header_txt.append("")
            self.switch_body_txt.append("")
        else:
            self.switch_header_txt[self.switchdepth] = ""
            self.switch_body_txt[self.switchdepth] = ""

        self.append_to_switch_body = True
        case_count = ctx.getChildCount()
        self.generator.generateEnterSwitchbody(case_count)

    def enterCaseblock(self, ctx: ExprParser.CaseblockContext):
        txt = self.generator.generateEnterCaseblock()
        self.appendText(txt)

    def enterCase_value(self, ctx: ExprParser.Case_valueContext):
        self.generator.generateEnterCase_value()
        self.append_to_switch_header = True
        self.append_to_switch_body = False

    def exitCase_value(self, ctx: ExprParser.Case_valueContext):
        self.generator.generateExitCase_value()
        self.append_to_switch_header = False
        self.append_to_switch_body = True

    def exitCaseblock(self, ctx: ExprParser.CaseblockContext):
        txt = self.generator.generateExitCaseblock()
        self.appendText(txt)

    def enterDefaultblock(self, ctx: ExprParser.DefaultblockContext):
        txt = self.generator.generateEnterDefaultblock()
        self.appendText(txt)

    def exitDefaultblock(self, ctx: ExprParser.DefaultblockContext):
        txt = self.generator.generateExitDefaultblock()
        self.appendText(txt)

    def exitSwitchbody(self, ctx: ExprParser.SwitchbodyContext):
        txt, end_txt, current_main_reg, switch_first_reg, switch_last_reg = self.generator.generateExitSwitchbody()
        self.append_to_switch_header = True
        self.append_to_switch_body = False
        self.appendText(txt)
        self.append_to_switch_header = False

        self.fixRegs(current_main_reg, switch_first_reg, switch_last_reg)
        self.appendText(self.switch_header_txt[self.switchdepth])
        self.appendText(self.switch_body_txt[self.switchdepth])
        self.appendText(end_txt)
        self.switchdepth -= 1

    def fixRegs(self, current_main_reg, switch_first_reg, switch_last_reg):
        #print(current_main_reg, switch_first_reg, switch_last_reg)
        n_ops = current_main_reg - switch_first_reg
        obj = {}
        for i in range(n_ops):
            aim = switch_first_reg + i
            repl = switch_last_reg + i
            obj[str(aim)] = str(repl)
        if (obj == {}):
            #No fixing necessary
            return
        new_str = re.sub("|".join(obj), lambda x: obj[x.group(0)], self.switch_body_txt[self.switchdepth])
        self.switch_body_txt[self.switchdepth] = new_str

