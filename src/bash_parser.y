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
%token DEPEND FUNCTION IDENTIFIER INDENT LIBIDO UNPARSED_CODE VERBATIM

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
  | bash_code code_blocks
  ;

code_blocks:
    comment_block
  | function_def
  | libido_statment
  | free_code
  ;

libido_statment:
    verbatim_chunk
  | libido_dependency
  ;

comment_block:
    comment_block COMMENT
  | COMMENT
  ;

function_def:
    FUNCTION IDENTIFIER '(' ')' function_body
  | IDENTIFIER '(' ')' function_body
  ;

function_body:
  '{'                           { ENTER(function_body); }
     lines_of_indented_code
  '}'
  ;

free_code:
    BASH_KEYWORD
  | BASH_STRING
  | BASH_VAR
  | free_code ';' free_code
  | IDENTIFIER
  | BASH_PONCTUATION
  | INDENT
  | CODE
  ;


lines_of_indented_code:
    %empty
  | lines_of_indented_code indented_code
  ;

indented_code:
    INDENT CODE
  | COMMENT_LINE
  | INDENT COMMENT_LINE
  ;

verbatim_chunk:
  LIBIDO VERBATIM '(' IDENTIFIER ')' '{'   { ENTER(unparsed_code); }
    chunk_of_unparsed_code
  '}'
  ;

chunk_of_unparsed_code:
    %empty
  | chunk_of_unparsed_code UNPARSED_CODE
  ;

libido_dependency:
  DEPEND '(' entities ')'
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
