#include <stdio.h>


char *Keywords[] = {
    "if",
    "then",
    "else",
    "fi",
    "case",
    "esac",
    "while",
    "do",
    "done",
    "source",
    NULL
};

int counter = sizeof(Keywords) / sizeof(char *);

int main(void)
{
    printf("counter=%d\n", counter);
}
