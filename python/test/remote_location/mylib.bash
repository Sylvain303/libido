# myfunc
myfunc() {
    echo some_func
    echo "c'est ça le pouvoir de la funk!"
}
# func2
func2() {
    echo "I call $(myfunc)"
}
two() {
    for i in $(seq 1 2)
    do
        one
    done
}
one() {
    echo "code for one"
}
