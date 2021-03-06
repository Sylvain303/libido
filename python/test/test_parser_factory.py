import sys
sys.path.append('..')

import parser_factory

def test_detect():
    # fake configparser in a dict
    conf = {'libido' :{'lib_source' : '../examples/libido/*'} }
    fname = '../../examples/libido/shell_lib.bash'
    factory = parser_factory.parser_factory(conf)
    t = factory.detect(fname)

    assert t == 'bash'

    fname = './extension_less_bash_test'
    t = factory.detect(fname)
    assert t == 'bash'

def test_get_parser():
    conf = {'libido' :{'lib_source' : '../examples/libido/*'} }
    fname = '../../examples/libido/shell_lib.bash'

    factory = parser_factory.parser_factory(conf)
    p = factory.get_parser(fname)

    assert p.name == 'bash'

    # pass parser type directly
    p = factory.get_parser(filename=None, type_parser='bash')
    assert p.name == 'bash'

    # same libido_parser for all parser
    lp = factory.libido_parser
    assert p.libido_parser == lp

