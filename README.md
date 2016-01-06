# libido - handle your personal library of code

Make your own lib by merging pieces of code into your code.

What?

libido stand for maximizing your pleasure! => lib I do

libido is a smart text preprocessor/editor which modify inline your code!
By inserting comment (or not) with libido keyword you can expand/update some part of your code with your lovely crafted snipet.

OK, a kind of super sed, with a nice syntax to extract, fetch, update inline chunk of code. See bellow.

## Written in C

Old school programming. OK may be. But lightning fast!

* GNU flex and bison for lexical analyser and grammar parser
* GNU make and gcc

## Current feature
* UTF-8 support
* parse an external source to match code fragment (See [example](examples/libido/shell_lib.bash))
* COV 100 % (Code coverage with unittesting) unittesting is testing 100% of the code lines.

## Unittesting

## Usage

examples/readme_ex0.sh

~~~bash
#!/bin/bash 
#
# libido: bash_code=bash(die, docopts)
#
# Howto Rebuild: rebuild this code with:
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

The first `libido:` tag tell the preprocessor that the bash script will use a exteranl chunk of code, here 2 functions: die and docopts, written in bash.

The second occurence, `libido: expand bash_code` will expand the parsed code in place juste here. The name `bash_code` is defined previously with the affectation.

Hey, how does libido nows where to find the snipet for die() and such?

In the libido.conf!

## libido.conf

libido can use a conf file to store config globaly outside the sourcecode. libido.conf looks like bash variable assignment.

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

Usage: libido [OPTIONS] SOURCE_FILE ...

OPTIONS:
 -n          dry run
 -v          verbose
 -b=[suffix] backup with suffix (incremental backup)
 -r          revert?
 -e          export back marked piece of code

### exporting

exporting is a way of collecting fresh crafted piece of code into your lib.

## Lexical analyser with flex
* [flex](http://flex.sourceforge.net/manual/Simple-Examples.html#Simple-Examples)
* [bison](https://www.gnu.org/software/bison/manual/html_node/index.html#SEC_Contents)


## Other preprocessor like program

* [m4](http://www.gnu.org/software/m4/m4.html) - macro preprcessor
* [cpp](http://gcc.gnu.org/onlinedocs/cpp/) - C preprocessor
* [sed](https://www.gnu.org/software/sed/manual/sed.html) - stream editor
* [gpp](http://en.nothingisreal.com/wiki/GPP) - general-purpose preprocessor

## snipMate
Having snippet autocompletable in code
* http://www.vim.org/scripts/script.php?script_id=2540 - vim snipMate
* https://github.com/garbas/vim-snipmate
