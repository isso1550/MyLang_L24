@echo off
for /f "delims=" %%a in ('llvm-config --host-target') do set target=%%a
python preprocessor.py %1
antlr4 -v 4.13.0 -listener -Dlanguage=Python3 Expr.g4
python Driver.py .\preprocess-out %target%
if ERRORLEVEL 1 echo Stopping compilator script & exit(1)
opt -S -o optimized.ll mylang.ll
clang optimized.ll -o mylang.exe
mylang.exe