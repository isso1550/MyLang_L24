# Current Version: 0.8

# V-List
* 0.1 Declaration, assignment, print, expression evaluation (+,*,())
* 0.2 Negative numbers (INT grammar), comparisons (>,<,<=,>=,==,!=), boolean type, bool operators(&,|,^,~), more tests, expression evaluation fixes (now same level expressions evaluated in order "as written"), basic type checking before operations, bool printing, universal "prepare evaluation" function, value negation when init
* 0.3 Functions!, args/no args, call within calls, no nested funcs allowed, calls as values, calls as args to calls, global variables, better exceptions, line counting for exceptions, expression level fixes in g4, tests
* 0.4 If blocks, If_else blocks, While loops, double number type, handling number types, handling negative ints/doubles, nested loops, nested if_else blocks
    * 0.4.1
        program: lines? => allows handling whitespace only input (instead of throwing random errors)
    * 0.4.2
        better function and variable declaration exceptions associated with their names, allow functions without commands in block, handling function def syntax errors, cannot create variables and functions with same names, control number of arguments passed to function
* 0.5 Arrays, can't declare arrays in functions, arrays get modified in function when passed as args, getting array values, arrays as args to functions, can't return arrays from functions, return array elements, assign entire array, some syntax error exceptions, removing useless comments, split assigments to classic and array, function definition and declaration grammar exceptions syntax errors, next somewhat serious program! (selection sort + pick_min), test 15-17, test 12 fixed types
* 0.6 Structures, declare struct, assign to struct, assign to struct fields, fields type check, pass struct as argument, global structures, use struct values in expressions, test18 test19
* 0.7 read user input, read int, read double, warnings when incorrect type, exception when reading bool, disable entire array assigments, can't print struct, call g4 changes, func return value push to stack prevention, sendWarning func, test20
* 0.8 switchcase, collect body and header -> combine intro final text, no nested switchcase, basic switch errors, fix register order, declare arrays in functions, fixed return val push to stack preventions (didn't work with nested calls print(f4(a)==0)) -> now uses pop when call is one line on exit

# TODO
* tables (done?)
* (optional) short circuit boolean
* struct (done?)
* read user input (done)
* switch case (done?)
* verify errors!
* clean up useless code after disabling struct as possible return

# General info
* nested functions not allowed
* expression eval order has to be checked with even more tests!
* expression levels
    * 0 - comparison, bool operations
    * 1 - basic arithmetic, negation
    * 2 - (), "advanced" arithmetic *, /
* user has to provide correct number type during assignment (2.0 to double 2 to int)!
* cannot call function before its definition
* cannot declare arrays in functions that call other functions, to make things easier you can't declare arrays inside functions. The requirement to use memcpy makes making it possible really difficult.
* functions cannot return structures, to modify them use globals
* cannot declare function using global vars before declaring used global vars
* cannot use nested switchcases

# Limitations
* no auto conversions from numbers to double/int, when initializing variable you must ensure they digit is in correct type:
    * double a = 2; WRONG!
    * double a = 2.0; correct!
* cannot declare functions nor arrays inside functions -> fixed
    * declaring arrays inside functions only breaks the program if that function contains calls to another functions (not well tested, might be other causes too), but locking declaration possibility entirely makes everything simplier for both program and user who doesn't have to consider whether he can or can't do it
* cannot call function before its definition
* functions cannot return structs, to modify struct use global variables
* cannot declare functions using global variables before declaring these global variables
* only "syntax error" when user attempts to declare struct with assignment
* can't assign multiple values at once to structure
* cannot use nested switchcases
* not 100% sure switchcase reg fix works
* functions cannot return arrays

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
* Test14
    * Same name local variable used in multiple functions, use of global vars in functions, use of other functions in functions
    * Results: all 1
* Test15
    * Basic arrays tests
    * Results: 2.5, 16, 25, 3, 12, 10, 8, 6, 4, 2, 1.5, Rest all 1
* Test16
    * Basic arrays tests
    * Results: all 1
* Test17
    * Pick min, selection_sort
    * Results: 1, then sorted ascending 1-6
* Test18
    * Basic structs
    * Results: all 1
* Test19
    * More advanced structure operations
    * Results: almost all 1, second to last should be -1
* Test20
    * Test reading user input
    * Results based on input: input 2xint , 2xdouble -> print sum of ints, sum of doubles -> input 1xint 1xdouble -> print int value, double value
* Test21
    * Basic switchcases
    * Results: all 1
* Test22
    * Verify fixed array declarations in functions
    * Results: all 1 (4 prints)