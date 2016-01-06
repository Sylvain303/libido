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

libido_code: 
           assignment        
           | action_code
           ;

action_code: EXPAND entity { $action_code = libido->expand($entity); }
           ;

assignment: VARIABLE '='  parser '(' entities ')'  { libido->assign($VARIABLE, exctract_from_code($parser, $entities); }
          ;

parser: BASH        { $parser = create_parser(bash_parser); }
      ;

entities: entity 
        | entity[left] ',' entity[right]     { $entities = make_list($left, $right); }
        ;

entity: IDENTIFIER      { $entity = lookup_table->find($IDENTIFIER); }
      ;

%%

int main(int argc, char **argv)
{
    Libido *libido = libido_create();
    Symbol_table *lookup_table = libido->symbols;

    libido->start_parser();
}
