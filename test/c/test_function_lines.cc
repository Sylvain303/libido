#include "gtest/gtest.h"

/* imort as C code in C++ test framework */
extern "C"
{
#include "collected_lines.h"
#include "function_lines.h"
}


#define GET_STR(GSList_pointer) (char *) ((StringBuf *)GSList_pointer->data)->str
#define STR_APPEND(result, fname, suffix) strcpy(result, fname); strcat(result, suffix)

int read_lines_from_file(GSList **lines, const char *fname) {
    FILE *f;
    char rbuf[BUF_SIZE];
    StringBuf *buf;
    int n = 0, nbc;

    f = fopen(fname, "r");
    assert(f);
    buf = StringBuf_create(BUF_SIZE); 

    while(fgets(rbuf, BUF_SIZE, f)) {
        /* chomp */
        nbc = strlen(rbuf);
        rbuf[nbc - 1] = '\0';
        buffer_add(buf, rbuf);

        buf = add_new_line(lines, buf);
        n++;
    }

    fclose(f);

    return n;
}

GSList *get_lines_ref(GSList *l, int line_n) {
    GSList *p;
    int n = 0;
    p = l;
    while(p) {
        n++;
        if(n == line_n)
            break;
        p = p->next;
    }

    return p;
}

#define CMD_MAX 1024
bool call_diff(char *fname) {
    char cmd[CMD_MAX];
    assert(snprintf(cmd, CMD_MAX, "diff %s %s.output", fname, fname) <= CMD_MAX);
    printf("%s\n", cmd);
    return system(cmd) == 0;
}

// ############################################################################
//
TEST(C_function_lines, call_diff) {
    EXPECT_TRUE(call_diff((char *) "output/function_test_tool.bash"));
    EXPECT_FALSE(call_diff((char *) "output/function_test_tool.b"));
}

TEST(C_function_lines, read_lines_from_file) {
    const char fname[] = "input/shell_lib.bash";
    GSList *lines = NULL;
    int n;

    n = read_lines_from_file(&lines, fname);

    EXPECT_EQ(35, n);
    EXPECT_STREQ("#!/bin/bash", GET_STR(lines));
}

TEST(C_function_lines, get_lines_ref) {
    const char fname[] = "input/shell_lib.bash", match[] = "die() {",
          match2[] = "# libido: }";
    GSList *lines = NULL, *p;

    read_lines_from_file(&lines, fname);

    p = get_lines_ref(lines, 8);
    EXPECT_STREQ(match, GET_STR(p));
    p = get_lines_ref(lines, 35);
    EXPECT_STREQ(match2, GET_STR(p));
}

TEST(C_function_lines, assign_collected) {
  GSList *lines = NULL, *start, *end;
  function_lines *func_block;

  read_lines_from_file(&lines, "input/shell_lib.bash");

  start = get_lines_ref(lines, 15);
  end = get_lines_ref(lines, 24);

  func_block = assign_collected(start, end);

  EXPECT_EQ(start, func_block->start);
  EXPECT_EQ(end, func_block->end);

  const char output[] = "output/function_test_tool.bash";
  char result[80];
  STR_APPEND(result, output, ".output");
  EXPECT_STREQ("output/function_test_tool.bash.output", result);

  FILE *fdest = fopen(result, "wt");
  fprint_function(fdest, func_block);
  fclose(fdest);
  EXPECT_TRUE(call_diff((char *) output));
}
