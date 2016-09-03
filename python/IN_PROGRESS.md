# in progress

refactoring `token_map{}` for recursive dependancy support for `expand` related token or assignment.

## deep code analyze

`libido_parser.token_map` should be changed during `load_lib()`, but `bash_parser` instanciate its own `libido_parser`
not related to *caller* `libido_parser`.  See `bash_parser` constructor.

## `libido_parser.py`

assignment could be differenciated from found ref in lib: `bash_code` dont depend on itself. Stored in `token_map`

refactorining:

    def resolve_assignement(self):
    def resolve_dependancies(self):
    def expand_all_chunk(self):
