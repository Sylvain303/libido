# in progress

command line interface with docopt

=> -e export

filter export


## Taged export

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
`libido_parser.token_map{}` is completedd during `load_lib()`, by sup-parser.
`libido_parser` instance is kept between all parsers via `parser_factory`
`token_map` is our reference for declarative dependancy. `get_dep()` uses it to resolve deps recursively.
