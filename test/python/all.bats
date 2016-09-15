#!/bin/bash

# define vars for folders
source default_vars.sh

@test "render readme_ex0.sh" {
    ex=readme_ex0.sh
    in=$EX_DIR/$ex
    out=$OUT_DIR/$ex
    expected=$EXPECT_DIR/$ex

    $LIBIDO $in > $out
    diff -u $expected $out
}

@test "with dep" {
    ex=in_with_dep.sh
    in=$ex
    out=$OUT_DIR/$ex
    expected=$EXPECT_DIR/$ex

    $LIBIDO $in > $out
    diff -u $expected $out
}
