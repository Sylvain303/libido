#include "gtest/gtest.h"

/* imort as C code in C++ test framework */
extern "C"
{
#include "linked_list.h"
}


/* define a typedef for the list and for node having int */
LinkedList_DEFINE_TYPES(TLIST_int, int);

/* which produces:
 *
 * typedef struct __TLIST_int_node {
 *   int value;
 *   struct __TLIST_int_node *next;
 *   struct __TLIST_int_node *prev;
 * } TLIST_int_node;
 *
 * typedef struct __TLIST_int_list {
 *   int size;
 *   TLIST_int_node *head;
 *   TLIST_int_node *end;
 * } TLIST_int;
 */

TEST(C_LList, Create) {
  TLIST_int *l;
  l = LinkedList_create(TLIST_int);

  EXPECT_EQ(0, l->size);
  EXPECT_EQ(0, l->head);
  EXPECT_EQ(0, l->end);
}

TEST(C_LList, Destroy) {
  LinkedList *l;
  l = LinkedList_create(TLIST_int);
  LinkedList_destroy(l);
}

TEST(C_LList, list_push) {
    LinkedList *l;
    int val = 1;
    l = LinkedList_create(TLIST_int);

    for(int i = 1; i <= 100; i++, v += 10) { 
        list_push(l, i);
    }

    EXPECT_EQ(100,  l->size);
    EXPECT_EQ(0,    l->head->value);
    EXPECT_EQ(1000, l->end->value);
    EXPECT_EQ(10,   l->head->next->value);
    EXPECT_EQ(990,  l->end->prev->value);

    /* pointer test */
    EXPECT_EQ(0,   l->head->prev);
    EXPECT_EQ(0,   l->end->next);

    LinkedList_destroy(l);
}
