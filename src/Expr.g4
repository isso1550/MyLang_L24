grammar Expr;

program : 
    lines
    ;

lines: 
    line ';' lines?
    ;

line: 
    declaration
    | assignment
    | print
    ;

declaration:
    type ID ('=' expression)?
    ;
    
assignment:
    ID '=' expression
    ;

print:
    'print' LPAREN expression RPAREN
    ;

value:
    '~' value #value_negation
    | INT     #value_int
    | ID    #value_id
    | bool  #value_bool
    ;
    
expression:
    value
    | expr0
    ;
    
expr0 :
    expr0 ('==' | '>' | '<' | '>=' | '<=' | '!=') expr1
    | expr0 '+' expr1
    | expr0 ('|'| '&'| '^') expr1
    | value
    | '~' expr0
    | expr1
    ;
    
expr1 :
    expr1 '*' expr1
    | LPAREN expr0 RPAREN
    | value
    ;
    
type:
    'int'
    | 'bool'
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

INT : [-]?[0-9]+ ;
ID: [a-zA-Z_][a-zA-Z_0-9]* ;
WS: [ \t\n\r\f]+ -> skip ;