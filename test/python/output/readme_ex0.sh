#!/bin/bash 
#
# libido: bash_code=bash(die, docopts)
#
# Howto Rebuild: rebuild this code with:
# $ libido examples/readme_ex0.sh

echo 'some code here'

# libido code will be included/ updated here
# libido: expand bash_code
die() {
    echo "$*"
    exit 1
}

# missing: docopts
echo 'some more code using die() and or docopts'
if [[ -z "$1" ]]
then
    die "missing argument1"
fi
exit 0
