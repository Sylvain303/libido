#
# libido_parser can only be created by parser_factory as it needs to be a singelton for all internal parser
#
import os
import pytest

import sys
sys.path.append('..')
# local lib
from libido_parser import libido_parser, symbol
import parser_factory
from py_test_helper import write_tmp, file_match
from helper import flat_line

def _find_examples():
    path = os.path.realpath('../../examples/libido/')
    assert os.path.isdir(path)
    return path + '/*'

def _create_factory(conf = None):
    if conf == None:
        # fake configparser
        conf = {'libido' : {'lib_source' : _find_examples()} }
    f = parser_factory.parser_factory(conf)
    return f

def _create_parser(conf = None):
    """
    _create_parser() : create the factory and get its libido_parser
    """
    if conf != None:
        f = _create_factory(conf)
    else:
        f = _create_factory()

    return f.libido_parser

def test__create_parser():
    p = _create_parser()
    # with have the good parser
    assert isinstance(p, libido_parser)

    assert p.parser_factory.libido_parser == p
    
    # create a bash_parser and ensure it has the same libido_parser as libido_parser property
    import glob
    f = glob.glob(p.config['lib_source'])[0]
    bp = p.parser_factory.get_parser(f)
    assert isinstance(bp, p.parser_factory.parsers['bash'])
    assert bp.libido_parser == p


def test_load_lib():
    p = _create_parser(conf={'libido' : {} })
    # raise if no config_location found
    with pytest.raises(RuntimeError):
        p.load_lib()

    p = _create_parser()
    r = p.load_lib()
    assert len(p.code_lib) > 0

    # with given input_list_to_parse
    input_fname = 'input.bash'
    p.parse(input_fname)

    # at this step, the only token is the var (functions name are not parsed by libido)
    assert p.token_map.keys() ==  [ 'allcode' ]
    assert len(p.code_lib) == 0

    # this call use the same parsed file as lib. Now a bash_parser will be create and the function parsed.
    r = p.load_lib(input_list_to_parse=[input_fname])
    assert len(p.code_lib) == 1
    # we have a Bash_parser in code_lib{} which have parsed input_fname
    assert p.code_lib[input_fname].parsed_filename == input_fname
    # ignore token that are not chunk (ex: var)
    chunk_names = filter(lambda k: p.token_map[k].tsym == 'chunk', p.token_map)
    assert len(chunk_names) == 3

def test_find_chunk():
    p = _create_parser()

    c = p.find_chunk('die')
    assert isinstance(c['lines'], list)
    for l in c['lines']:
        assert isinstance(l, str)
        assert l[-1] == '\n'
    assert c['start'] == 8

    assert p.find_chunk('di2') == None

def test_dump_result():
    p = _create_parser()
    p.parse('../../examples/readme_ex0.sh')
    out = p.dump_result()
    # TODO: could it be an instance of unicode?
    assert isinstance(out, str)

    # ensure no extra newline
    assert out[-1] == '\n'
    assert p.output[-1] == p.lines[-1]

    # can be run twice 
    out2 = p.dump_result()
    assert out == out2


def test_tokenize():
    """
    require REMatcher
    """
    from rematcher import REMatcher
    p = _create_parser()

    # triming REMatcher line is not tokenize()'s job

    t = p.tokenize(REMatcher('fail'))
    assert t == None

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

    t = p.tokenize(REMatcher('depend top_func(dep1, dep2)'))
    assert t.action == 'depend'
    assert t.what == 'top_func'
    assert t.args == ['dep1', 'dep2']

    # need a top_func def (may be later we could look next line?)
    t = p.tokenize(REMatcher('depend(die)'))
    assert t == None

    # export token
    t = p.tokenize(REMatcher('export(die)'))
    assert t.action == 'export'
    assert t.args == [ 'die' ]

    t = p.tokenize(REMatcher('export( you, and_me, and_tea, for2 )'))
    assert t.action == 'export'
    assert t.args == [ 'you', 'and_me', 'and_tea', 'for2' ]

def test_dependencies():
    from rematcher import REMatcher
    p = _create_parser()
    t = p.tokenize(REMatcher('depend top_func(dep1, dep2)'))

    p.add_dependency(t.what, t.args)

    assert t.what in p.token_map
    for dep in t.args:
        assert dep in p.token_map

    p.assign('all', "some some2".split())
    assert 'all' in p.token_map
    assert 'some' not in p.token_map

    # sub-paser can modify dependencies in the refering libido_parser
    #
    # the token is not here before, but if we call a sub-parser it will fill token_map{}
    assert 'one' not in p.token_map
    bp = p.parser_factory.get_parser(filename=None, type_parser='bash')
    # input.bash has dependencies internaly
    bp.parse('input.bash')
    for c in bp.get_chunk_keys():
        assert c in p.token_map

    # test dependancies in the libido_parser
    # libido.parse() has not been called, but bp.parse() must have called analyze_line during parse
    d = p.get_dep('three')
    assert sorted(d) == sorted(['one', 'two', 'three'])

    # analyze_line not called if dest_parser.ignore_libido_analyze = True
    p.reset_parser()
    bp.ignore_libido_analyze = True
    assert 'one' not in p.token_map
    bp.parse('input.bash')
    # still not here
    assert 'one' not in p.token_map
    # this wont work of course
    with pytest.raises(RuntimeError):
        d = p.get_dep('three')

def test_analyze_line():
    """
    require bash_parser, REMatcher
    """
    p = _create_parser()

    from bash_parser import Bash_parser
    from rematcher import REMatcher

    bp = p.parser_factory.get_parser(filename=None, type_parser='bash')
    bp.init_parser()

    bp.n = 10
    p.analyze_line(bp, REMatcher('verbatim (pipo){'))
    assert bp.chunks['pipo']['start'] == 10

    bp.n = 30
    p.analyze_line(bp, REMatcher('}'))
    assert bp.chunks['pipo']['end'] == 30

    assert bp.chunks == {'pipo' : {'start': 10, 'end' : 30 }}

def test_get_dep():
    p = _create_parser()
    p.token_map = {
            'code': symbol(tsym='var', deps=['three']),
            'die': symbol(tsym='chunk', deps=[]),
            'one': symbol(tsym='chunk', deps=[]),
            'test_tool': symbol(tsym='chunk', deps=['die']),
            'three': symbol(tsym='chunk', deps=['two']),
            'two': symbol(tsym='chunk', deps=['one'])
            }

    d = p.get_dep('three')
    assert sorted(d) == sorted(['one', 'two', 'three'])

    d = p.get_dep('three', not_me=True)
    assert sorted(d) == sorted(['one', 'two'])

    d = p.get_dep('code', not_me=True)
    assert sorted(d) == sorted(['one', 'two', 'three'])

    d = p.get_dep('die')
    assert d == ['die']

def test_resolve_dependancies():
    p = _create_parser()
    p.parse('in_with_dep.sh')

    # call twice, idempotence
    r1 = p.resolve_dependancies()
    r2 = p.resolve_dependancies()
    assert r1 == r2
# example of resolved_dep{}
# {
#  'code': ['three', 'two', 'one'],
#  'die': {'deps': ['die'],
#   'lines': ['die() {\n', '    echo "$*"\n', '    exit 1\n', '}\n'],
#   'start': 8},
#  'one': {'deps': ['one'],
#   'lines': ['one() {\n', '    echo "code for one"\n', '}\n'],
#   'start': 6},
#  'test_tool': {'deps': ['test_tool', 'die'],
#   'lines': ['test_tool() {\n',
#    '    local cmd=$1\n',
#    '    if type $cmd > /dev/null\n',
#    '    then\n',
#    '        # OK\n',
#    '        return 0\n',
#    '    else\n',
#    '        die "tool missing: $cmd"\n',
#    '    fi\n',
#    '}\n'],
#   'start': 15},
#  'three': {'deps': ['one', 'three', 'two'],
#   'lines': ['three() {\n', '    echo "code for three"\n', '    two\n', '}\n'],
#   'start': 19},
#  'two': {'deps': ['two', 'one'],
#   'lines': ['two() {\n',
#    '    for i in $(seq 1 2)\n',
#    '    do\n',
#    '        echo "two:$(one)"\n',
#    '    done\n',
#    '}\n'],
#   'start': 11}
#}

    # data structure format
    for k, data in p.resolved_dep.items():
        assert p.token_map.has_key(k)

    # auto resolve for exporting without using a library
    p.parse('for_exporting.bash')
    assert not p.token_map.has_key('myfunc')
    assert not p.token_map.has_key('func2')

    deps = p.resolve_dependancies(auto_parse_input=True)
    # the filename is also parsed as lib_source
    assert p.token_map.has_key('myfunc')
    assert p.token_map.has_key('func2')

def test_order_chunk():
    p = _create_parser()
    # populate with an known result
    p.parse('in_with_dep.sh')
    r1 = p.resolve_dependancies()
   
    list_d = "three one two".split()
    deps_three = r1['three']['deps']
           
def test_parse():
    p = _create_parser()
    stats = p.parse('in_with_dep.sh')
    assert stats['line_count'] > 0
    assert stats['libido'] > 0

def test_get_resolved_dep():
    p = _create_parser()
    p.parse('input.bash')
    r1 = p.resolve_dependancies(auto_parse_input=True)

    p.chunk_expanded = set()
    code = p.get_resolved_dep('two')

    # TODO: test without file write
    tmp = write_tmp(flat_line(code))
    assert file_match('^one\(\)', tmp)
    os.remove(tmp)

    
