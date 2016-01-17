#ifndef _COLLECTED_LINES_H
#define _COLLECTED_LINES_H

/* Makefile: 
 * $(CXX) $(CPPFLAGS) $(CXXFLAGS) -c test_collected_lines.cc $$(pkg-config --cflags glib-2.0) 
 * liker: $(CXX) $(CPPFLAGS) $(CXXFLAGS) $^ -lpthread $$(pkg-config --libs glib-2.0) -o $@
 */
#include <glib.h>
#include "buf_string.h"

#define BUF_SIZE 1024

typedef struct _collected_lines_t {
    GSList *list;
} CollectedLines;
/* add_new_line() : add a StringBuf to the list, return a new empty line
 */
StringBuf *add_new_line(CollectedLines *list, StringBuf *buf) {
    StringBuf *new_buf;
    list->list = g_slist_append(list->list, buf);
    new_buf = StringBuf_create(BUF_SIZE);
    return new_buf;
}

#endif /* _COLLECTED_LINES_H */
