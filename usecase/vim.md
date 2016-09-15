# libido inside vim

* complete your code
* export your code
* import in your code

## Examples

The examples suppose that you have a correcly configured `libido.conf`.
Referencing your own `lib_source` local or remote.

### Expansion in your code by parsing the code

Enter the text in your vim buffer (here bash):

~~~bash
# libido: expand die
~~~

and execute a vim function
(the current line is selected, if not the whole buffer is saved and parsed)

~~~vim
:Libido
~~~

add the code under the libido marker, as a modified buffer

~~~bash
die() {
    echo "$*"
    exit 1
}
~~~

Which represents the equivalent of:

* save the current buffer
* remember the path of a local (or remote) source code which contains the function `die()` (in this case the current
  code source is detected as `bash`)
* `:r the_code_containing_die` (or copy/paste)
* remove unwanted lines if any

### Expansion by issuing an `expand`

execute a vim function:

~~~vim
:Libido expand die
~~~

No code parsing, your current buffer `file_type` detection is automatic, expansion under the cursor.

~~~bash
die() {
    echo "$*"
    exit 1
}
~~~

### Export part of the buffer to `lib_source`

#### Visual selection

* select a portion of code
* run: `:Libido export`
* the code is exported, named with what detected in the parsed code (function's name, named chuck)
  * if no name is detected, a prompt will asks for.
* no modification in the buffer

#### Taged export

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

* run: `:Libido export`
* the code is exported to your configured `lib_source`
* no modification in the buffer
