# in progress

command line interface with docopt

## deeper code analyze

### `libido_parser`
`libido_parser.token_map{}` is completedd during `load_lib()`, by sup-parser.
`libido_parser` instance is kept between all parsers via `parser_factory`
`token_map` is our reference for declarative dependancy. `get_dep()` uses it to resolve deps recursively.
