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
