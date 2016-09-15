#!/bin/bash
#
# re-build expected from libido

source default_vars.sh

# fetch input for testing from unittest
inputs="$(awk -F= '/ex=/ { print $2 }' *.bats)"

for ex in $inputs
do
    in=$ex
    # guess where it can live…
    if [[ "$ex" =~ _ex ]]
    then
        in=$EX_DIR/$ex
    fi
    expected=$EXPECT_DIR/$ex
    $LIBIDO $in > $expected
done
