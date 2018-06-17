"""
    Test the three different modes currently supported by `logexc`.
"""

from prettytb import logexc


def test_with_statement(capsys):
    with logexc():
        1/0

    err = capsys.readouterr().err
    assert err.find("1/0") != -1
    assert err.find("ZeroDivisionError") != -1
    assert err.find("capsys = ") != -1

def test_decorator(capsys):
    @logexc
    def errfunc():
        somevar = 1
        1/0
    errfunc()

    err = capsys.readouterr().err
    assert err.find("1/0") != -1
    assert err.find("ZeroDivisionError") != -1
    assert err.find("somevar = 1") != -1

def test_call(capsys):
    try:
        somevar = 1
        1/0
    except Exception as exc:
        logexc(exc)

    err = capsys.readouterr().err
    assert err.find("1/0") != -1
    assert err.find("ZeroDivisionError") != -1
    assert err.find("somevar = 1") != -1
    assert err.find("capsys = ") != -1
