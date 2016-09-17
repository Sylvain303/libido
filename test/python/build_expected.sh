#!/bin/bash
#
# re-build expected from libido
#

source default_vars.sh

# fetch input for testing from unittest assignment
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

    # also run script for expecting result
    chmod a+x $expected
    output=$EXPECT_DIR/$(basename $expected).out
    $expected > $output
    echo -e "\033[31;1m===================== $expected =====================\033[0m"
    cat -n  $output
done
