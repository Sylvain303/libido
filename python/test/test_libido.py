from __future__ import print_function
import sys
import configparser
import os
import re

sys.path.append('..')
import libido

def file_match(pattern, filename):
    """
    file_match() : search regexp pattern in file content, stop at first match
    """
    content = open(filename,'r').readlines()
    reg = re.compile(pattern)
    for i, line in enumerate(content):
        if reg.search(line):
            return True

    return False

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

def write_tmp(string_of_code):
    """
    write_tmp(): create a temporary file handling the code in the string
                 auto remove #!shebang indent if any, if input is multiline
    return : the filename generated
    """
    from tempfile import NamedTemporaryFile
    code = []
    s = None
    for i, l in enumerate(string_of_code.split("\n")):
        if len(code) == 0:
            m = re.search(r'^(\s*)#!/bin/bash', l)
            if m:
                # we found the indent
                s = re.compile('^' + m.group(1))

            if l == "":
                # remove first emply lines
                continue

        # no more empty line, we add the code
        if s:
            l = s.sub('', l)
        code.append(l)


    tmp = NamedTemporaryFile(delete=False)
    tmp.write("\n".join(code))
    tmp.close()
    return tmp.name

def remove_file(fname):
    try:
        os.remove(fname)
    except OSError:
        pass

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
    remove_file(dest)

    # create lib:
    f = write_tmp("""
    #!/bin/bash
    die() {
        echo "you died"
        exit 1
    }
    some_func() {
        echo "param $1"
    }
    """)
    l.parse_input(f)
    l.process_export(f)
    assert os.path.isfile(dest)
    # cleanup input file
    os.remove(f)

    # update the lib
    # assert old code is still here
    assert file_match('you died"$', dest)
    assert file_match('^some_func', dest)

    f = write_tmp("""
    #!/bin/bash
    die() {
        echo "you died also here"
        exit 1
    }
    """)
    l.parse_input(f)
    l.process_export(f)

    # check exported functions in the local repos
    assert file_match("you died also here", f)
    assert file_match('^some_func', dest)

    # assert old code no more here
    assert not file_match('you died"$', dest)
    os.remove(f)

    f = write_tmp("""
    #!/bin/bash
    die() {
        echo "you died"
        exit 1
    }
    some_func() {
        echo "param $1"
    }
    """)
    only = [ 'some*', 'di' ]
    os.remove(dest)
    l.process_export(f, only)
    assert not file_match("^die\(\)", dest)
    assert file_match('^some_func', dest)
    os.remove(f)

    f = './input.bash'
    l.parse_input(f)
    l.process_export(f, ['three'])
    assert file_match('^three', dest)

