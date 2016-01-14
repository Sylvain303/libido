%{
#include <stdio.h>

/* from lexer.l */
extern FILE * yyin;
extern int yylineno;

/* for changing lexer start condition */
extern int function_body_change;
extern int unparsed_code_change;

int yylex(void);
void yyerror(char const *);

/* dummy */
int make_list(int e1, int e2) { return 2; }

#define YYDEBUG 1
/* change a global var to modify lexer start condition */
#define ENTER(lexer_sc) lexer_sc ## _change = 1
%}

%token BASH_KEYWORD BASH_PONCTUATION BASH_STRING BASH_VAR CODE COMMENT COMMENT_LINE 
%token DEPEND FUNCTION IDENTIFIER INDENT LIBIDO NUMBER STRING VERBATIM

/* trick: r!grep -o '[A-Z_]\{2,\}' < % | sort -u */

%verbose
%define parse.error verbose
%define parse.trace true


/* declare a libido code_chunk, composed by 2 entities die and docopts
 * # libido: bash_code=bash(die, docopts)
 *
 * in input parser: make a dependent inclusion for this function to another one
 * # libido: depend(die)
 *
 */


%%

bash_code:
    %empty
  | bash_code code_block
  ;

code_block:
    function_def
  | COMMENT libido_statment
  | COMMENT '\n'
  | '\n'
  ;

libido_statment:
    LIBIDO verbatim_chunk
  | LIBIDO libido_dependency
  ;

function_def:
    FUNCTION IDENTIFIER '(' ')' newline_list function_body
  | FUNCTION IDENTIFIER newline_list function_body
  | IDENTIFIER '(' ')' newline_list function_body
  ;

newline_list:
    %empty
  | newline_list '\n'
  ;

function_body:
  '{'
     lines_of_indented_code
  '}'
  ;

lines_of_indented_code:
    newline_list indented_code
  | lines_of_indented_code indented_code
  ;

indented_code:
    INDENT CODE '\n'
  | COMMENT_LINE '\n'
  | INDENT COMMENT_LINE '\n'
  ;

free_code:
    bash_line '\n'
  | '{' bash_code '}'
  | function_def
  | COMMENT '\n'
  ;

bash_line:
    bash_line bash_line
    BASH_KEYWORD
  | BASH_STRING
  | BASH_VAR
  | ';'
  | IDENTIFIER
  | BASH_PONCTUATION
  | NUMBER
  | STRING
  | '='
  ;


verbatim_chunk:
  VERBATIM '(' IDENTIFIER ')' '{' '\n'
    newline_list free_code
  COMMENT LIBIDO '}' '\n'
  ;

libido_dependency:
  DEPEND '(' entities ')' '\n'
  ;

entities:
    entity
  | entity[left] ',' entity[right]     { $entities = make_list($left, $right); }
  ;

entity:
  IDENTIFIER      { $entity = $IDENTIFIER; }
  ;
%%

/*
  * Main program. initializes data and calls yyparse.
  */
int main(int argc, char **argv) {
    int filepos = 1;

    init_bash_keywords();

    /* switch to debug mode */
    if(strcmp(argv[1], "-d") == 0) {
        yydebug = 1;
        filepos++;
    }

    yyin = fopen(argv[filepos],"r");
    yyparse();
}

void yyerror(char const *s) {
    fprintf(stderr,"%d:%s\n", yylineno, s);
}
