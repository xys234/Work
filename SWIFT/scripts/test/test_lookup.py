import pytest
from services.data_service import Lookup


def test_lookup_unequal_length_inputs():

    # invalid inputs, unequal length inputs
    x, y = [1, 2, 3], [7, 4]
    name = 'case1'
    with pytest.raises(ValueError):
        Lookup(x, y, name)


def test_lookup_exact():
    x, y = [3, 1, 2], [7, 4, 5]
    name = 'case2'
    lk = Lookup(x, y, name)
    assert lk.lookup(0, True) is None
    assert lk.lookup(1, True)[1] == 4
    assert lk.lookup(2, True)[1] == 5
    assert lk.lookup(3, True)[1] == 7
    assert lk.lookup(4, True) is None


def test_lookup_approx():
    x, y = [3, 1, 2], [7, 4, 5]
    name = 'case3'
    lk = Lookup(x, y, name)
    assert lk.lookup(0, False) == (0, 4)
    assert lk.lookup(1, False) == (1, 4)
    assert lk.lookup(2, False) == (2, 5)
    assert lk.lookup(3, False) == (3, 7)
    assert lk.lookup(4, False) == (4, 7)


def test_lookup_interp():
    x, y = [3, 1, 4], [6, 3, 7]
    name = 'case4'
    lk = Lookup(x, y, name)
    assert lk.lookup(2, False) == (2, 4.5)


if __name__ == '__main__':
    pass