import pytest


@pytest.mark.parametrize('value, result', [(1, True), (0, False)])
def test_spoof_true(return_true, value, result):
    assert return_true is True
    assert bool(value) == (return_true and result)


@pytest.mark.parametrize('value, result', [(1, True), (0, False)])
def test_spoof_false(return_false, value, result):
    assert return_false is False
    assert bool(value) == return_false or result
