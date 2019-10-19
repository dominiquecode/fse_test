import pytest


def fun():
    return 4


def test_function():
    assert fun() == 4, "la valeur retournée n'est pas un entier"


def test_zero_division():
    with pytest.raises(ZeroDivisionError):
        1 / 0
