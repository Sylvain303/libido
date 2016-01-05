#!/bin/bash 
#
# this is ex0 from readme but written with gpp text-processor
#
# libido: bash_code=bash(die, docopts)
# => becomes: parse source where die and docopts lives and create bash_code
# => inclusion sources
#
# Howto Rebuild: rebuild this code with:
# $ libido examples/readme_ex0.sh
# => becomes:
# $ make split-libido-to-gpp
# $ gpp -I gpp readme_ex0.gpp.sh

echo 'some code here'

# libido code will be included/ updated here
# libido: expand bash_code
# => becomes:
#include die_bash_code.sh

echo 'some more code using die() and or docopts'
if [[ -z "$1" ]]
then
    die "missing argument1"
fi
exit 0
