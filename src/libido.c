/*
 * libido.c
 */

#include <stdio.h>
#include <stdlib.h>


#include "functions.h"

/*
 * algorithm
 *
 * load_config
 * first pass: parse input code
 * fetch snipet
 * second pass: expand code
 * save
 */

int main(int argc, char **argv)
{
    printf("welcome to libido!\n");

    parse_command_line();
    load_config();

    pass1_parser();
    resolve_references();

    parse_external_sources("../examples/libido/shell_lib.bash");

    pass2_parser();

    write_buffers();

    exit(0);
}
