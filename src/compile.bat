python preprocessor.py
antlr4 -v 4.13.0 -listener -Dlanguage=Python3 Expr.g4
python Driver.py .\preprocess-out
opt -S -o optimized.ll mylang.ll
clang optimized.ll -o mylang.exe
mylang.exe