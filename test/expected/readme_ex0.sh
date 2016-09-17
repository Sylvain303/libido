#!/bin/bash 
#
# libido: bash_code=bash(die)
#
# Howto Rebuild: rebuild this code with:
# $ libido examples/readme_ex0.sh

echo 'some code here'

# libido code will be included/ updated here
# libido: expand bash_code
# expanded from: bash_code => die
die() {
    echo "$*"
    exit 1
}
echo 'some more code using die() and or docopts'
if [[ -z "$1" ]]
then
    die "missing argument1"
fi
exit 0
