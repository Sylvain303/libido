/*
 * libido functions
 */

#include "functions.h"
#include <stdio.h>

#define FAIL_OPEN 301
#define MAX_LINE 1024

int parse_command_line(void) { return 1; }
int load_config(void) { return 1; }
int pass1_parser(void) { return 1; }
int resolve_references(void) { return 1; }

FILE *open_file(char *filename)
{
    FILE *f;

    /* will add some file lookup to smart location here */
    f = fopen(filename, "r");
    return f;
}

int fail_open(char *filename)
{
    printf("error: fail to open text file: '%s'\n", filename);
    return FAIL_OPEN;
}

int parse_external_sources(char *filename)
{ 
    FILE *f;
    char buf[MAX_LINE], *p;
    int n;
    
    if((f = open_file(filename)) == NULL)
        return fail_open(filename);

    while(!feof(f))
    {
       p = fgets(buf, MAX_LINE, f);
       if(p != NULL)
           printf("in:%s", buf);
       else
           printf("end\n");
    }

    fclose(f);

    return 1; 
}

int pass2_parser(void) { return 1; }
int write_buffers(void) { return 1; }
