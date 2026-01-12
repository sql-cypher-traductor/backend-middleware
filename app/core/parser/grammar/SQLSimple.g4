grammar SQLSimple;

// ============================================================================
// PARSER RULES
// ============================================================================

// Regla principal: una consulta SQL
query
    : selectStatement EOF
    ;

// SELECT statement básico
selectStatement
    : SELECT selectList FROM tableName whereClause?
    ;

// Lista de columnas en SELECT
selectList
    : ASTERISK                          # SelectAll
    | columnName (COMMA columnName)*    # SelectColumns
    ;

// Cláusula WHERE opcional
whereClause
    : WHERE condition
    ;

// Condiciones en WHERE
condition
    : condition AND condition           # AndCondition
    | condition OR condition            # OrCondition
    | columnName comparisonOp value     # ComparisonCondition
    | LPAREN condition RPAREN           # ParenCondition
    ;

// Operadores de comparación
comparisonOp
    : EQ        # Equal
    | NEQ       # NotEqual
    | LT        # LessThan
    | GT        # GreaterThan
    | LTE       # LessThanOrEqual
    | GTE       # GreaterThanOrEqual
    ;

// Nombres de tablas y columnas
tableName
    : IDENTIFIER
    ;

columnName
    : IDENTIFIER
    ;

// Valores literales
value
    : STRING_LITERAL    # StringValue
    | NUMBER            # NumberValue
    | TRUE              # BooleanTrue
    | FALSE             # BooleanFalse
    | NULL              # NullValue
    ;

// ============================================================================
// LEXER RULES (Tokens)
// ============================================================================

// Palabras clave SQL (case-insensitive)
SELECT      : S E L E C T ;
FROM        : F R O M ;
WHERE       : W H E R E ;
AND         : A N D ;
OR          : O R ;
TRUE        : T R U E ;
FALSE       : F A L S E ;
NULL        : N U L L ;

// Operadores de comparación
EQ          : '=' ;
NEQ         : '!=' | '<>' ;
LT          : '<' ;
GT          : '>' ;
LTE         : '<=' ;
GTE         : '>=' ;

// Símbolos
ASTERISK    : '*' ;
COMMA       : ',' ;
LPAREN      : '(' ;
RPAREN      : ')' ;

// Identificadores (nombres de tablas y columnas)
IDENTIFIER
    : [a-zA-Z_][a-zA-Z0-9_]*
    ;

// Literales de cadena
STRING_LITERAL
    : '\'' ( ~'\'' | '\'\'' )* '\''
    ;

// Números (enteros y decimales)
NUMBER
    : [0-9]+ ('.' [0-9]+)?
    ;

// Espacios en blanco (ignorar)
WS
    : [ \t\r\n]+ -> skip
    ;

// Comentarios de línea (ignorar)
LINE_COMMENT
    : '--' ~[\r\n]* -> skip
    ;

// Comentarios de bloque (ignorar)
BLOCK_COMMENT
    : '/*' .*? '*/' -> skip
    ;

// ============================================================================
// Case-insensitive character fragments
// ============================================================================

fragment A : [aA] ;
fragment B : [bB] ;
fragment C : [cC] ;
fragment D : [dD] ;
fragment E : [eE] ;
fragment F : [fF] ;
fragment G : [gG] ;
fragment H : [hH] ;
fragment I : [iI] ;
fragment J : [jJ] ;
fragment K : [kK] ;
fragment L : [lL] ;
fragment M : [mM] ;
fragment N : [nN] ;
fragment O : [oO] ;
fragment P : [pP] ;
fragment Q : [qQ] ;
fragment R : [rR] ;
fragment S : [sS] ;
fragment T : [tT] ;
fragment U : [uU] ;
fragment V : [vV] ;
fragment W : [wW] ;
fragment X : [xX] ;
fragment Y : [yY] ;
fragment Z : [zZ] ;
