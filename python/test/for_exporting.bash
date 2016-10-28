#!/bin/bash
#
# libido: export *
#

echo "some outsider code"
echo "more"

myfunc() {
    echo some_func
    echo "c'est ça le pouvoir de la funk!"
}

func2() {
    echo "I call $(myfunc)"
}
