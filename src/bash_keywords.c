#include "bash_keywords.h"

char *bash_Keywords[] = {
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
    0
};

BashKeyword frequency_bash_keywords[sizeof(bash_Keywords)/sizeof(char *)];

BashKeyword *init_bash_keywords(void) {
    BashKeyword *pf = frequency_bash_keywords;
    char **pk = bash_Keywords;

    while(*pk) {
        pf->counter = 0;
        pf->keyword = *pk;

        pk++;
        pf++;
    }

    return frequency_bash_keywords;
}

int update_keyword_counter(int i) {
    frequency_bash_keywords[i].counter++;
}

int is_keyword(char *k) {
    int i = 0;
    char **p = bash_Keywords;

    while(*p) {
        if(strcmp(k, *p) == 0) {
            update_keyword_counter(i);
            return 1;
        }
        p++;
        i++;
    }
    return 0;
}
