import os
import sys
sys.path.append('..')

import libido


def test_readconfig():
    l = libido.libido({})
    config_file = './libido.conf'

    conf = l.readconfig(config_file)
    assert isinstance(conf, dict)
    assert conf.get('lib_source')

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

