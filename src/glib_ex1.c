//ex-compile.c
#include <glib.h>
#include <stdio.h>

/* See: http://www.ibm.com/developerworks/linux/tutorials/l-glib/index.html
 * https://developer.gnome.org/glib/stable/glib-Doubly-Linked-Lists.html
 * $ gcc -I/usr/include/glib-2.0 -I/usr/lib/glib-2.0/include  
 *    -lglib-2.0 -o ex-compile ex-compile.c
 */

int main(int argc, char** argv) {
 GList* list = NULL;

 list = g_list_append(list, "Hello world!");
 list = g_list_append(list, "some more");
 list = g_list_append(list, "some more1");
 list = g_list_append(list, "some more21");
 list = g_list_append(list, "some more3");
 
 printf("The first item is '%s'\n", (char*) g_list_first(list)->data);
 printf("The last item is '%s'\n", (char*) g_list_last(list)->data);
 return 0;
}
