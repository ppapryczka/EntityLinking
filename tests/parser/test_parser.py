from pytest import fixture
from morfeusz2 import Morfeusz
from entity_linking.parser.parser import Parser
from entity_linking.grammar.range import Range
from entity_linking.grammar.token import Token


@fixture(scope="module")
def parser():
    return Parser()


@fixture(scope="module")
def simple_analysis_word():
    return "11-latkowie"


@fixture(scope="module")
def simple_analysis_token():
    return Token.from_analysis(start=0, end=1, analysis=(
        '11-latkowie', '11-latek', 'subst:pl:nom.voc:m1', ['nazwa pospolita'], []))


@fixture(scope="module")
def double_analysis_word():
    return "Zaginieni"


@fixture(scope="module")
def double_analysis_token():
    token = Token.from_analysis(start=0, end=1, analysis=(
        'Zaginieni', 'zaginiony:a', 'adj:pl:nom.voc:m1:pos', [], []))
    token.add_analysis(('Zaginieni', 'zaginiony:s',
                        'subst:pl:nom.voc:m1', ['nazwa_pospolita'], []))
    return token


def test_analyse_text(parser):
    word = "tests"
    assert parser.analyse_text(word) == Morfeusz().analyse(word)


def test_parse_simple_analysis_word(parser, simple_analysis_token, simple_analysis_word):
    tokens = parser.parse_text(simple_analysis_word)
    assert len(tokens) == 1
    assert tokens[0] == simple_analysis_token


def test_parse_double_analysis_word(parser, double_analysis_word, double_analysis_token):
    tokens = parser.parse_text(double_analysis_word)
    assert len(tokens) == 1
    assert tokens[0] == double_analysis_token

def test_multiple_word_analysis(parser, double_analysis_token, double_analysis_word, simple_analysis_token, simple_analysis_word):
    tokens = parser.parse_text(double_analysis_word + ' ' + simple_analysis_word)
    assert len(tokens) == 2
    assert tokens[0] == double_analysis_token
    simple_analysis_token._range = Range(start=1, end=2)
    assert tokens[1] == simple_analysis_token
