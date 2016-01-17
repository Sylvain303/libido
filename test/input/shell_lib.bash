#!/bin/bash
#
# some example lib for bash
#
# Here 3 examples: 2 functions, with a dependancy, a verbatim chunck of code
# libido should match: die, test_tool which depend on die, bash_main

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


# libido: verbatim(bash_main) {
# sourcing code detection, if code is sourced for debug purpose, main is not executed.
[[ $0 != "$BASH_SOURCE" ]] && sourced=1 || sourced=0
if  [[ $sourced -eq 0 ]]
then
    # pass positional argument as is
    main "$@"
fi
# libido: }
