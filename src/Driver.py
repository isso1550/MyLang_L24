import sys
from antlr4 import *
from ExprLexer import ExprLexer
from ExprParser import ExprParser
from ListenerInterp import ListenerInterp

def main(argv):
    input = FileStream(argv[1])
    target = argv[2]
    lexer = ExprLexer(input)
    stream = CommonTokenStream(lexer)
    parser = ExprParser(stream)
    tree = parser.program()
    #print(tree.toStringTree(recog=parser))
    if parser.getNumberOfSyntaxErrors() > 0:
        print("syntax errors")
    else:
        linterp = ListenerInterp()
        linterp.setTarget(target)
        walker = ParseTreeWalker()
        walker.walk(linterp, tree)
        print("Generated IR")
if __name__ == '__main__':
    main(sys.argv)