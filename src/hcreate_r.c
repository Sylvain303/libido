#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define _GNU_SOURCE
#define __USE_GNU
#include <search.h>

char *data[] = { "alpha", "bravo", "charlie", "delta",
    "echo", "foxtrot", "golf", "hotel", "india", "juliet",
    "kilo", "lima", "mike", "november", "oscar", "papa",
    "quebec", "romeo", "sierra", "tango", "uniform",
    "victor", "whisky", "x-ray", "yankee", "zulu"
};

int main(void)
{
   ENTRY e, *ep;
   int i, r;
   struct hsearch_data h;
   memset(&h, 0, sizeof(h));

   hcreate_r(30, &h);

   for (i = 0; i < 24; i++) {
       e.key = data[i];
       /* data is just an integer, instead of a
          pointer to something */
       e.data = (void *) (long)i;
       r = hsearch_r(e, ENTER, &ep, &h);

       /* there should be no failures */
       if (ep == NULL) {
           fprintf(stderr, "entry failed\n");
           exit(EXIT_FAILURE);
       }
   }

   for (i = 22; i < 26; i++) {
       /* print two entries from the table, and
          show that two are not in the table */
       e.key = data[i];
       r = hsearch_r(e, FIND, &ep, &h);
       printf("%9.9s -> %9.9s:%ld\n", e.key,
              ep ? ep->key : "NULL", ep ? (long)(ep->data) : 0);
   }
    
   // remove one
   e.key = "quebec";
   if(r = hsearch_r(e, FIND, &ep, &h)) {
       ep->key = NULL;
       ep->data = NULL;
    }

   if(! hsearch_r(e, FIND, &ep, &h)) {
       printf("quebec still here!\n");
   }
        



   hdestroy_r(&h);
   exit(EXIT_SUCCESS);
}
