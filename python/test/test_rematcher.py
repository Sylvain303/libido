import sys
sys.path.append('..')

from rematcher import REMatcher

def test_REMatcher():
    l = 'some string'

    m = REMatcher(l)
    assert m.match(r'(some)')
    assert m.group(1) == 'some'

    assert m.all() == ('some',)
