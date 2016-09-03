#
# bash_parser depends on libido_parser for parsing libido: statement
#
import os
import sys
sys.path.append('..')

from bash_parser import Bash_parser

filen = os.path.realpath('../../examples/libido/shell_lib.bash')

class fake_libido_parser:
    def __init__(self):
        self.token_map = {}

    def analyze_line(self, bash_parser, rematcher):
        pass

def _create_parser(libido_parser = None):
    conf = {}
    if libido_parser:
        p = Bash_parser(conf, libido_parser=libido_parser)
    else:
        p = Bash_parser(conf, libido_parser=fake_libido_parser())

    return p

def test_get_chunk():
    p = _create_parser()
    r = p.parse(filen)
    assert len(p.chunks) > 0

    c = p.get_chunk(p.chunks['die'])
    assert isinstance(c, list)
    assert c[0] == 'die() {\n'


def test_verbatim_start_and_end():
    p = _create_parser()
    p.init_parser()
    p.verbatim_start('code')

    assert p.chunks['code']['start'] == 0
    assert p.verbatim == 'code'
    assert p.collect 

    p.verbatim_end()

    assert p.chunks['code']['end'] == 0
    assert p.verbatim == None
    assert not p.collect 

def test_dependencies():
    # we need a real libido_parser for that
    from libido_parser import libido_parser, symbol
    lp = libido_parser(config={}, parser_factory=None)

    p = _create_parser(lp)
    p.parse('input.bash')

    expect = {'one': symbol(var=False, chunk=True, deps=[]),
             'three': symbol(var=False, chunk=True, deps=['two']),
              'two': symbol(var=False, chunk=True, deps=['one'])}
    assert p.libido_parser.token_map == expect 
