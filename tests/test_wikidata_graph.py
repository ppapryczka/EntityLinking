import networkx as nx
from entity_linking.graph_wikidata import create_graph_for_entity, check_if_target_entity_is_in_graph
from .test_utils import TEST_ENTITY_1, TEST_ENTITY_2, TEST_ENTITY_3
from wikidata.entity import EntityId
from entity_linking.wikidata_api import WikidataWebAPI

api = WikidataWebAPI()


def test_create_graph_for_entity_zero_level():
    g: nx.Graph = create_graph_for_entity(EntityId(TEST_ENTITY_1), api, 0)
    assert list(g.nodes()) == []


def test_create_graph_for_entity_one_level():
    expected_entity: str = "Q215380"
    g: nx.Graph = create_graph_for_entity(EntityId(TEST_ENTITY_2), api, 1)
    assert TEST_ENTITY_2 in list(g.nodes())
    assert expected_entity in list(g.nodes())


def test_check_if_target_entity_is_in_graph():
    g: nx.Graph = create_graph_for_entity(EntityId(TEST_ENTITY_3), api, 1)
    assert check_if_target_entity_is_in_graph(g)
