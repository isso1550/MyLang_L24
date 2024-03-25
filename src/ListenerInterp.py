import sys
from antlr4 import *
from ExprParser import ExprParser
from ExprListener import ExprListener
from LLVMGenerator import LLVMGenerator

from collections import deque

class ListenerInterp(ExprListener):
    def __init__(self):
        self.generator = LLVMGenerator()
        self.txt = ""
        self.pre_main_txt = ""
        self.func_depth = 0
        self.result = {}

        self.exprStack = deque() 

    def appendText(self, txt, append_to_premain=False):
        if (self.func_depth > 0) | (append_to_premain):
            self.pre_main_txt += txt
        else:
            self.txt += txt

    def exitProgram(self, ctx: ExprParser.ProgramContext):
        header, main_start = self.generator.generateHeader()
        self.txt = header + self.pre_main_txt + main_start + self.txt + self.generator.generateFooter()
        with open("myllvm.ll",'w') as f:
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

    def enterError_no_arr_size(self, ctx: ExprParser.Error_no_arr_sizeContext):
        self.generator.raiseException("No array size specified")
    
    def exitArray_assignment(self, ctx: ExprParser.Array_assignmentContext):
        vname = ctx.getChild(0).getText()
        len = (ctx.getChild(2).getChildCount() - 2 + 1)/2 
        txt = self.generator.generateArrayAssignment(vname, int(len))
        self.appendText(txt)

    def exitPrint(self, ctx: ExprParser.PrintContext):
        txt = self.generator.generatePrint()
        self.appendText(txt)
    

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
                    raise Exception(f"Unknown operation {op}")
            self.appendText(txt)
        elif (ctx.getChildCount() > 1):
            if (ctx.getChild(0).getText() != '~'):
                raise Exception(f"Unknown situation {ctx.getText()}")
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
        rettype = ctx.getChild(1).getText()
        fname = ctx.getChild(2).getText()
        txt = self.generator.generateEnterFunctionDefinition(rettype, fname)
        self.appendText(txt)

    def enterFunc_def_with_args(self, ctx: ExprParser.Func_def_with_argsContext):
        return self.enterFunction_definition(ctx)
    def enterFunc_def_no_args(self, ctx: ExprParser.Func_def_no_argsContext):
        self.func_depth += 1
        rettype = ctx.getChild(1).getText()
        fname = ctx.getChild(2).getText()
        txt = self.generator.generateEnterFunctionDefinitionNoArgs(rettype, fname)
        self.appendText(txt)

    def exitFunc_arg(self, ctx: ExprParser.Func_argContext):
        dtype = ctx.getChild(0).getText()
        if (ctx.getChild(1).getText() == "[]"):
            arr = True
            vname = ctx.getChild(2).getText()
            dtype = dtype + "[]"
        else:
            arr = False
            vname = ctx.getChild(1).getText()
        self.generator.generateFunctionArgument(dtype, vname, array=arr)

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

    def enterCall(self, ctx: ExprParser.CallContext):
        self.generator.generateEnterCall(ctx.getChild(0).getText())

    def exitCall(self, ctx: ExprParser.CallContext):
        txt = self.generator.generateExitCall()
        self.appendText(txt)

    def exitCall_arg(self, ctx: ExprParser.Call_argsContext):
        self.generator.generateCallArg()

    def enterLine(self, ctx: ExprParser.LineContext):
        self.generator.incLine(ctx.start.line)

    def enterGlobal_declaration_error(self, ctx: ExprParser.Global_declaration_errorContext):
        self.generator.raiseException(f"Global variable declaration without type {ctx.getChild(1).getText()}")
    def enterError_func_def_no_type(self, ctx: ExprParser.Error_func_def_no_typeContext):
        self.generator.raiseException(f"Function {ctx.getChild(1).getText()} error missing return type")
    def enterError_func_return_arr(self, ctx: ExprParser.Error_func_return_arrContext):
        self.generator.raiseException(f"Function cannot return array type. Use global variables to modify.")
    
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
