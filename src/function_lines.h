#ifndef _FUNCTION_LINES_H
#define _FUNCTION_LINES_H

#include <glib.h>
#include <stdio.h>

typedef struct function_lines {
    GSList *start;
    GSList *end;
} function_lines;

function_lines *assign_collected(GSList *start, GSList *end);
void fprint_function(FILE *output, function_lines *f);
#endif /* _FUNCTION_LINES_H */
