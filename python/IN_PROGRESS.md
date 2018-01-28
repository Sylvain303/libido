# in progress

=> export `process_export()`

filter export, export code to libido `lib_source` pointed in libido.conf

* dependancy export only matched function - Partial dependencies in progress
* preserve libido dependencies statment in exported code => related comment


## TODO
add functional testing:

```
git checkout -- remote_location/mylib.bash
./libido.py export for_exporting.bash
# nodup !!
```

## Tagged export

A tagged export is a part of the code which is named by libido statement.

The following example, should export `fail()` and `me`, which is an libido alias defined by `verbatim` statement

~~~bash
# libido: export(fail, me)
fail() {
  local msg="error: %s"
  printf "$msg\n" "$1"
  exit 1
}


# libido: verbatim(me) {
me=$(readlink -f "$0")
# libido: }
~~~

## test to add

read /dev/null should not raise error with libido.py (move fail)

## deeper code analyze

### `libido_parser`
`libido_parser.token_map{}` is completed during `load_lib()`, by sup-parser.
`libido_parser` instance is kept between all parsers via `parser_factory`
`token_map` is our reference for declarative dependancy. `get_dep()` uses it to resolve deps recursively.
