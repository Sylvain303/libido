#!/bin/bash 
#
# libido: bash_code=bash(die, docopts)
# libido: => REF(libido/shell_lib.bash)
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
# libido: => EXPANDED }

echo 'some more code using die() and or docopts'
if [[ -z "$1" ]]
then
    die "missing argument1"
fi
exit 0
