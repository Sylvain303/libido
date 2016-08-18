import os
import sys
sys.path.append('..')

from bash_parser import Bash_parser

def test_get_chunk():
    filen = os.path.realpath('../../examples/libido/shell_lib.bash')
    conf = {}
    p = Bash_parser(conf, parser_factory=None)

    r = p.parse(filen)
    assert len(p.chunks) > 0

    c = p.get_chunk(p.chunks['die'])
    assert isinstance(c, list)
    assert c[0] == 'die() {'

