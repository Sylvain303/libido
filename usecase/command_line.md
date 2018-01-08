# libido command line use

most of the listed command doesn't exist at all

```
libido list     ==> list available top_level template names or repositories
libido config   ==> show current config (libido.conf)
libido init     ==> create a new libido.conf and or a repsitory
libido parse    ==> parse a code and show result on stdout (parsable output)
libido add [-u] ==> add a code bloc to your libido repository
libido update   ==> update only a bloc
libido del      ==> delete a bloc (revertable in repository history)
libido show     ==> show a bloc (+ information if requested)
libido do       ==> changes SOURCE_FILES, replace libido code inplace, default behavior
libido export   ==> export marked piece of code, to remote_project (update)
libido diff     ==> no change, `diff -u SOURCE_FILE result` on stdout
libido help     ==> show internal help
libido cat      ==> as do but generated source in outputed to stdout
```

## `libido parse`

parse input bash code and displays parsed chunks

## `libido list`
## `libido config`
## `libido init`

## `libido add`

from stdin (or editor `:'<,'>w!libido add`)

cat script.sh | libido add

## `libido update`
## `libido del`
## `libido show`
## `libido do`
## `libido export`

export libido chucks to the remote_project. Libido chucks are:

* funtions if nothing is specifided all function are exported
* `export(...)` only pieces of code listed in export statments
* `-m` shell-like glob function names from the input

## `libido diff`
## `libido help`
## `libido cat`
