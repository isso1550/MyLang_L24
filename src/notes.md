# Current Version: 0.2

# V-List
* 0.1 Declaration, assignment, print, expression evaluation (+,*,())
* 0.2 Negative numbers (INT grammar), comparisons (>,<,<=,>=,==,!=), boolean type, bool operators(&,|,^,~), more tests, expression evaluation fixes (now same level expressions evaluated in order "as written"), basic type checking before operations, bool printing, universal "prepare evaluation" function, value negation when init

# Testers
* Test1
    * Basic assignments, declarations
    * Expression evaluation 
    * Results should be: 60, 27, 25, 180 (all printed with newlines)
* Test2
    * declaration and assigments test
    * value in paranthesis
    * Results should be: 5, 6, 21, 1, 60
* Test3
    * Basic tables for AND, OR, XOR
    * Results: 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0
* Test4
    * More advanced AND, OR, XOR, NEGATION, includes comparisons
    * Results: all 1
* Test5
    * Basic comparisons
    * Results: 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0
* Test6
    * Negation in declaration and assignment, negative ints
    * Results: 0, 1, 1