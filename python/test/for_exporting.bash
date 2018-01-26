#!/bin/bash
#
# The following libido statement is telling libido to export all functions found inside
# this source file. Outsider chunks will be ignored.
#
# libido: export(*)
#

echo "some outsider code"
echo "more"

myfunc() {
    echo some_func
    echo "c'est ça le pouvoir de la funk!"
}

# libido: depend func2(myfunc)
func2() {
    echo "I call $(myfunc)"
}
