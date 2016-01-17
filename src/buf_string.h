#ifndef _BUF_STRING_H
#define  _BUF_STRING_H

typedef struct string_buffered {
    int size;
    int max_buf_size;
    char *str;
} StringBuf;


StringBuf *StringBuf_create(int size);
void StringBuf_destroy(StringBuf *buf);

int buffer_add(StringBuf *buf, char *collected);
int buffer_addc(StringBuf *buf, char collected_c);

#endif /* _BUF_STRING_H */
