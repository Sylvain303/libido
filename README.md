# libido - handle your personal library of code

Make your own lib by merging pieces of code into your code.

What?

libido stand for maximizing your pleasure! => lib I do

`libido` is a smart text preprocessor/editor which modifies your code inline!
By inserting comment (or not) with `libido:` keyword you can expand/update some part of your code with your lovely
crafted snippet.

OK, a kind of super `sed`, with a nice syntax to extract, fetch, update inline chunk of code. See bellow.

## Status : Prototype

This project is a sandbox for idea. It cares about parsing and programming freely.

Draft and prototype.

* some test with googleTest in `test/`
* some test with bats in `test/`
* parse an external source to match code token with the grammar (See [example](examples/libido/shell_lib.bash))
* some prototype in C for buffering data
* Makefiles OK.
* a python protype implementing part of the goals described here in `python/` + unittest with `py.test`

## Written in C and python

Old school programming. OK may be. But lightning fast! (heu, but long to code maybe…)

* GNU flex and bison for lexical analyser and grammar parser
* GNU make and gcc

Actually I moved to `python/` for a *not performance* oriented prototype.

### other derivative languages

Yes some other programming languages are also used.

* python
* ruby
* bash
* C++


## Unittesting
* GoogleTest for C
* bats for functional testing in bash
* py.test for python

## Usage - Example - goals at term

What will be achieved when working?

File: [examples/readme_ex0.sh](examples/readme_ex0.sh)

~~~bash
#!/bin/bash 
#
# libido: bash_code=bash(die, docopts)
#
# how to rebuild: rebuild this code with:
# $ libido examples/readme_ex0.sh

echo 'some code here'

# libido code will be included/ updated here
# libido: expand bash_code

echo 'some more code using die() and or docopts'
if [[ -z "$1" ]]
then
    die "missing argument1"
fi
exit 0
~~~

The first `libido:` tag tell the preprocessor that the bash script will use a external chunk of code, here 2 functions: `die` and `docopts,` written in bash.

The second occurrence, `libido: expand bash_code` will expand the parsed code in place just here. The name `bash_code`
is defined previously with the affectation.

Hey, how does libido nows where to find the snippet for die() and such?

In the libido.conf!

## libido.conf

`libido` can use a conf file to store config globally outside the source code. `libido.conf` looks like bash variable
assignment.

~~~
# some comment in libido.conf
remote_location=http://your.personal.me/git/somerepos.git
remote_project=somecode_lib
search_scan_offset=0
libido_keyword=libido
git_auto_commit=true
auto_inc_duplicate=true
auto_quote_string=always|nospace|protected_chars
disable_add_ref=false
~~~

## Command line

~~~
Usage: libido [OPTIONS] SOURCE_FILE ...

OPTIONS:
 -n          dry run
 -v          verbose
 -b=[suffix] backup with suffix (incremental backup)
 -r          revert?
 -e          export back marked piece of code
~~~

### exporting

Exporting is a way of collecting fresh crafted piece of code into your lib.

## libido syntax

Note: `open_marker` is `libido:` embeded in comment

* `libido_statement`: 'libido:' `libido_action`
* `libido_action`:
 * `VARIABLE` '=' `parser_name` `LIST`
 * 'expand' `VARIABLE`
* `parser_name`:
 * 'bash'
* `VARIABLE`: `[a-zA-Z_][a-zA-Z0-9_]*`
* `LIST`: '(' `VARIABLE`, ... ')'

### example of syntax
~~~
# libido: bash_code=bash(die, docopts)
~~~

`bash_code` is assigned with foreign code parsed with bash. Function collected are `die` and `docopts`

~~~
# libido: expand bash_code
~~~

expands `bash_code` here. comment is kept.
 

## Some references

### Lexical analyzer with flex
* [flex](http://flex.sourceforge.net/manual/Simple-Examples.html#Simple-Examples)
* [bison](https://www.gnu.org/software/bison/manual/html_node/index.html#SEC_Contents)


### Other preprocessor like program

* [m4](http://www.gnu.org/software/m4/m4.html) - macro preprocessor
* [cpp](http://gcc.gnu.org/onlinedocs/cpp/) - C preprocessor
* [sed](https://www.gnu.org/software/sed/manual/sed.html) - stream editor
* [gpp](http://en.nothingisreal.com/wiki/GPP) - general-purpose preprocessor

### template

* [mustache](https://mustache.github.io/mustache.5.html) - Templating JSON and preprocessor

### snipMate
Having snippet auto completable in code
* http://www.vim.org/scripts/script.php?script_id=2540 - vim snipMate
* https://github.com/garbas/vim-snipmate
