#!/bin/bash
#
# libido: code=bash(three)
#
# libido: expand code
# expanded from: code => three,two,one
one() {
    echo "code for one"
}
two() {
    for i in $(seq 1 2)
    do
        echo "two:$(one)"
    done
}
three() {
    echo "code for three"
    two
}

three ici
