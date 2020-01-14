import pytest
from entity_linking.grammar.analysis import Analysis, AnalysisError


@pytest.fixture(scope="module")
def analysis():
    lemma = "a"
    tag = "b"
    add_info_1 = ["a"]
    add_info_2 = ["b"]
    return Analysis(lemma=lemma, tag=tag,
                    add_info_1=add_info_1, add_info_2=add_info_2)


@pytest.mark.parametrize("different",
             [Analysis("b", "b", ["a"], ["b"]),
              Analysis("a", "c", ["a"], ["b"]),
              Analysis("a", "b", ["b"], ["b"]),
              Analysis("a", "b", ["a"], ["c"])
              ])
def test_not_equal(analysis, different):
    assert not analysis == different
    assert analysis != different


def test_equal(analysis):
    analysis1 = Analysis(analysis.lemma, analysis.tag,
                         analysis.add_info_1, analysis.add_info_2)
    assert analysis == analysis1
    assert not analysis != analysis1


def test_analysis_constructor():
    lemma = "a"
    tag = "b"
    add_info_1 = ["a"]
    add_info_2 = ["b"]
    analysis = Analysis(lemma=lemma, tag=tag,
                        add_info_1=add_info_1, add_info_2=add_info_2)
    assert analysis.lemma == lemma
    assert analysis.tag == tag
    assert analysis.add_info_1 == add_info_1
    assert analysis.add_info_2 == add_info_2


def test_from_analysis():
    word = "a"
    lemma = "a"
    tag = "b"
    add_info_1 = ["a"]
    add_info_2 = ["2"]
    analysis_tuple = (word, lemma, tag, add_info_1, add_info_2)
    analysis = Analysis.from_analysis(analysis=analysis_tuple)
    assert analysis.lemma == lemma
    assert analysis.tag == tag
    assert analysis.add_info_1 == add_info_1
    assert analysis.add_info_2 == add_info_2


def test_invalid_analysis_tuple():
    analysis_tuple = ("a", "b")
    with pytest.raises(AnalysisError):
        Analysis.from_analysis(analysis=analysis_tuple)
