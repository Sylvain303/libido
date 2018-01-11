some_func() {
    echo "param $1"
}
# some_func
one() {
    echo "code for one"
}
two() {
    for i in $(seq 1 2)
    do
        one
    done
}
three() {
    echo "code for three"
    two
}
