from entity_linking.grammar.range import Range

def test_range_constructor():
    start = 0
    end = 1
    r = Range(start=start, end=end)
    assert r.get_start() == start
    assert r.get_end() == end

def test_eq_other_start():
    start1 = 1
    start2 = 2
    end = 3
    r1 = Range(start=start1, end=end)
    r2 = Range(start=start2, end=end)
    assert not r1 == r2
    assert r1 != r2


def test_eq_other_end():
    start = 1
    end1 = 2
    end2 = 3
    r1 = Range(start=start, end=end1)
    r2 = Range(start=start, end=end2)
    assert not r1 == r2
    assert r1 != r2

def test_equal():
    start = 1
    end = 3
    r1 = Range(start=start, end=end)
    r2 = Range(start=start, end=end)
    assert r1 == r2
    assert not r1 != r2
