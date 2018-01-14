
# bash_parser depends on libido_parser for parsing libido: statement
#
import os
import sys
sys.path.append('..')
from tempfile import NamedTemporaryFile

from bash_parser import Bash_parser
from py_test_helper import string_match

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
    filen = os.path.realpath('../../examples/libido/shell_lib.bash')
    r = p.parse(filen)
    assert len(p.chunks) > 0

    c = p.get_chunk('die')
    assert isinstance(c, list)
    assert c[0] == 'die() {\n'

    # ensure it is a copy array of line
    c[0] =  '#no more die'
    c2 = p.get_chunk('die')
    assert c2[0] == 'die() {\n'

    # used by update_chunk()
    p.new_chunk['die'] = 'die() {\necho pipo\n}\n'.split('\n')
    c3 = p.get_chunk('die')
    assert c3[0] == 'die() {'
    assert c3[1] == 'echo pipo'

    # force read the old chunk not the new one in new_chunk[]
    c4 = p.get_chunk('die', force_old=True)
    assert c2 == c4

    assert None == p.get_chunk('doesnt_exist')

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

    expect = {'one': symbol(tsym='chunk', deps=[]),
             'three': symbol(tsym='chunk', deps=['two']),
              'two': symbol(tsym='chunk', deps=['one'])}
    assert p.libido_parser.token_map == expect

def test_get_chunk_keys():
    p = _create_parser()
    p.parse('input.bash')

    assert len(p.get_chunk_keys()) == 3

    # compose and ordered list (same order as in input.bash)
    it = "one two three".split()
    i = 0
    for c in p.get_chunk_keys():
        assert c == it[i]
        i += 1

    # add a new chunks and check if its here
    p.new_chunk['pipo_one'] = [ 'fake' ]
    p.new_chunk['pipo_two'] = [ 'fake2' ]
    assert p.get_chunk_keys() == (it + [ 'pipo_one', 'pipo_two' ])

    # get ordered chunks with outsider_ keys at the good position
    p.identify_chunk_outsider()
    assert len(p.get_chunk_keys()) > 3
    expected = "one two three pipo_one pipo_two".split()
    assert p.get_chunk_keys() == expected

    expected = "outsider_1 one outsider_2 two outsider_3 three pipo_one pipo_two".split()
    assert len(expected) == 8
    assert p.get_chunk_keys(interleave_ousider=True) == expected


def test_identify_chunk_outsider():
    p = _create_parser()
    p.parse('input.bash')
    assert len(p.chunks) == 3
    p.identify_chunk_outsider()
    assert len(p.chunks) == 6

    # without function in the source
    parse_stat = p.parse('in_with_dep.sh')
    assert parse_stat['function'] == 0
    assert len(p.chunks) == 0
    p.identify_chunk_outsider()
    assert len(p.chunks) == 1
    assert len(p.get_chunk('outsider_1')) == parse_stat['line_count']

    # call twice
    p.identify_chunk_outsider()
    assert len(p.chunks) == 1
    assert len(p.get_chunk('outsider_1')) == parse_stat['line_count']

def test_write():
    p = _create_parser()
    # without func
    parse_stat = p.parse('in_with_dep.sh')
    assert parse_stat['function'] == 0

    # tmp is automatically deleted  on close
    tmp = NamedTemporaryFile()
    p.write(tmp.name)
    f = open(tmp.name)
    lines = f.readlines()
    assert p.lines == lines
    tmp.close()

def test_update_chunk():
    p = _create_parser()
    p.parse('for_exporting.bash')
    assert len(p.chunks) == 2

    code = p.get_chunk('func2')
    assert len(code) == 3

    # hack copy a func from another code
    p2 = _create_parser()
    p2.parse('input.bash')
    p2.chunks['func2'] = p2.chunks['one']

    p.update_chunk('func2', p2)
    assert p.chunks['func2']['updated']
    assert p.new_chunk['func2'] == p2.get_chunk('func2')

    # the code still contains one() not func2()
    assert p.new_chunk['func2'][0].startswith('one()')
    p.new_chunk['func2'][0] = p.new_chunk['func2'][0].replace('one()', 'func2()')

    # write updated
    tmp = NamedTemporaryFile()
    p.write(tmp.name)

    p3 = _create_parser()
    p3.parse(tmp.name)
    tmp.close()

    assert len(p3.chunks) == 2
    assert sorted(p3.chunks.keys()) == sorted(['myfunc', 'func2'])

    assert p3.get_chunk('func2')[1:] == p2.get_chunk('one')[1:]
    assert p.get_chunk('func2', force_old=True) != p3.get_chunk('func2')

    # add new chunk not present in p
    p4 = _create_parser()
    p4.parse('a_new_one.bash')
    p.update_chunk('a_new_one', p4)
    assert p.get_chunk('a_new_one')[0].startswith('a_new_one()')
    assert p.get_chunk('a_new_one', force_old=True) == None

# decorator py.test for capturing stdout testing
def test_print_chunks(capsys):
    p = _create_parser()
    p.parse('for_exporting.bash')

    import copy
    c1 = copy.deepcopy(p.chunks)

    p.identify_chunk_outsider()

    # ensure some content as been added to chunks{}
    assert len(c1.keys()) != len(p.chunks.keys())

    p.print_chunks(print_code=False)
    out, err = capsys.readouterr()
    assert string_match('myfunc', out)

