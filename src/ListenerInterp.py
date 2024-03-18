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
        self.result = {}

        self.exprStack = deque() 

    def exitProgram(self, ctx: ExprParser.ProgramContext):
        self.txt = self.generator.generateHeader() + self.txt + self.generator.generateFooter()
        print('_____PROGRAM_____')
        print(self.txt)

        with open("myllvm.ll",'w') as f:
            f.write(self.txt)
            f.close()
        

    def exitDeclaration(self, ctx: ExprParser.DeclarationContext):
        dtype = ctx.getChild(0).getText()
        vname = ctx.getChild(1).getText()
        val = None
        if (ctx.getChildCount() > 2):
            #Declaration with assignment
            val = ctx.getChild(3).getText()
        print(f"Declared variable {vname} of type {dtype} with value {val}")
        self.txt += self.generator.generateDeclaration(dtype, vname, val)
    
    def exitAssignment(self, ctx: ExprParser.AssignmentContext):
        vname = ctx.getChild(0).getText()
        val = ctx.getChild(2).getText()
        print(f"Assigning value {val} to variable {vname}")
        self.txt += self.generator.generateAssignment(vname)

    def exitPrint(self, ctx: ExprParser.PrintContext):
        child = ctx.getChild(2)
        val = child.getText()

        txt = self.generator.generatePrint()
        self.txt += txt
        print(f"Printing {val}")
    

    def exitValue_id(self, ctx: ExprParser.Value_idContext):
        vname = ctx.getText()
        txt = self.generator.generateLoadVar(vname)
        print(f"Loading value for value_id {vname}")
        self.txt += txt

    def exitValue_int(self, ctx: ExprParser.Value_intContext):
        val = ctx.getText()
        dtype = 'i32'
        self.generator.pushValToStack(val, dtype)

    def exitExpression(self, ctx: ExprParser.ExpressionContext):
        if (ctx.getChildCount() > 1):
            if (ctx.getChild(0).getText() == '('):
                #If parathesis - just skip, the expression will auto-evaluate later
                return
            #Calculations required
            op = ctx.getChild(1).getText()
            match op:
                case '+':
                    print(f"Found addition operation {op}")
                    txt = self.generator.generateAddition()
                    self.txt += txt
                case '*':
                    print(f"Found multiply operation {op}")
                    txt = self.generator.generateMultiply()
                    self.txt += txt
                case _:
                    raise Exception("Unknown operation")
        else:

            pass

    def exitExpr0(self, ctx: ExprParser.Expr0Context):
        return self.exitExpression(ctx)
    
    def exitExpr1(self, ctx: ExprParser.Expr1Context):
        return self.exitExpression(ctx)