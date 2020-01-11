from pytest import raises, fixture
from copy import copy
from entity_linking.grammar.analysis import AnalysisError
from entity_linking.grammar.token import Token
from entity_linking.grammar.range import Range
from entity_linking.grammar.analysis import Analysis


@fixture
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


def test_eq_token(token):
    token1 = Token.from_analysis(
        start=token.get_range().get_start(),
        end=token.get_range().get_end(),
        analysis=(token.get_word(), token.get_analyses()[0].get_lemma(), token.get_analyses()[0].get_tag(), token.get_analyses()[0].get_add_info_1(), token.get_analyses()[0].get_add_info_2())
    )
    assert token == token1
    assert not token != token1

def test_ne_token_other_range(token):
    token1 = Token.from_analysis(
        start=token.get_range().get_start(),
        end=token.get_range().get_end()+1,
        analysis=(token.get_word(), token.get_analyses()[0].get_lemma(), token.get_analyses()[0].get_tag(), token.get_analyses()[0].get_add_info_1(), token.get_analyses()[0].get_add_info_2())
    )
    assert not token == token1
    assert token != token1

def test_ne_token_other_word(token):
    token1 = Token.from_analysis(
        start=token.get_range().get_start(),
        end=token.get_range().get_end(),
        analysis=(token.get_word()+"a", token.get_analyses()[0].get_lemma(), token.get_analyses()[0].get_tag(), token.get_analyses()[0].get_add_info_1(), token.get_analyses()[0].get_add_info_2())
    )
    assert not token == token1
    assert token != token1

def test_ne_token_other_analysis(token):
    token1 = Token.from_analysis(
        start=token.get_range().get_start(),
        end=token.get_range().get_end(),
        analysis=(token.get_word(), token.get_analyses()[0].get_lemma()+"a", token.get_analyses()[0].get_tag(), token.get_analyses()[0].get_add_info_1(), token.get_analyses()[0].get_add_info_2())
    )
    assert not token == token1
    assert token != token1


def test_invalid_analysis_tuple():
    start = 0
    end = 1
    analysis_tuple = ([], [])
    with raises(AnalysisError):
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
    assert token.get_range() == Range(start=start, end=end)
    assert token.get_word() == word
    analyses = token.get_analyses()
    assert len(analyses) == 1
    assert analyses[0] == Analysis.from_analysis(analysis=analysis_tuple)


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
    assert token.get_range() == Range(start=start, end=end)
    assert token.get_word() == word
    analyses = token.get_analyses()
    assert len(analyses) == 1
    assert analyses[0] == Analysis.from_analysis(analysis_tuple)


def add_analysis_invalid_analysis_tuple(token):
    with raises(AnalysisError):
        token.add_analysis("a", "b")


def test_add_analysis(token):
    lemma = "c"
    tag = "d"
    add_info_1 = ["e"]
    add_info_2 = ["f"]
    analysis_tuple = ("a", lemma, tag, add_info_1, add_info_2)
    token.add_analysis(analysis_tuple)
    analyses = token.get_analyses()
    assert len(analyses) == 2
    assert analyses[1] == Analysis.from_analysis(analysis=analysis_tuple)
