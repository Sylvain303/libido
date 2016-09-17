/* Infix notation calculator.  */

%{
  #include <math.h>
  #include <stdio.h>
  int yylex (void);
  void yyerror (char const *);
%}

/* Bison declarations.  */
%define api.value.type {double}
%token NUM
%left '-' '+'
%left '*' '/'
%precedence NEG   /* negation--unary minus */
%right '^'        /* exponentiation */

%%

input:
  %empty
| input line
;

line:
  '\n'
| exp '\n'          { printf ("\t%.10g\n", $exp); }
;

exp:
  NUM                           { $$ = $NUM;           }
| exp[left] '+' exp[right]      { $$ = $left + $right;      }
| exp[left] '-' exp[right]      { $$ = $left - $right;      }
| exp[left] '*' exp[right]      { $$ = $left * $right;      }
| exp[left] '/' exp[right]      { $$ = $left / $right;      }
| '-' exp  %prec NEG { $$ = -$2;          }
| exp[left] '^' exp[right]        { $$ = pow ($left, $right); }
| '(' exp ')'        { $$ = $2;           }
;

%%



#include <stdio.h>

/* Called by yyparse on error.  */
void
yyerror (char const *s)
{
  fprintf (stderr, "%s\n", s);
}

int
main (void)
{
  return yyparse ();
}



/* The lexical analyzer returns a double floating point
   number on the stack and the token NUM, or the numeric code
   of the character read if not a number.  It skips all blanks
   and tabs, and returns 0 for end-of-input.  */

#include <ctype.h>

int
yylex (void)
{
  int c;

  /* Skip white space.  */
  while ((c = getchar ()) == ' ' || c == '\t')
    continue;

  /* Process numbers.  */
  if (c == '.' || isdigit (c))
    {
      ungetc (c, stdin);
      scanf ("%lf", &yylval);
      return NUM;
    }

  /* Return end-of-input.  */
  if (c == EOF)
    return 0;
  /* Return a single char.  */
  return c;
}

