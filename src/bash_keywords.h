/*
 * bash_keywords.h - detect and optimize bash_keywords detection
 */

#ifndef BASH_KEYWORD_INC
#define BASH_KEYWORD_INC

extern char *bash_Keywords[];

typedef struct bash_keyword {
    int counter;
    char *keyword;
} BashKeyword;

/* static table */
extern BashKeyword frequency_bash_keywords[];

BashKeyword *init_bash_keywords(void);
int is_keyword(char *k);
int update_keyword_counter(int i);

#endif /* BASH_KEYWORD_INC */
