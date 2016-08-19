#!/bin/bash

source init.sh

@test "render readme_ex0.sh" {
    ex=readme_ex0.sh
    in=$ex_dir/$ex
    out=$out_dir/$ex
    expected=$expect_dir/$ex

    $libido $in > $out
    diff -u $expected $out
}
