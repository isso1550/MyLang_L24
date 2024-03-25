grammar Expr;

program : 
    lines?
    ;

lines: 
    line lines?
    ;

line: 
    declaration ';'
    | ifline
    | whileloop
    | function_definition
    | assignment ';'
    | print ';'
    | expression ';'
    | return ';'
    | call ';'
    
    ;

whileloop:
    'while' expression '{' whileblock '}'
    ;
whileblock: block;    

ifline:
    'if' expression '{' ifblock '}' #if_no_else
    | 'if' expression '{' ifblock '}' 'else' 
    '{' elseblock '}' #if_else
    ;
ifblock: block;
elseblock: block;

global:
    'global'
    ;
    
call:
    ID LPAREN call_args? RPAREN
    ;
    
call_args:
    call_arg ',' call_args
    | call_arg
    ;

call_arg:
    expression
    ;
    
return:
    'return' expression
    ;
    
function_definition:
    'function' type ID
    LPAREN func_args
    RPAREN '{' block? '}' #func_def_with_args
    | 'function' type ID LPAREN 
    RPAREN '{' block? '}' #func_def_no_args
    
    | 'function' ID LPAREN func_args? RPAREN
    '{' block? '}' #error_func_def_no_type

    |'function' type ID? LPAREN? 
    func_args? RPAREN? '{'? 'block'?
    '}'? #error_func_def
    
    | 'function' type '[]' ID? 
    LPAREN? 
    func_args? RPAREN? '{'? 'block'?
    '}'? #error_func_return_arr
    ;

func_args:
    func_arg ',' func_args1
    | func_arg
    ;
    
func_args1:
    func_arg ',' func_args1
    | func_arg
    ;
    
func_arg:
    type ID
    | type '[]' ID
    ;
    
block:
    lines
    ;

declaration:
    global? (type | array_type)
    ID #declaration_no_assign
    
    | global? (type | array_type)
    ID '=' expression #declaration_assign 
    
    | global? array_type ID '=' array_assign #declaration_assign_array
    
    | global ID ('=' expression)? #global_declaration_error
    ;
    
assignment:
    ID '=' array_assign #array_assignment
    | (ID | array_elem) '=' 
    expression #classic_assignment
    ;

print:
    'print' LPAREN expression RPAREN
    ;

value:
    '~' value #value_negation
    | '-' (INT | DOUBLE) #value_negative
    | '-' bool #error
    | INT     #value_int
    | ID    #value_id
    | bool  #value_bool
    | DOUBLE #value_double
    | array_elem #value_array_elem
    ;
    
array_assign:
    '{' value (',' value)* '}'
    ;
    
expression:
    expr0
    ;
    
expr0:
    expr0 ('==' | '>' | '<' | '>=' |
    '<=' | '!=') expr0
    | expr0 ('|'| '&'| '^') expr0
    | value
    | call
    | expr1
    | expr2
    ;
    
expr1 :
    expr1 ('+' | '-') expr1
    | value
    | call
    | '~' expr1
    | expr2
    ;
    
expr2 :
    expr2 ('*' | '/') expr2
    | LPAREN expr0 RPAREN
    | value
    | call
    ;
    
type:
    'int'
    | 'bool'
    | 'double'
    ;

array_type:
    type '[' INT ']' #arr_type
    | type '[]' #error_no_arr_size
    ;

array_elem:
    ID '[' expression ']'
    ;
    
bool:
    'true'
    | 'false'
    ;
    
AND : 'and' ;
OR : 'or' ;
NOT : 'not' ;
EQ : '=' ;
COMMA : ',' ;
SEMI : ';' ;
LPAREN : '(' ;
RPAREN : ')' ;
LCURLY : '{' ;
RCURLY : '}' ;

INT : [0-9]+ ;
DOUBLE : [0-9]+[.][0-9]+;
ID: [a-zA-Z_][a-zA-Z_0-9]* ;
WS: [ \t\n\r\f]+ -> skip ;