from pytest import raises
from entity_linking.grammar.analysis import Analysis, AnalysisError


def test_eq_other_lemma():
    lemma1 = "a"
    lemma2 = "b"
    tag = "c"
    add_info_1 = ["a"]
    add_info_2 = ["b"]
    analysis1 = Analysis(lemma=lemma1, tag=tag,
                         add_info_1=add_info_1, add_info_2=add_info_2)
    analysis2 = Analysis(lemma=lemma2, tag=tag,
                         add_info_1=add_info_1, add_info_2=add_info_2)

    assert not analysis1 == analysis2
    assert analysis1 != analysis2


def test_eq_other_tag():
    lemma = "a"
    tag1 = "b"
    tag2 = "c"
    add_info_1 = ["a"]
    add_info_2 = ["b"]
    analysis1 = Analysis(lemma=lemma, tag=tag1,
                         add_info_1=add_info_1, add_info_2=add_info_2)
    analysis2 = Analysis(lemma=lemma, tag=tag2,
                         add_info_1=add_info_1, add_info_2=add_info_2)

    assert not analysis1 == analysis2
    assert analysis1 != analysis2


def test_eq_other_add_info_1():
    lemma = "a"
    tag = "b"
    add_info_1_1 = ["c"]
    add_info_1_2 = ["a"]
    add_info_2 = ["b"]
    analysis1 = Analysis(lemma=lemma, tag=tag,
                         add_info_1=add_info_1_1, add_info_2=add_info_2)
    analysis2 = Analysis(lemma=lemma, tag=tag,
                         add_info_1=add_info_1_2, add_info_2=add_info_2)

    assert not analysis1 == analysis2
    assert analysis1 != analysis2


def test_eq_other_add_info_2():
    lemma = "a"
    tag = "b"
    add_info_1 = ["c"]
    add_info_2_1 = ["a"]
    add_info_2_2 = ["b"]
    analysis1 = Analysis(lemma=lemma, tag=tag,
                         add_info_1=add_info_1, add_info_2=add_info_2_1)
    analysis2 = Analysis(lemma=lemma, tag=tag,
                         add_info_1=add_info_1, add_info_2=add_info_2_2)

    assert not analysis1 == analysis2
    assert analysis1 != analysis2


def test_analysis_constructor():
    lemma = "a"
    tag = "b"
    add_info_1 = ["a"]
    add_info_2 = ["b"]
    analysis = Analysis(lemma=lemma, tag=tag,
                        add_info_1=add_info_1, add_info_2=add_info_2)
    assert analysis.get_lemma() == lemma
    assert analysis.get_tag() == tag
    assert analysis.get_add_info_1() == add_info_1


def test_from_analysis():
    word = "a"
    lemma = "a"
    tag = "b"
    add_info_1 = ["a"]
    add_info_2 = ["2"]
    analysis_tuple = (word, lemma, tag, add_info_1, add_info_2)
    analysis = Analysis.from_analysis(analysis=analysis_tuple)
    assert analysis.get_lemma() == lemma
    assert analysis.get_tag() == tag
    assert analysis.get_add_info_1() == add_info_1
    assert analysis.get_add_info_2() == add_info_2


def test_invalid_analysis_tuple():
    analysis_tuple = ("a", "b")
    with raises(AnalysisError):
        Analysis.from_analysis(analysis=analysis_tuple)
