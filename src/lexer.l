/* 
 * lexer for parsing external source for collecting snippet of code.
 */
%{
#define CHAR 20
#define STRING 20
#define IDENTIFIER 20
#define CHAR 20

int *nlines;
void p(char *what, char *val)
{
    if(what[0] == '<')
        printf("%d:\033[32;1m%s\033[0m:%s", *nlines, ++what, val);
    else
        printf("%d:\033[32;1m%s\033[0m:%s\n", *nlines, what, val);
}
%}
    int num_lines = 0, num_chars = 0;


IDENTIFIER  [A-Za-z][A-Za-z0-9_]*
COMMENT     #
STRING      \"[^\"]*\"
VARIABLE    \${IDENTIFIER}
NUMBER      [0-9]+

/* exclusive start condition */
%x comment libido
%%

<comment>libido:        p("<libido=>", ""); BEGIN(libido);
<comment>\n             ++num_lines; BEGIN(0);
<comment>.              /* skip */ ++num_chars;

<libido>{IDENTIFIER}    p("<ID", yytext);
<libido>\n              ++num_lines; BEGIN(0);
<libido>.               ++num_chars; p("<C", yytext);


^[[:blank:]]*{COMMENT}    p("COMMENT", yytext); BEGIN(comment);
{VARIABLE}                p("variable", yytext);
{IDENTIFIER}              p("An identifier", yytext);
{STRING}                  p("STRING", yytext);
{NUMBER}                  p("<NUMBER", yytext);

[[:blank:]]             ++num_chars;
\n                      ++num_lines; ++num_chars;
.                       ++num_chars; p("<CHAR", yytext);

%%


int main(int argc, char **argv)
{
    num_lines = 1;
    nlines = &num_lines;
    yylex();
}
