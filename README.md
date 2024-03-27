<!-- TOC --><a name="mylang-guide"></a>
# MyLang guide
by Filip Horst
<!-- TOC start (generated with https://github.com/derlin/bitdowntoc) -->

- [Overview](#overview)
- [Compiling input to exe](#compiling-input-to-exe)
- [General syntax info](#general-syntax-info)
   * [Statement ending](#statement-ending)
   * [Comments](#comments)
   * [Available types](#available-types)
   * [Other](#other)
- [Basic variables](#basic-variables)
   * [Empty declaration](#empty-declaration)
   * [Declaration with assignments](#declaration-with-assignments)
   * [Assigning values](#assigning-values)
   * [Using variables](#using-variables)
- [Operations](#operations)
   * [Arithmetic operators](#arithmetic-operators)
   * [Comparison operators](#comparison-operators)
   * [Boolean operators](#boolean-operators)
   * [Multiple operations in one expression](#multiple-operations-in-one-expression)
   * [Expressions in paranthesis](#expressions-in-paranthesis)
- [User input and output](#user-input-and-output)
   * [Reading input ](#reading-input)
   * [Read - <span style="color:orange">known issues</span>](#read-known-issues)
   * [Printing output](#printing-output)
- [Arrays](#arrays)
   * [Declarations and assignment](#declarations-and-assignment)
   * [<span style='color:orange'>Limitations</span>](#limitations)
- [Structures](#structures)
   * [Declarations and assignments](#declarations-and-assignments)
   * [Accessing structure fields](#accessing-structure-fields)
   * [Important structure notes:](#important-structure-notes)
   * [<span style='color:orange'> Limitations </span>](#limitations-1)
- [Functions](#functions)
   * [Creating functions](#creating-functions)
   * [Returning values notes](#returning-values-notes)
   * [Calling functions](#calling-functions)
   * [<span style="color:orange"> Limitations </span>](#limitations-2)
- [If-else blocks](#if-else-blocks)
   * [Creating if and ifelse blocks](#creating-if-and-ifelse-blocks)
   * [Nested if-else blocks](#nested-if-else-blocks)
- [Switchcase blocks](#switchcase-blocks)
   * [Creating switchcase](#creating-switchcase)
   * [<span style="color:orange">Limitations</span>](#limitations-3)
- [While loops](#while-loops)
   * [Creating while loop](#creating-while-loop)
   * [Nested loops](#nested-loops)
- [Global variables](#global-variables)
   * [Results of declaring variable as global](#results-of-declaring-variable-as-global)
   * [Declaring global variables](#declaring-global-variables)
- [Full list of functionalities](#full-list-of-functionalities)
- [Full list of <span style="color:orange">limitations</span>](#full-list-of-limitations)
- [Handled errors](#handled-errors)
- [Code samples](#code-samples)
   * [Numerical integrals (basic algorithm)](#numerical-integrals-basic-algorithm)
   * [Selection sort](#selection-sort)
   * [Additional code snippets](#additional-code-snippets)
- [Resources and used programs](#resources-and-used-programs)

<!-- TOC end -->



<!-- TOC --><a name="overview"></a>
## Overview
MyLang is a very simple programming language created as part of university course related to compilers. I am not very creative so i couldn't come up with any catchy name :)

Sometimes i wasn't sure where to put a certain limitation so i included all of them as list in [Full list of <span style="color:orange">limitations</span>](#full-list-of-limitations).

To see all functionalities without reading about them visit [Full list of functionalities](#full-list-of-functionalities).

<!-- TOC --><a name="compiling-input-to-exe"></a>
## Compiling input to exe
System architecture is specified in LLVMGenerator. If user works on another system he is required to change it accordingly. One can find what target triple is necessary by using clang -S -emit-llvm tester.c and reading it from created tester.ll.

`target triple = "x86_64-w64-windows-gnu"`

To compile and run program, paste it's code into file called "input" in the same directory as other programs and run script called "compiler.bat". Result will be available as mylang.exe and will run automatically or errors will be printed in the console.

To read IR code view "mylang.ll" and "optimized.ll" files.

To clean compiler files and .ll you can use "clean.bat" script.

<!-- TOC --><a name="general-syntax-info"></a>
## General syntax info
<!-- TOC --><a name="statement-ending"></a>
### Statement ending
All statements (lines) should end with a semicolon. Exceptions to this rule are: If-else blocks, Switchcase blocks, While loops and function definitions.
<!-- TOC --><a name="comments"></a>
### Comments
To add a comment use '//'. Entire text occuring after that sign will be deleted. Multi-line comments are not supported.
```
// This is a comment!
```
<!-- TOC --><a name="available-types"></a>
### Available types
There are 3 core types:
* int - stored as i32, allowed values are: ..., -2, -1, 0, 1, 2, ...
* double - stored as double, allowed values are: -0.2, -0.1, 0, 0.1, 0.2, ..., 1, ...
* bool - stored as i1, allowed values are: true, false (printed as 1, 0)

In addition, each of these types can be stored as an array of values:
* array of int
* array of double
* array of bool

User can also define custom structures that can be used as a type:
* user structures

<!-- TOC --><a name="other"></a>
### Other
More information regarding each functionality are included in respective sections.
<!-- TOC --><a name="basic-variables"></a>
## Basic variables
Information in this section applies only to very basic variables. Arrays and structures are described in further sections.
<!-- TOC --><a name="empty-declaration"></a>
### Empty declaration
To declare a variable without assigning any value to it use the following format: [type]_[name];

A few examples:
```
int a;
double x;
bool fact;
```
<!-- TOC --><a name="declaration-with-assignments"></a>
### Declaration with assignments
Assignment during declaration is very natural. Just use =[value]; after variable's name. Remember to provide values with correct types!

A few examples:
```
int a = 5;
double x = 1.2;
bool fact = true;
```
<!-- TOC --><a name="assigning-values"></a>
### Assigning values
To assign or reassign variable's value use format: [name]=[value];. Make sure that the variable has been declared earlier in the program! Compiler will verify whether value and variable types are correct where it can.

A few examples:
```
a = 10;
x = 19.2;
fact = false;
```

<span style='color:orange'>Examples of incorrect code:</span>
```
a = 10;     //Variable a wasn't declared before ->  
            //unknown var error
double x;
x = 12;     //Wrong value type(int) -> 
            //wrong types assignment error
```

<!-- TOC --><a name="using-variables"></a>
### Using variables
Variables can be used as any other value. Compiler will verify whether variable has been initialized before attempting to load them.

A few examples:
```
int a = 5;
int b = a;  //b=5
```
<span style='color:orange'>Examples of incorrect code:</span>
```
int a;
int b = a;  // -> loading uninitialized variable error
```

<!-- TOC --><a name="operations"></a>
## Operations
<!-- TOC --><a name="arithmetic-operators"></a>
### Arithmetic operators
Arithmetic operators allowed:
* "+" - addition
* "-" - substraction
* "*" - multiplication 
* "/" - division

To perform an arithmetic operation put values with the same type on both sides of one of the allowed operators.

A few examples:
```
int r;
r = 5+2;    //r=7
r = 5-2;    //r=3
r = 5*2;    //r=10
r = 10/2;   //r=5

r = 5/2;    //automatic "cut" to int r=2
```

Notes:
* Make sure that both values are the same type. Otherwise compiler will throw an error.
* Make sure operation result is the same type as assignment. Otherwise an error will be thrown.
* If operation on ints results in a non-int value (ex. 5/2 = 2.5) value will be automatically "cut" to fit int type. In the program this will be true: 5/2 = 2
<!-- TOC --><a name="comparison-operators"></a>
### Comparison operators
Values can be compared using following operators:
* "==" - left equals right
* "!=" - left is not equal to right
* ">" - left greater than right
* ">=" - left greater or equal to right
* "<" - left less than right
* "<=" - left less or equal to right

Examples:
```
2==2;   //true
1==2;   //false

1!=2;   //true
2!=2;   //false

3>2;    //true
2>2;    //false

2>=2;   //true
2>=3;   //false

3<5;    //true
3<2;    //false

3<=3;   //true
4<=3;   //false
```
Notes:
* Both values are required to have the same type

<!-- TOC --><a name="boolean-operators"></a>
### Boolean operators
User can perform operations on boolean values using following operators:
* "~" - negation (not)
* "&" - and
* "|" - or
* "^" - xor

Examples:
```
~true;              //false

true & true;        //true
true & false;       //false

true | true;        //true
true | false;       //true

true ^ false;       //true
true ^ true;        //false
```
<!-- TOC --><a name="multiple-operations-in-one-expression"></a>
### Multiple operations in one expression
User can chain multiple operations in one expression. All operations will be evaluated according to mathematical order.

Examples:
```
2+2*2;      //6
2+15/3*2;   //12
```

Operations of different categories can be chained together as long as user makes sure they are performed on correct types. Otherwise compiler will throw an error.

Example:
```
bool a;
a = 8/2 > 2 ^ true;     //a=false
```
<!-- TOC --><a name="expressions-in-paranthesis"></a>
### Expressions in paranthesis
User can redefine evaluation order using paranthesis. Multiple pairs of paranthesis can be used in one expression.

Example:
```
int a;
a = 2+2*2;          //a=6
a = (2+2)*2;        //a=8
a = (2*(2+2))*2;    //a=16
```
<!-- TOC --><a name="user-input-and-output"></a>
## User input and output
<!-- TOC --><a name="reading-input"></a>
###  Reading input 
There are 2 built-in function that allow to read user input:
* read(var) - read int value into variable named "var"
* readd(var) - read double value into variable named "double"

If user inputs incorrect type of value it will either be converted to 0 of expected type or "cut" to int. Compiler print a warning if it detects situation like this.

Examples:
```
int a;
read(a);    //user inputs 5
            //a=5
double b;
readd(b);   //user inputs 2.5
            //b=5
```

<!-- TOC --><a name="read-known-issues"></a>
### Read - <span style="color:orange">known issues</span>
1. Read doesn't read user input correctly in following scenario. Reason for this unwanted behaviour is unknown, but user is warned that types are incorrect and can cause problems.
```
int a;
read(a);
print(a);

int b;
readd(b);
print(b);
```

<!-- TOC --><a name="printing-output"></a>
### Printing output
To print any value user can use built-in function:
* print(expr) - print expression of any core type (int, double, bool) to console. Expression can also be a simple value. Function print(expr) prints a newline character before the value.

Example:
```
print(5+2);     //prints 7 to console
print(2.5);     //prints 2.5 to console
int a = 2;
print(a);       //prints 2 to console
```
<!-- TOC --><a name="arrays"></a>
## Arrays
<!-- TOC --><a name="declarations-and-assignment"></a>
### Declarations and assignment
To declare an array user must specify it's type AND SIZE using the following format: [type]"[" [size] "]"_[name];

Example:
```
int[5] a;   //array of 5 ints
```

To assign value to array's element pick it using square brackets and treat as basic variable.

Example:
```
int[5] a;
a[0] = 1;
a[2] = 5;
```

To declare or assign entire array at once use curly brackets with value of EVERY element inside.

Example:
```
int[2] a = {4,6};
print(a[1]);    //6
a = {6,4};
print(a[1]);    //4
```

Important notes:
* Arrays are assumed to be initialized even without any assignments. 
* Arrays are modified when passed as argument to a function that modifies array's elements.
<!-- TOC --><a name="limitations"></a>
### <span style='color:orange'>Limitations</span>
* User cannot assign one array to another:
```
int[2] a = {1,2};
int[2] b = a;   //IMPOSSIBLE! compiler handles error
```
* User cannot return an array from function
* User cannot create nested arrays (arrays of arrays)
* Cannot print entire array at once

<!-- TOC --><a name="structures"></a>
## Structures
<!-- TOC --><a name="declarations-and-assignments"></a>
### Declarations and assignments
User can define his own types using structures. To declare a structure user must use keyword "struct" followed by structure name (picked by user). After opening curly brackets user has to provide list of fields. One field is a pair of type and name. Each field should be ended with a semicolon ";". After closing curly brackets struct declaration must end with a semicolon ";".

Example of a declaration:
```
struct myType {
    int a;
    double b;
};
```
To declare a variable using newly created type user must provide keyword "struct" followed by structure unique name instead of a type.

Example of variable declaration using struct type:
```
//Assume we have structure myType declared -> previous example

struct myType a;
```
Notes:
* User cannot assign default values
* User cannot assign values for entire structure when declaring a variable of struct's type
<!-- TOC --><a name="accessing-structure-fields"></a>
### Accessing structure fields
After declaring variable with structure type user can access it's fields using [structure name].[field name] format.

Example:
```
struct myType {
    int a;
};

struct myType a;
a.a = 5;
print(a.a);     //5
```
<!-- TOC --><a name="important-structure-notes"></a>
### Important structure notes:
* Structures are not modified when they are modified inside a function to which they were passed as argument. To allow modifications inside functions declare them as global variables.
<!-- TOC --><a name="limitations-1"></a>
### <span style='color:orange'> Limitations </span>
* User cannot create nested structures
* User cannot return structure from a function
* Structures are always assumed to be initialized (return 0 by default)
* User cannot use arrays or other struct type variables inside struct
* Cannot assign multiple values at once
* Cannot print entire structure at once
<!-- TOC --><a name="functions"></a>
## Functions
<!-- TOC --><a name="creating-functions"></a>
### Creating functions
To create a function user must write keyword "function" followed by returned value type and name. Next, in paranthesis user must specify list of input arguments. Each input argument consists of type and name. After closing paranthesis function code is required to be written between curly brackets. No semicolon is needed after function definition.

Example:
```
function int add_ints(int a, int b){
    int c = a + b;
    return c;
}
```

To specify array as an input argument user does not have to provide it's size:

```
function int add_ints_array(int[] a){
    return a[0] + a[1];
}
```

To specify structure as an input argument user has to provide structure type in the same way as in variable declaration:
```
function int add_ints_struct(struct myType a){
    return a.a + a.b;
}
```
<!-- TOC --><a name="returning-values-notes"></a>
### Returning values notes
* As stated before, functions cannot return arrays nor structures. What they can do is return one element of an array or structure assuming it's type is the same as return type stated in declaration.
* If user does not provide a return statement, it is automatically added and returns 0 of type stated in declaration.
<!-- TOC --><a name="calling-functions"></a>
### Calling functions
To call a function write it's name and provide parameter values in paranthesis directly after the name. If call is an entire line remember to end with semicolon ";". 

Examples:
```
//Example is calling functions from 
//Creating functions subsection

int a;
a = add_ints(1,2);
print(a);                   //3

int[2] b = {1,2};
a = add_ints_array(b);
print(a);                   //3

//Assume struct myType is declared with fields a,b of type int
struct myType c;            

c.a = 1;
c.b = 2;
a = add_ints_struct(c);
print(a);                   //3
```

Function calls can be used as any other value:
```
function int f1(){
    return 2;
}
int a = f1() + f1(); 
print(a);               //prints 4
```

<!-- TOC --><a name="limitations-2"></a>
### <span style="color:orange"> Limitations </span>
* Function cannot call itself
* Function cannot return structs nor arrays
* Cannot declare functions that use global variables before declaring said global variables
* Cannot call function before it's code
* Cannot define functions inside functions

<!-- TOC --><a name="if-else-blocks"></a>
## If-else blocks
<!-- TOC --><a name="creating-if-and-ifelse-blocks"></a>
### Creating if and ifelse blocks
User can create if-else blocks using classic syntax. Keyword "if" is followed by expression that can be evaluated to boolean value. Next, a block of code if written between curly brackets that will execute only if the condition turns out to be true. Next, user can input any code (then it is if-block) or add keyword "else" and create another block of code that will execute only if the condition is false (then it's if-else block).

Example:
```
int a = 2;
if a==2 {
    print(1);   //prints 1 because a==2 is true
} 

if a>2 {
    print(2);
} else {
    print(-1);  //prints -1 because a>2 is false
}
```
<!-- TOC --><a name="nested-if-else-blocks"></a>
### Nested if-else blocks
User can nest as many if-else blocks and/or if-blocks as he wants.

Example:
```
int a = 2;
int b = 3;

if a>1{
    if b>0 {
        if b>1{
            if b>3{
                print(1);
            } else {
                print(-1);  //prints -1, because all conditions
                            // except b>3 are true
            }
        }
    }
}
```

<!-- TOC --><a name="switchcase-blocks"></a>
## Switchcase blocks
<!-- TOC --><a name="creating-switchcase"></a>
### Creating switchcase
User can create switchcase blocks using following syntax. Keyword "switch" is followed by expression and curly brackets. Inside curly brackets user can provide as many cases as he wants by writing keyword "case" followed by value of the same type as switch expression. Each case must contain block of code (or empty block) inside another curly brackets. Every switch can contain even zero cases, but defautl is obligatory. Default is created by writing keyword "default" (same as in case) but without any value. Code in default will execute only if none of previously stated cases will be equal to switch value.

Example:
```
int a = 2;
int b = 2;
switch a {
    case 1 {
        print(1);
    }
    case b {
        print(2);       //prints 2, because a==b
    }
    default {
        print(-1);
    }
}
```
<!-- TOC --><a name="limitations-3"></a>
### <span style="color:orange">Limitations</span>
* User cannot create nested switchcases

<!-- TOC --><a name="while-loops"></a>
## While loops
<!-- TOC --><a name="creating-while-loop"></a>
### Creating while loop
To create a loop user must write "while" keyword followed by a condition (that can be evaluated to a boolean value) and a code of block that will be executed every time the condition is true.

Example:
```
int i = 5;
while (i>=0){
    print(i);
    i = i - 1;
}   //Results in 5,4,3,2,1,0
```
<!-- TOC --><a name="nested-loops"></a>
### Nested loops
User can nest multiple while loops.

Example:
```
int i = 2;
int j;
while (i>0){
    j = 2;
    while (j>0){
        print(j);
        j = j - 1;
    }
    i = i - 1;
} //Results in 2,1,2,1
```

<!-- TOC --><a name="global-variables"></a>
## Global variables
<!-- TOC --><a name="results-of-declaring-variable-as-global"></a>
### Results of declaring variable as global
When a variable is declared as global it becomes known inside every function. What it means is that it can be modified or read inside functions without being passed as a parameter. 
<!-- TOC --><a name="declaring-global-variables"></a>
### Declaring global variables
To declare a global variable use keyword "global" before it's standard declaration.

Full demo of global variables:
```
global int a = 1;
int b = 2;
int c = 3;

function int f1(int b){
    a = b;      //a is known from global context
                //b is function parameter
}

print(a);   //prints 1
f1(c);      //passed value c=3 as parameter
print(a);   //prints 3
```

<!-- TOC --><a name="full-list-of-functionalities"></a>
## Full list of functionalities
* declaring variables with or without assignment
* assigning values to variables
* printing variables
* basic arithmetic operations +,-,*,/
* 3 core types: int, double, bool
* handling negative numbers
* comparison operators >, <, <=, >=, ==, !=
* boolean operators &, |, ^, ~ (and, or, xor, not)
* functions with or without arguments
* calls within calls, using calls as values
* global variables
* if blocks, if-else blocks
* while loops, nested while loops
* arrays, read and modify each element, assign entire array as once
* structures
* reading user input, read int or double
* switchcase

<!-- TOC --><a name="full-list-of-limitations"></a>
## Full list of <span style="color:orange">limitations</span>
* No auto conversions from numbers (2, 2.0 etc.) to double/int. When initializing variables user must ensure that they provide correct type.
* Cannot call function before it's code
* Function cannot call itself
* Functions cannot return structs
* Functions cannot return arrays
* Cannot declare functions that use global variables before declaring said global variables
* Cannot assign multiple values at once to structures
* Cannot use nested switchcases
* Syntax errors sometimes not described well enough (example: declaring struct with assignment similar to array)
* Cannot define functions inside functions
* Cannot print entire array nor struct at once, only one element

<!-- TOC --><a name="handled-errors"></a>
## Handled errors
Except syntax error information provided by ANTLR tool, tree walker module also returns both syntax and semantic errors information. Full list of handled semantic errors:

* unknown variable type
* variable already declared as var or function
* variable already declared as global var
* variable name already used as function name
* cannot declare global variable inside a function
* unknown type in struct declaration
* unknown struct type
* unknown assignment error (fallback)
* cannot assign to unknown variable
* cannot assign to entire array, use brackets to initialize the array
* cannot assign type to type (in arrays)
* tuple assignment can only be used on array
* not enought elements to assign to array
* too many values in array assignment
* cannot assign type to type (inside entire array assignment)
* unknown field name
* wrong type in struct field assignment
* trying to load uninitialized variable
* array index must be int
* cannot print entire array, choose one element
* cannot print entire struct
* cannot read bool values, use temporary int var (in read())
* warnings: using incorrect type read to read var
* cannot perform operation on different types (arithmetic op)
* unknown type or operation on type not allowed
* unknown operation for type
* unknown comparison operator for type
* unknown boolean operator
* cannot negate non-bool values
* cannot create nested functions
* function cannot return structures
* unknown return type for funtion
* cannot return entire array
* function must return type specified in declaration
* calling function without or before it's definition
* too many arguments passed to call
* wrong argument type
* not enough arguments passed to function
* if condision has to return boolean value
* while loop condition has to resolve to bool value
* cannot compare case value type to switch value type

Additionally handled syntax errors:
* cannot use structures as struct fields
* cannot use arrays as struct fields
* no array size specified
* read function requires 1 argument
* too many arguments passed to read
* unknown operation (regarding arithmetic, boolean, compare)
* global var declaration without type
* function missing return type
* function cannot return array type
* syntax errors in function definition
* cannot nest switchcases

All errors handled by Python programs include line number in which error occured. Comments do not change displayed line value.
Example error:

`Exception: Trying to load uninitialized variable a : line 9`
<!-- TOC --><a name="code-samples"></a>
## Code samples

<!-- TOC --><a name="numerical-integrals-basic-algorithm"></a>
### Numerical integrals (basic algorithm)
Also available in Test12
```
function double f(double x) {
    return 2.0*x*x - 2.0*x + 2.0;
}

double step = 0.0001;
double lower = -5.0;
double upper = 5.0;


if (upper < lower){
    print(-1);
}

double sum = 0.0;
double x = lower;
while (x <= upper){
    sum = sum + f(x);
    x = x + step;
}
sum = step * sum;
print(sum);
```
With default settings return 186.667...

<!-- TOC --><a name="selection-sort"></a>
### Selection sort
Also available in Test17

```
int[12] t = {3,6,5,4,1,2,8,9,0,-1, 25,-12};

function int min_element(int[] t, int len){
    int min = t[0];
    int i = 0;
    while i<len{
        if (t[i] < min){
            min = t[i];
        }
        i = i + 1;
    }
    return min;
}

int r = min_element(t, 12);

function int selection_sort(int[] t, int len){
    int i = 0;
    while i<len {
        int min_idx = i;
        int j = i + 1;
        while (j<len){
            if (t[min_idx] > t[j]){
                min_idx = j;
            }
            j = j + 1;
        }
        int tmp = t[min_idx];
        t[min_idx] = t[i];
        t[i] = tmp;
        i = i + 1;
    }

    i = 0;
    while i<len{
        print(t[i]);
        i = i + 1;
    }
    return 0;
}

int len = 12;
selection_sort(t, len);
```
Prints array from first line in ascending order.

<!-- TOC --><a name="additional-code-snippets"></a>
### Additional code snippets
Check out /src/Tests folder on github to see more.

<!-- TOC --><a name="resources-and-used-programs"></a>
## Resources and used programs
* Python language to code tree walker and IR generator
* ANTLR4 to create parsers/lexers based on g4 grammar
* clang from [winlibs]("https://winlibs.com") to compile IR
* C language with clang to find out how IR code is generated
* opt from [winlibs]("https://winlibs.com") to optimize IR code
* [Mapping high level constructs to llvm ir](https://mapping-high-level-constructs-to-llvm-ir.readthedocs.io/en/latest/a-quick-primer/index.html") additional info
* MyLang repository [GitHub](https://github.com/isso1550/MyLang_L24)
* Markdown TOC generator [Markdown TOC generator](https://derlin.github.io/bitdowntoc/)
* Resources from the course: Języki formalne i kompilatory L24, Politechnika Warszawska