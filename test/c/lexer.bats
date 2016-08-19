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

init

# tests

@test "test lexer token" {
    src=input/shell_lib.bash
    timeout 1 $lexer < $src | diff -u bash_parsed.token -
}

@test "test lexer colleccollect" {
    src=input/shell_lib.bash
    timeout 1 $lexer --collected < $src | sed -n '/^LEXER_END/,$ {/LEXER_END/ d; p}' \
     | diff - $src
}
