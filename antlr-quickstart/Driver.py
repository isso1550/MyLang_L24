import sys
from antlr4 import *
from ExprLexer import ExprLexer
from ExprParser import ExprParser

def main(argv):
    input = FileStream(argv[1])
    lexer = ExprLexer(input)
    stream = CommonTokenStream(lexer)
    parser = ExprParser(stream)
    tree = parser.program()
    print(tree.toStringTree(recog=parser))

if __name__ == '__main__':
    main(sys.argv)