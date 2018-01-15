# some_func
some_func() {
    echo "param $1"
}
myfunc() {
    echo some_func
    echo "c'est ça le pouvoir de la funk!"
}
func2() {
    echo "I call $(myfunc)"
}
