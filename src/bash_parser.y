%code top {
#include <stdio.h>
}

%code requires {
#include "function_lines.h"
typedef int dummy_list;
}


%union {
    char *str;
    function_lines *range;
    dummy_list *list;
}

%{
/* from lexer.l */
extern FILE * yyin;
extern int yylineno;

/* for changing lexer start condition */
extern int function_body_change;
extern int unparsed_code_change;

int yylex(void);
void yyerror(char const *);

/* dummy */
dummy_list *make_list(char *e1, char *e2) { return NULL; }
int store_func_table(char *identifier, function_lines *range) { return 0xCACA; }

#define YYDEBUG 1
/* change a global var to modify lexer start condition */
#define ENTER(lexer_sc) lexer_sc ## _change = 1

/* globals */
GSList *function_start, *verbatim_start, *current_line;
%}


%token BASH_KEYWORD BASH_PONCTUATION BASH_STRING BASH_VAR CODE COMMENT COMMENT_LINE 
%token DEPEND FUNCTION INDENT LIBIDO NUMBER STRING UNPARSED VERBATIM 

/* assign type from %union to terminal and non-terminal symbols */
%token <str>    IDENTIFIER
%type  <str>    entity
%type  <range>  function_body
%type  <range>  verbatim_chunk
%type  <list>   entities


/* trick to extract %token: r!grep -o '[A-Z_]\{2,\}' < % | sort -u */

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
  | comment
  ;

comment:
    COMMENT
  | COMMENT libido_statment
  ;

libido_statment:
    LIBIDO verbatim_chunk
  | LIBIDO libido_dependency
  ;

function_def:
    FUNCTION IDENTIFIER '(' ')' function_body   { store_func_table($IDENTIFIER, $function_body); }
  | FUNCTION IDENTIFIER function_body           { store_func_table($IDENTIFIER, $function_body); }
  | IDENTIFIER '(' ')' function_body            { store_func_table($IDENTIFIER, $function_body); }
  ;

function_body:
  '{'                              { ENTER(function_body); function_start = current_line; }
     lines_of_indented_code
  '}'                              { $function_body = assign_collected(function_start, current_line); }
  ;

lines_of_indented_code:
    indented_code
  | lines_of_indented_code indented_code
  ;

indented_code:
    INDENT CODE
  | COMMENT_LINE
  | INDENT COMMENT_LINE
  ;

verbatim_chunk:
  VERBATIM '(' IDENTIFIER ')' '{'   { ENTER(unparsed_code); verbatim_start = current_line; }
    unparsed_lines
  LIBIDO '}'                        { $verbatim_chunk = assign_collected(verbatim_start, current_line); }
  ;

unparsed_lines:
    UNPARSED
  | unparsed_lines UNPARSED
  ;

libido_dependency:
  DEPEND '(' entities ')'
  ;

entities:
    entity                             { $entities = make_list($entity, NULL); } 
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

    initilize_lexer();
    /* TODO: current_line was in confict with lexer, change to something else */
    current_line = function_start = verbatim_start = NULL;

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
