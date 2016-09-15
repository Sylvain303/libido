#!/bin/bash
#
# libido: allcode=bash(one, two, three)
#

one() {
    echo "code for one"
}

# libido: depend two(one)
two() {
    for i in $(seq 1 2)
    do
        echo "two:$(one)"
    done
}

# libido: depend three(two)
three() {
    echo "code for three"
    two
}
