from pytest import fixture
from entity_linking.wiki.api import WikidataApi
from entity_linking.wiki.entity import Entity


@fixture(scope="module")
def api():
    return WikidataApi()


@fixture(scope="module")
def token():
    return "Krzysztof Krawczyk"


@fixture(scope="module")
def pages():
    return [
        "Q1380592",
        "Q61780001",
        "Q11749406",
        "Q1790445"
    ]


@fixture(scope="module")
def entity(entity_id, token):
    return Entity(id=entity_id, token=token, instance_of=["Q5"], subclass_of=[], facet_of=[])


def test_get_pages(api, token, pages):
    assert api.get_pages(token=token) == pages


def test_get_entity_data(api, entity_id, entity):
    assert api.get_entity_data(entity_id) == entity
