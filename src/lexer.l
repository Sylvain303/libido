/*
 * lexer for parsing external source for collecting snippet of code.
 */
    int num_lines = 0, num_chars = 0;

ID   [a-z][a-z0-9]*
%%

libido: printf("keyword:%d:%s\n", num_lines, yytext);

{ID}    printf("An identifier:%d:%s\n", num_lines, yytext);

\n      ++num_lines; ++num_chars;
.       ++num_chars;

