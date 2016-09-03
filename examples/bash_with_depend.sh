#!/bin/bash 
#
# libido: bash_code=bash(test_tool)
#

# libido: expand bash_code

# die will be imported too as dependencies
if [[ -z "$1" ]]
then
    die "missing argument1"
fi
exit 0

test_tool libido
