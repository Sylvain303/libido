%token EXPAND VARIABLE BASH IDENTIFIER

/* declare a libido code_chunk, composed by 2 entities die and docopts
 * # libido: bash_code=bash(die, docopts)
 *
 * in input parser: make a dependent inclusion for this function to another one
 * # libido: depend(die)
 *
 * in expanded code: execute 'expand' for bash_code assigned chunck
 * # libido: expand bash_code
 *
 */

%%

libido_code: assignment |
           action_code;

action_code: EXPAND entity ;

assignment: VARIABLE '='  parser '(' entities ')' ;

parser: BASH ;

entities: entity |
        entity ',' entity ;

entity: IDENTIFIER;
