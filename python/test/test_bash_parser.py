import os
import sys
sys.path.append('..')

from bash_parser import Bash_parser

filen = os.path.realpath('../../examples/libido/shell_lib.bash')

def _create_parser():
    conf = {}
    p = Bash_parser(conf, parser_factory=None)
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

