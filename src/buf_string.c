#include <assert.h>
#include <stdio.h>
#include <string.h>

#define MAX_BUF 1024*16


typedef struct string_buffered {
    int size;
    char str[MAX_BUF];
} StringBuf;


int buffer_add(StringBuf *buf, char *collected) {
    int new_size = strlen(collected);
    assert((buf->size + new_size +1) <= MAX_BUF);
    strncpy(&buf->str[buf->size], collected, new_size);
    buf->size += new_size;
    
    return buf->size;
}

#ifdef DEBUG_BUF_STRING
int main(int argc, char **argv) {
    StringBuf s;
    s.size = 0;
    int i;

    for(i = 1; i <argc; i++) {
        printf("%d:+%s\n", s.size, argv[i]);
        buffer_add(&s, argv[i]);
    }
}
#endif
