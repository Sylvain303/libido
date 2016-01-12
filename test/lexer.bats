#!/bin/bash
# bats unittest script

# test grammar for bash parsing
#create input.bash
#create expect_bash.parsed
#bash_parser input.bash > result_bash.parsed
#compare expect_bash.parsed result_bash.parsed

init() {
    cd ../src/
    make lexer
    lexer=$PWD/lexer
    cd - > /dev/null
}

# tests

@test "test lexer token" {
    init
    timeout 1 $lexer < ../examples/libido/shell_lib.bash | diff -u bash_parsed.token -
}
