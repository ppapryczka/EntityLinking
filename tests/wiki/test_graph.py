from pytest import fixture
from entity_linking.wiki.graph import GraphBuilder


@fixture(scope="module")
def graph_builder():
    return GraphBuilder()


def test_build_graph(graph_builder, entity_id):
    graph = graph_builder.build_graph(entity_id)
    assert False
