antlr4 -v 4.13.0 -listener -Dlanguage=Python3 Expr.g4
python Driver.py .\input
clang myllvm.ll -o myllvm.exe
myllvm.exe