from pytest import fixture
from entity_linking.parser.stemmer import Stemmer


@fixture(scope='module')
def input_list():
    return [
        "zaginieni",
        "środę",
        # "rano",
        # "wyszli",
        # "z",
        # "domów",
        # "do",
        "szkoły",
        # "w",
        # "nowym",
        # "targu",
        # "gdzie",
        "przebywali",
        "godziny",
        # "jak",
        "informuje",
        "tygodnik",
        "podhalański",
        "ivan",
        # "już",
        "się",
        "odnalazł",
        "ale",
        "los",
        "mariusza",
        "gajdy",
        # "wciąż",
        "jest",
        "nieznany",
        "chłopcy",
        # "od",
        "chwili",
        "zaginięcia",
        "przebywali",
        # "razem",
        # "między",
        "innymi",
        # "zakopanem",
        # "mieli",
        "rozstać",
        # "czwartek",
    ]


@fixture(scope='module')
def output_list():
    return [
        "zaginiony",
        "środa",
        # "rano",
        # "wyszli",
        # "z",
        # "domów",
        # "do",
        "szkoła",
        # "w",
        # "nowym",
        # "targu",
        # "gdzie",
        "przebywać",
        "godzina",
        # "jak",
        "informować",
        "tygodnik",
        "podhalański",
        "ivan",
        # "już",
        "się",
        "odnaleźć",
        "ale",
        "los",
        "mariusz",
        "gajda",
        # "wciąż",
        "być",
        "znać",
        "chłopiec",
        # "od",
        "chwila",
        "zaginięcie",
        "przebywać",
        # "razem",
        # "między",
        "inny",
        # "zakopane",
        # "mieli",
        "rozstać",
        # "czwartek",
    ]


def test_stemmer(input_list, output_list):
    stemmer = Stemmer()
    assert len(input_list) == len(output_list)
    for (input_word, output_word) in zip(input_list, output_list):
        assert stemmer.stem(input_word) == output_word
        if input_word != output_word:
            print("{}->{}".format(input_word, output_word))
