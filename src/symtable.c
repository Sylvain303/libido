#include <math.h>
#include <stdio.h>

/* Function type.  */
typedef double (*func_t) (double);

/* Data type for links in the chain of symbols.  */
#define VAR 1
#define FNCT 2
struct symrec
{
  char *name;  /* name of symbol */
  int type;    /* type of symbol: either VAR or FNCT */
  union
  {
    double var;      /* value of a VAR */
    func_t fnctptr;  /* value of a FNCT */
  } value;
  struct symrec *next;  /* link field */
};

typedef struct symrec symrec;

/* The symbol table: a chain of 'struct symrec'.  */
//extern symrec *sym_table;

symrec *putsym (char const *, int);
symrec *getsym (char const *);

// The new version of main will call init_table to initialize the symbol table:

struct init
{
  char const *fname;
  double (*fnct) (double);
};

struct init const arith_fncts[] =
{
  { "atan", atan },
  { "cos",  cos  },
  { "exp",  exp  },
  { "ln",   log  },
  { "sin",  sin  },
  { "sqrt", sqrt },
  { 0, 0 },
};

/* The symbol table: a chain of 'struct symrec'.  */
symrec *sym_table;

/* Put arithmetic functions in table.  */
static void init_table (void)
{
  int i;
  for (i = 0; arith_fncts[i].fname != 0; i++)
    {
      symrec *ptr = putsym (arith_fncts[i].fname, FNCT);
      ptr->value.fnctptr = arith_fncts[i].fnct;
    }
}

// By simply editing the initialization list and adding the necessary include files, you can add additional functions to the calculator.
// 
// Two important functions allow look-up and installation of symbols in the
// symbol table. The function putsym is passed a name and the type (VAR or FNCT)
// of the object to be installed. The object is linked to the front of the list,
// and a pointer to the object is returned. The function getsym is passed the name
// of the symbol to look up. If found, a pointer to that symbol is returned;
// otherwise zero is returned.

#include <stdlib.h> /* malloc. */
#include <string.h> /* strlen. */

symrec * putsym (char const *sym_name, int sym_type)
{
  symrec *ptr = (symrec *) malloc (sizeof (symrec));
  ptr->name = (char *) malloc (strlen (sym_name) + 1);
  strcpy (ptr->name,sym_name);
  ptr->type = sym_type;
  ptr->value.var = 0; /* Set value to 0 even if fctn.  */
  ptr->next = (struct symrec *)sym_table;
  sym_table = ptr;
  return ptr;
}

symrec * getsym (char const *sym_name)
{
  symrec *ptr;
  for (ptr = sym_table; ptr != (symrec *) 0;
       ptr = (symrec *)ptr->next)
    if (strcmp (ptr->name, sym_name) == 0)
      return ptr;
  return 0;
}

double douze(double d) { return 12.0; }

int main(void)
{
    init_table();

    symrec *ptr;
    ptr = putsym("douze", FNCT);
    ptr->value.fnctptr = douze;

    double n;
    func_t f;

    ptr = getsym("sqrt");
    f = ptr->value.fnctptr;

    printf("r=%lf\n", f(36.0));

    ptr = getsym("douze");
    f = ptr->value.fnctptr;
    printf("r=%lf\n", f(1.0));

}
