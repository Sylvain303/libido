#include "gtest/gtest.h"

/* imort as C code in C++ test framework */
extern "C"
{
#include "collected_lines.h"
}


#define GET_STR(GSList_pointer) (char *) ((StringBuf *)GSList_pointer->data)->str

TEST(C_collected_lines, add_new_line) {
  StringBuf *buf, *buf0;
  GSList *list = NULL, *e;

  buf0 = buf = StringBuf_create(1024);

  buffer_add(buf, (char *) "some");
  buf = add_new_line(&list, buf);

  buffer_add(buf, (char *) "some more");
  buf = add_new_line(&list, buf);

  EXPECT_NE(buf, buf0);
  EXPECT_EQ(2, g_slist_length(list));
  e = list;
  EXPECT_STREQ("some", (char *) GET_STR(e));
  EXPECT_STREQ("some more", (char *) GET_STR(e->next));
  EXPECT_EQ(buf0, (StringBuf *) e->data);
}
