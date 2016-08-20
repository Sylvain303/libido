import os
import sys
sys.path.append('..')

import libido_parser
import parser_factory
import pytest

def _find_examples():
    path = os.path.realpath('../../examples/libido/')
    assert os.path.isdir(path)
    return path + '/*'

def _create_factory(conf = None):
    if conf == None:
        conf = {'lib_source' : _find_examples()}
    f = parser_factory.parser_factory(conf)
    return f

def _create_parser(conf = None):
    if conf == None:
        conf = {'lib_source' : _find_examples()}
    f = _create_factory(conf)
    return libido_parser.libido_parser(conf, parser_factory=f)

def test_load_lib():
    p = _create_parser(conf={})
    # raise if no config_location found
    with pytest.raises(RuntimeError):
        p.load_lib()

    p = _create_parser()
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
        assert l[-1] == '\n'

def test_resolve_assignement():
    p = _create_parser()
    p.parse('../../examples/readme_ex0.sh')
    p.resolve_assignement()

    assert len(p.chunks_resolved) > 0
    assert len(p.chunks_resolved['bash_code']) > 1

    p.resolve_assignement()
    assert len(p.chunks_resolved['bash_code']) > 1


def test_dump_result():
    p = _create_parser()
    p.parse('../../examples/readme_ex0.sh')
    out = p.dump_result()
    assert isinstance(out, str)

    # ensure no extra newline
    assert out[-1] == '\n'
    assert p.output[-1] == p.lines[-1]

    # can be run twice 
    out2 = p.dump_result()
    assert out == out2

def test_flat_line():
    v = 'some text'
    r = libido_parser.flat_line(v)
    assert r == 'some text\n'

def test_tokenize():
    """
    require REMatcher
    """
    from rematcher import REMatcher
    p = _create_parser()

    t = p.tokenize(REMatcher('fail'))
    assert t == None

    # triming REMatcher line is not tokenize()'s job
    t = p.tokenize(REMatcher('depend(die)'))
    assert t.action == 'depend'
    assert t.args[0] == 'die'

    t = p.tokenize(REMatcher('somevar=parser_here(die, something)'))
    assert t.action == 'assign'
    assert t.args == [ 'die', 'something' ]
    assert t.parser == 'parser_here'

    # inside parsing triming, OK
    t2 = p.tokenize(REMatcher('somevar = parser_here (  die  ,   something  )'))
    # same thing
    assert t == t2

    t = p.tokenize(REMatcher('expand  somevar '))
    assert t.action == 'expand'
    assert t.args == 'somevar'

def test_analyze_line():
    """
    require bash_parser, REMatcher
    """
    p = _create_parser()

    from bash_parser import Bash_parser
    from rematcher import REMatcher

    bp = Bash_parser(p.config, p.parser_factory)
    bp.init_parser()

    bp.n = 10
    p.analyze_line(bp, REMatcher('verbatim (pipo){'))
    assert bp.chunks['pipo']['start'] == 10

    bp.n = 30
    p.analyze_line(bp, REMatcher('}'))
    assert bp.chunks['pipo']['end'] == 30

    assert bp.chunks == {'pipo' : {'start': 10, 'end' : 30 }}
