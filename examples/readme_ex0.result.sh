#!/bin/bash 
#
# libido: bash_code=bash(die, docopts)
# libido: ref(libido/shell_lib.bash)
#
# Howto Rebuild: rebuild this code with:
# $ libido examples/readme_ex0.sh

echo 'some code here'

# libido code will be included/ updated here
# libido: expand bash_code => EXPANDED {
die() {
    echo "$*"
    exit 1
}

# helper, test if a shell program exists in PATH
# libido: depend(die)
test_tool() {
    local cmd=$1
    if type $cmd > /dev/null
    then
        # OK
        return 0
    else
        die "tool missing: $cmd"
    fi
}
# libido: => EXPANDED }

echo 'some more code using die() and or docopts'
if [[ -z "$1" ]]
then
    die "missing argument1"
fi
exit 0
