# Current Version: 0.4

# V-List
* 0.1 Declaration, assignment, print, expression evaluation (+,*,())
* 0.2 Negative numbers (INT grammar), comparisons (>,<,<=,>=,==,!=), boolean type, bool operators(&,|,^,~), more tests, expression evaluation fixes (now same level expressions evaluated in order "as written"), basic type checking before operations, bool printing, universal "prepare evaluation" function, value negation when init
* 0.3 Functions!, args/no args, call within calls, no nested funcs allowed, calls as values, calls as args to calls, global variables, better exceptions, line counting for exceptions, expression level fixes in g4, tests
* 0.4 If blocks, If_else blocks, While loops, double number type, handling number types, handling negative ints/doubles, nested loops, nested if_else blocks

# TODO
* tables / short circuit boolean
* struct
* read user input

# General info
* nested functions not allowed
* expression eval order has to be checked with even more tests!
* expression levels
    * 0 - comparison, bool operations
    * 1 - basic arithmetic, negation
    * 2 - (), "advanced" arithmetic *, /
* allowed function and variable to share name
* user has to provide correct number type during assignment (2.0 to double 2 to int)!

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
* Test7
    * Testing functions, advanced calls
    * Results: all 1
* Test8
    * Basic global vars test
    * Results: 1, 1, 27, 1 (can only look at ones)
* Test9 
    * Advanced expression to test expression levels in grammar (expr0 expr1 expr2)
    * Results: 1 (important to look at AST tree!)
* Test10
    * Basic if, if/else, while loops
    * Results: 1, then countdown from 10 to 0 included
* Test11
    * Correctly reading minuses for substraction and negative value
    * Results: all 1
* Test12
    * Easiest numeric integrals
    * Results: test yourself! (default ~186.667)
* Test13
    * Everything implement so far, testing multiple types, calculations, bool operators, functions, global vars, loops, nested ifs
    * Results: 2, 2, 2, 2, 2.0, 2.0, 2.0, 2.0, rest all 1