import networkx as nx
from entity_linking.utils import TARGET_ENTITIES
from entity_linking.wikidata_api import get_instance_of_for_entity
from wikidata.entity import EntityId
from typing import List

"""
DRAW GRAPH
import matplotlib.pyplot as plt
"""


MAX_DEPTH_LEVEL = 5


def create_graph_for_entity(entity: EntityId, graph_levels: int = MAX_DEPTH_LEVEL) -> nx.Graph():
    """
    Create directed graph for given ``entity``. Nodes are entity names.

    Args:
        entity: Name of entity, in format Q{Number}.
        graph_levels: Max graph levels. Default: MAX_DEPTH_LEVEL.

    Returns:
        Graph for given ``entity``.
    """

    g = nx.DiGraph()
    g.add_node(entity)

    this_level_entities = [entity]

    for depth in range(graph_levels):
        next_level_entities = []

        # iterate over this level entities
        for ent in this_level_entities:
            for instance_of in get_instance_of_for_entity(ent):
                g.add_node(instance_of)
                g.add_edge(ent, instance_of)
                next_level_entities.append(instance_of)

        this_level_entities = next_level_entities

    """
    DRAW GRAPH
    nx.draw_kamada_kawai(g, with_labels=True, font_weight='bold', )
    plt.show()
    """
    return g


def check_if_target_entity_is_in_graph(g: nx.Graph) -> bool:
    nodes: List = list(g.nodes())
    for target_e in TARGET_ENTITIES:
        if target_e in nodes:
            return True

    return False

