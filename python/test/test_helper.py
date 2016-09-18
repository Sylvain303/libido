import sys
sys.path.append('..')
from helper import printerr, quiet

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
