import sys
from antlr4 import *
from ExprLexer import ExprLexer
from ExprParser import ExprParser
from ListenerInterp import ListenerInterp

def main(argv):
    input = FileStream(argv[1])
    lexer = ExprLexer(input)
    stream = CommonTokenStream(lexer)
    parser = ExprParser(stream)
    tree = parser.program()
    #print(tree.toStringTree(recog=parser))
    if parser.getNumberOfSyntaxErrors() > 0:
        print("syntax errors")
    else:
        print("___________________________SUCCESFULLY GENERATED IR")
        linterp = ListenerInterp()
        walker = ParseTreeWalker()
        walker.walk(linterp, tree)
if __name__ == '__main__':
    main(sys.argv)