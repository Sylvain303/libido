# in progress

refactoring `token_map{}` and `resolve_dependancies()`_for recursive dependancy support for `expand` related token or
assignment.  Using symbol() with type for `chunk` and `var` with `tsym`.

`token_map` is our reference for declarative dependancy. `get_dep()` uses it to resolve deps recursively.

not working yet `dump_result()` with introduced dependancies

## deep code analyze

`libido_parser.token_map{}` is completedd during `load_lib()`, by sup-parser.
`libido_parser` instance is kept between all parsers via `parser_factory`
