%{
#include <ctype.h>
#include <stdio.h>
extern FILE * yyin; 
extern int *nlines, num_lines;
int yylex(void);
void yyerror(char const *);

int make_list(int e1, int e2) { return 2; }

#define YYDEBUG 1
%}

%token CODE COMMENT DEPEND FUNCTION IDENTIFIER INDENT VERBATIM UNPARSED_CODE

/* trick: !grep -o '[A-Z_]\{2,\}' < % | sort -u */
%define parse.error verbose
%define parse.trace

/* declare a libido code_chunk, composed by 2 entities die and docopts
 * # libido: bash_code=bash(die, docopts)
 *
 * in input parser: make a dependent inclusion for this function to another one
 * # libido: depend(die)
 *
 */

%%

bash_code:
    bash_header
  | function_def
  | verbatim_chunk
  | libido_dependency
  ;

bash_header:
    %empty
  | bash_header COMMENT
  ;

function_def:
    FUNCTION IDENTIFIER '(' ')' function_body
  | IDENTIFIER '(' ')' function_body
  ;

function_body:
  '{' 
  lines_of_indented_code
  '}'
  ;

lines_of_indented_code:
    INDENT CODE
  | %empty
  | COMMENT
  | INDENT COMMENT
  ;

verbatim_chunk:
  VERBATIM '(' IDENTIFIER ')' '{'
  chunk_of_unparsed_code
  '}'
  ;

chunk_of_unparsed_code:
    %empty
  | UNPARSED_CODE
  ;

libido_dependency:
  DEPEND '(' entities ')'
  ;

entities: entity 
        | entity[left] ',' entity[right]     { $entities = make_list($left, $right); }
        ;

entity: IDENTIFIER      { $entity = $IDENTIFIER; }
%%

/* 
  * Main program. initializes data and calls yyparse.
  */ 
int main(int argc, char **argv) {
    nlines = &num_lines;
    yyin = fopen(argv[1],"r");
    yyparse();
}
void yyerror(char const *s) {
    fprintf(stderr,"%d:%s\n", *nlines, s);
}
