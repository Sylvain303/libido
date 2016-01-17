#include <assert.h>
#include <string.h>
#include <stdlib.h>

#include "buf_string.h"

int buffer_add(StringBuf *buf, char *collected) {
    int new_size = strlen(collected);

    /* DONT Resize just hope that it has enough memory */
    assert((buf->size + new_size +1) <= buf->max_buf_size);

    strncpy(&buf->str[buf->size], collected, new_size);
    buf->size += new_size;
    
    return buf->size;
}

/* optimized collecte for single char */
int buffer_addc(StringBuf *buf, char collected_c) {
    /* DONT Resize just hope that it has enough memory */
    assert((buf->size + 1) <= buf->max_buf_size);

    buf->str[buf->size] = collected_c;
    buf->str[buf->size + 1] = '\0';
    return ++buf->size;
}

StringBuf *StringBuf_create(int size) {
    StringBuf *p;
    p = (StringBuf * ) malloc(sizeof(StringBuf));
    p->size = 0;
    p->max_buf_size = size;
    p->str = (char *) malloc(sizeof(char) * size);

    return p;
}

void StringBuf_destroy(StringBuf *p) {
    free(p->str);
    free(p);
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
