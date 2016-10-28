import sys
import configparser


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
    assert l.conf.get('libido', 'remote_location') == lib_source

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

def test_process_export():
    l = libido.libido({})
    l.load_config()
    l.init_factory()
    loc = l.ensure_remote_access()
    f = write_tmp('die() {;echo "you died";exit 1;}')
    l.parse_input(f)
    l.process_export(f)
