from entity_linking.grammar.range import Range
import pytest


@pytest.fixture(scope="module")
def range():
    start = 0
    end = 1
    return Range(start=start, end=end)


def test_range_constructor():
    start = 0
    end = 1
    r = Range(start=start, end=end)
    assert r.start == start
    assert r.end == end


@pytest.mark.parametrize("different", [Range(1, 1), Range(0, 2)])
def test_not_equal(range, different):
    assert not range == different
    assert range != different


def test_equal(range):
    r1 = Range(start=range.start, end=range.end)
    assert r1 == range
    assert not r1 != range
