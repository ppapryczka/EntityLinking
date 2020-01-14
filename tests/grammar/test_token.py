import pytest
from copy import copy
from entity_linking.grammar.analysis import AnalysisError
from entity_linking.grammar.token import Token
from entity_linking.grammar.range import Range
from entity_linking.grammar.analysis import Analysis


@pytest.fixture
def token():
    start = 0
    end = 1
    word = "test"
    lemma = "a"
    tag = "b"
    add_info_1 = ["1"]
    add_info_2 = ["2"]
    analysis_tuple = (word, lemma, tag, add_info_1, add_info_2)
    return Token.from_analysis(start=start, end=end, analysis=analysis_tuple)


def test_equal(token):
    token1 = Token.from_analysis(
        start=token.range.start,
        end=token.range.end,
        analysis=(token.word, token.analyses[0].lemma, token.analyses[0].tag,
                  token.analyses[0].add_info_1, token.analyses[0].add_info_2)
    )
    assert token == token1
    assert not token != token1


@pytest.mark.parametrize("different",
                         [
                             Token.from_analysis(
                                 1, 1, ("test", "a", "b", ["1"], ["2"])),
                             Token.from_analysis(
                                 0, 1, ("dom", "a", "b", ["1"], ["2"])),
                             Token.from_analysis(
                                 0, 1, ("test", "a", "c", ["1"], ["2"]))
                         ])
def test_not_equal(token, different):
    assert not token == different
    assert token != different


def test_invalid_analysis_tuple():
    start = 0
    end = 1
    analysis_tuple = ([], [])
    with pytest.raises(AnalysisError):
        Token.from_analysis(start=start, end=end, analysis=analysis_tuple)


def test_analysis_constructor():
    start = 0
    end = 1
    word = "test"
    lemma = "a"
    tag = "b"
    add_info_1 = ["1"]
    add_info_2 = ["2"]
    analysis_tuple = (word, lemma, tag, add_info_1, add_info_2)
    token = Token(start=start, end=end, analysis=analysis_tuple)
    assert token.range == Range(start=start, end=end)
    assert token.word == word
    assert len(token.analyses) == 1
    assert token.analyses[0] == Analysis.from_analysis(analysis=analysis_tuple)


def test_from_analysis():
    start = 0
    end = 1
    word = "test"
    lemma = "a"
    tag = "b"
    add_info_1 = ["1"]
    add_info_2 = ["2"]
    analysis_tuple = (word, lemma, tag, add_info_1, add_info_2)
    token = Token.from_analysis(start=start, end=end, analysis=analysis_tuple)
    assert token.range == Range(start=start, end=end)
    assert token.word == word
    assert len(token.analyses) == 1
    assert token.analyses[0] == Analysis.from_analysis(analysis_tuple)


def add_analysis_invalid_analysis_tuple(token):
    with pytest.raises(AnalysisError):
        token.add_analysis("a", "b")


def test_add_analysis(token):
    lemma = "c"
    tag = "d"
    add_info_1 = ["e"]
    add_info_2 = ["f"]
    analysis_tuple = ("a", lemma, tag, add_info_1, add_info_2)
    token.add_analysis(analysis_tuple)
    assert len(token.analyses) == 2
    assert token.analyses[1] == Analysis.from_analysis(analysis=analysis_tuple)
