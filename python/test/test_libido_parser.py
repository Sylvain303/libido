import os
import sys
sys.path.append('..')

import libido_parser
import parser_factory



def _find_examples():
    path = os.path.realpath('../../examples/libido/')
    assert os.path.isdir(path)
    return path + '/*'

def _create_factory():
    conf = {'lib_source' : _find_examples()}
    f = parser_factory.parser_factory(conf)
    return f

def test_load_lib():
    conf = {'lib_source' : _find_examples()}
    f = _create_factory()
    p = libido_parser.libido_parser(conf, parser_factory=f)

    r = p.load_lib()
    assert len(p.code_lib) > 0

def test_find_chunk():
    conf = {'lib_source' : _find_examples()}
    f = _create_factory()
    p = libido_parser.libido_parser(conf, parser_factory=f)

    c = p.find_chunk('die')
    assert isinstance(c, list)
    for l in c:
        assert isinstance(l, str)


