import sys
sys.path.append('..')

import parser_factory

def test_detect():
    conf = {'lib_source' : '../examples/libido/*'}
    fname = '../../examples/libido/shell_lib.bash'
    factory = parser_factory.parser_factory(conf)
    t = factory.detect(fname)

    assert t == 'bash'

def test_get_parser():
    conf = {'lib_source' : '../examples/libido/*'}
    fname = '../../examples/libido/shell_lib.bash'

    factory = parser_factory.parser_factory(conf)
    p = factory.get_parser(fname)

    assert p.name == 'bash'
