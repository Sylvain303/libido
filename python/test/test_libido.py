from __future__ import print_function
import sys
import configparser
import os
import re

sys.path.append('..')
import libido
from py_test_helper import file_match, write_tmp, remove_file

def test_readconfig():
    l = libido.libido({})
    config_file = './libido.conf'

    conf = l.readconfig(config_file)
    assert isinstance(conf, dict)
    assert conf.get('lib_source')

def test_load_config():
    l = libido.libido({})
    l.load_config()
    assert isinstance(l.conf,configparser.ConfigParser)
    lib_source = l.conf.get('libido', 'lib_source')
    assert lib_source
    # test against a local folder in test/
    assert l.conf.get('libido', 'remote_location') == './remote_location'

def test_get_usage():
    out = libido.get_usage()
    assert out == ''

    out = libido.get_usage(filename='../libido.py')
    assert out != ''
    lines = out.split('\n')
    assert len(lines) > 0
    assert lines[0].startswith('Usage:')

    # same thing
    assert lines[-1] == ''
    assert out[-1] == '\n'

    assert lines[-2].find('__future__') == -1


def test_ensure_remote_access():
    l = libido.libido({})
    l.load_config()
    assert l.conf['libido'].get('remote_location') == './remote_location'

    loc = l.ensure_remote_access()

    pwd = os.path.realpath('.')
    assert l.remote_location == pwd + '/remote_location'

def test_process_export():
    l = libido.libido({})
    l.load_config()
    l.init_factory()
    loc = l.ensure_remote_access()

    # mylib.bash is defined in libido.conf
    # remote_project=mylib.%s
    # TODO: get it from the libido configparser class
    dest = loc + '/mylib.bash'
    assert os.path.dirname(dest) != os.path.realpath('.')

    # force to create lib for storing libido exported content
    # so we create it first (also it can exists before the test)
    remove_file(dest)

    # create lib:
    tmpinput_fname = write_tmp("""
    #!/bin/bash
    die() {
        echo "you died"
        exit 1
    }
    some_func() {
        echo "param $1"
    }
    """)
    l.parse_input(tmpinput_fname)
    l.process_export(tmpinput_fname)
    assert os.path.isfile(dest)
    assert file_match('^die', dest)
    assert file_match('^some_func', dest)
    # cleanup input file
    os.remove(tmpinput_fname)

    # update the lib, we change the code of die()
    tmpinput_fname = write_tmp("""
    #!/bin/bash
    die() {
        echo "you died also here"
        exit 1
    }
    """)
    l.parse_input(tmpinput_fname)
    l.process_export(tmpinput_fname)

    # check exported functions in the local repos
    assert file_match("you died also here", tmpinput_fname)
    assert file_match('^some_func', dest)

    # assert old code no more here
    assert not file_match('you died"$', dest)
    os.remove(tmpinput_fname)

    # only add more functions, functions already in dest should stay
    tmpinput_fname = write_tmp("""
    #!/bin/bash
    #die() {
    #    echo "you died"
    #    exit 1
    #}
    more_func() {
        echo "param $1"
    }
    """)
    l.parse_input(tmpinput_fname)
    l.process_export(tmpinput_fname)
    for fn in "die some_func more_func".split():
        assert file_match("^%s\(\)" % fn, dest)
    os.remove(tmpinput_fname)

    # partial import select by glob pattern
    tmpinput_fname = write_tmp("""
    #!/bin/bash
    die() {
        echo "you died with another exit code"
        exit 2
    }
    some_func() {
        echo "param $1"
    }
    """)

    # "di" must not match as glob pattern on "die"
    only = [ 'some*', 'di' ]

    # we recreate the lib
    os.remove(dest)

    l.parse_input(tmpinput_fname)
    l.process_export(tmpinput_fname, only)
    assert not file_match("^die\(\)", dest)
    assert file_match('^some_func', dest)
    os.remove(tmpinput_fname)

    # import more code into the lib (three depends on two + one) should be
    # imported too.
    input_fname = './input.bash'
    l.parse_input(input_fname)
    # export all (no export statement in input.bash)
    l.process_export(input_fname)
    for fn in "three some_func two one".split():
        assert file_match("^%s\(\)" % fn, dest)
    # TODO: add filtering with only to see if dependencies are respected

    # TODO: the following bloc is sensing code, remove an perform correct test arround process_export()
    #
    # Test: import with an `export` statement inside the inputfile.
    # reset our library, it should contain only the exported chunks
    os.remove(dest)

    input_fname = './for_exporting.bash'
    l.parse_input(input_fname)
    # only resolve with parsed input not using any lib. The remote_location is to be modified.
    deps = l.lparser.resolve_dependancies(auto_parse_input=True)
    l.process_export(input_fname)
    for fn in "myfunc func2".split():
        assert file_match("^%s\(\)" % fn, dest)


def test_expand_chunk_names():
    l = libido.libido({})
    chunk_names = """
    pipo
    pipo_molo
    molo
    myfunc
    die
    did_it_again
    """.split()

    assert len(chunk_names) == 6

    l.load_config()
    # create lparser object
    l.init_factory()
    # fake assign self dependancies in libido_parser.token_map{}, used by get_dep() in expand_chunk_names()
    for chunk_name in chunk_names:
        l.lparser.add_dependency(chunk_name, [ chunk_name ])

    # start collecting chunk_names
    collector = []
    r = l.expand_chunk_names(chunk_names, 'm*', collector)
    assert r == True
    assert collector == ['molo', 'myfunc' ]

    # add more names
    assert l.expand_chunk_names(chunk_names, 'die', collector)
    assert collector == ['molo', 'myfunc', 'die' ]

    # unexistant pattern
    assert False == l.expand_chunk_names(chunk_names, 'not_found', collector)
    # collector unchanged
    assert collector == ['molo', 'myfunc', 'die' ]

    # add all (order is kept but as the collector was filled before)
    assert l.expand_chunk_names(chunk_names, '*', collector)
    assert collector == ['molo', 'myfunc', 'die', 'pipo', 'pipo_molo', 'did_it_again']

    # all with a new empty collector
    collector2 = []
    assert l.expand_chunk_names(chunk_names, '*', collector2)
    # in same order
    assert collector2 == chunk_names
    # called twice, all found, but not modified
    assert l.expand_chunk_names(chunk_names, '*', collector2)
    assert collector2 == chunk_names

    # collect with dependancies
    # before
    collector3 = []
    assert l.expand_chunk_names(chunk_names, 'molo', collector3)
    assert collector3 == ['molo']

    # add some dependencies
    l.lparser.add_dependency('molo', ['pipo', 'pipo_molo'])
    collector3 = []
    assert l.expand_chunk_names(chunk_names, 'molo', collector3)
    assert sorted(collector3) == sorted(['molo', 'pipo', 'pipo_molo'])


