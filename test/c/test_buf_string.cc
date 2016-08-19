#include "gtest/gtest.h"

/* imort as C code in C++ test framework */
extern "C"
{
#include "buf_string.h"
}


TEST(C_BufString, Create) {
  StringBuf *buf;
  buf = StringBuf_create(1024);
  EXPECT_EQ(1024, buf->max_buf_size);
  EXPECT_EQ(0, buf->size);
}

TEST(C_BufString, Destroy) {
  StringBuf *buf;
  buf = StringBuf_create(1024);
  StringBuf_destroy(buf);
}

TEST(C_BufString, buffer_add) {
  StringBuf *buf;
  buf = StringBuf_create(1024);
  const char *inputs[] = {
      "some",
      "more",
      "StringBuf",
      "if",
      "",
      "after empty",
      " ",
      "end",
      0
  };

  char **p = (char **) inputs;

  int t0, t1, s, sum = 0;
  while(*p) {
      t0 = buf->size;
      t1 = buffer_add(buf, *p);

      s = strlen(*p);
      sum += s;

      EXPECT_EQ(s, t1 - t0);

      p++;
  }

  EXPECT_EQ(sum, buf->size);
  StringBuf_destroy(buf);
}

TEST(C_BufString, buffer_addc) {
  StringBuf *buf;
  buf = StringBuf_create(1024);
  int t0, t1;

  EXPECT_EQ(0, buf->size);
  
  t0 = buffer_addc(buf, 'c');
  t1 = buffer_addc(buf, 'b');

  EXPECT_EQ(1, t0);
  EXPECT_EQ(2, t1);
  EXPECT_STREQ("cb", buf->str);
  EXPECT_EQ(2, buf->size);

  /* mix with buffer_add() */
  buffer_add(buf, (char*) " pipo");
  t1 = buffer_addc(buf, ' ');

  EXPECT_STREQ("cb pipo ", buf->str);
  t0 = strlen("cb pipo ");
  EXPECT_EQ(t0, buf->size);
  EXPECT_EQ(t0, t1);

  StringBuf_destroy(buf);
}
