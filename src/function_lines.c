#include "function_lines.h"
#include <stdlib.h>
#include "buf_string.h"

function_lines *assign_collected(GSList *start, GSList *end) {
    function_lines *func_block;
    func_block = (function_lines*) malloc(sizeof(function_lines));
    func_block->start = start;
    func_block->end = end;

    return func_block;
}

void fprint_function(FILE *output, function_lines *f) {
    GSList *p, *pp;
    pp = p = f->start;

    while(p && pp != f->end ) {
        fprintf(output, "%s\n", ((StringBuf *)p->data)->str);
        pp = p;
        p = p->next;
    }
}
