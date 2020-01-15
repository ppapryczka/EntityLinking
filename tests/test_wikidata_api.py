from entity_linking.wikidata_api import (
    get_data_for_given_entity,
    get_subclasses_for_entity_wikidata,
    get_pages_for_token_wikidata,
    get_wikidata_link_for_entity,
    WIKIDATA_URL,
)
from wikidata.entity import EntityId
from typing import Dict, Any, List
from .test_utils import TEST_ENTITY_1, TEST_ENTITY_2


def test_get_data_for_given_entity_1():
    data: Dict[str, Any] = get_data_for_given_entity(EntityId(TEST_ENTITY_1))
    assert data["title"] == TEST_ENTITY_1
    assert data["descriptions"] == [
        "miasto i gmina w województwie małopolskim",
        "city and urban gmina of Poland",
    ]
    assert data["labels"] == ["Nowy Targ", "Nowy Targ"]
    assert data["instance of"] == ["Q2616791"]


def test_get_data_for_given_entity_2():
    data: Dict[str, Any] = get_data_for_given_entity(EntityId(TEST_ENTITY_2))
    assert data["title"] == TEST_ENTITY_2
    assert data["descriptions"] == ["", "American blues and soul band"]
    assert data["labels"] == ["The Blues Brothers", "The Blues Brothers"]
    assert data["instance of"] == ["Q215380"]


def test_get_instance_of_for_entity():
    data: List = get_subclasses_for_entity_wikidata(EntityId(TEST_ENTITY_1))
    assert data == ["Q2616791"]


def test_get_pages_ids_for_given_token():
    pages: List = get_pages_for_token_wikidata("Nowy Targ")
    assert pages[0] == TEST_ENTITY_1


def test_get_wikidata_link_for_entity():
    url = get_wikidata_link_for_entity(TEST_ENTITY_1)
    assert url == f"{WIKIDATA_URL}/{TEST_ENTITY_1}"

