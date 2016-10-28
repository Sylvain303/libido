import sys
sys.path.append('..')
from helper import printerr, quiet, flat_line

def test_printerr(capsys):
    assert quiet() == False
    printerr("pipo")
    out, err = capsys.readouterr()
    assert out == ''
    assert err == 'pipo\n'

    quiet(True)
    assert quiet() == True

    printerr("pipo2")
    out, err = capsys.readouterr()
    assert out == ''
    assert err == ''

    quiet(False)
    assert quiet() == False

    printerr("pipo3")
    out, err = capsys.readouterr()
    assert out == ''
    assert err == 'pipo3\n'

def test_flat_line():
    v = 'some text'
    r = flat_line(v)
    assert r == 'some text\n'

    # no double \n
    inlist = ['one\n', 'two\n', '\n']
    r = flat_line(inlist)
    assert r == 'one\ntwo\n\n'
