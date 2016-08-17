import sys
sys.path.append('..')

import libido_parser

def test_load_lib():
    conf = {'lib_source' : '../examples/libido/*'}
    p = libido_parser.libido_parser(conf, parser_factory=None)

    p.load_lib()

