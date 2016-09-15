#!/bin/bash
#
# libido: code=bash(three)
#
# libido: expand code
three() {
    echo "code for three"
    two
}
two() {
    for i in $(seq 1 2)
    do
        echo "two:$(one)"
    done
}
one() {
    echo "code for one"
}

three ici
