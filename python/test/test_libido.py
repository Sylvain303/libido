import sys
import configparser
import os


sys.path.append('..')
import libido


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
    from tempfile import NamedTemporaryFile
    code = string_of_code.split(';')
    tmp = NamedTemporaryFile(delete=False)
    tmp.write("\n".join(code))
    tmp.close()
    return tmp.name

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

    dest = loc + '/mylib.bash'
    assert os.path.dirname(dest) != os.path.realpath('.')
    # create lib
    os.remove(dest)

    f = write_tmp('#!/bin/bash\ndie() {;echo "you died";exit 1;}')
    l.parse_input(f)
    l.process_export(f)
    assert os.path.isfile(dest)
    os.remove(f)

    # update lib

