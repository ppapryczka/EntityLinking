"""
Module that contain functions design to deal with entities graphs.
"""
from typing import List

import networkx as nx
from wikidata.entity import EntityId

from entity_linking.database_api import WikidataAPI
from entity_linking.utils import DISAMBIGATION_PAGE, TARGET_ENTITIES

MAX_DEPTH_LEVEL = 5


def create_graph_for_entity(
    entity: EntityId, wikidata_API: WikidataAPI, graph_levels: int = MAX_DEPTH_LEVEL
) -> nx.Graph():
    """
    Create directed graph for given ``entity``. Nodes are entity names.

    Args:
        entity: Name of entity, in format Q{Number}.
        graph_levels: Max graph levels. Default: MAX_DEPTH_LEVEL.
    Returns:
        Graph for given ``entity``.
    """

    g = nx.DiGraph()

    this_level_entities = [entity]

    for depth in range(graph_levels):
        next_level_entities = []

        # iterate over this level entities
        for ent in this_level_entities:
            # omit DISAMBIGATION_PAGE - it cause errors
            if ent == DISAMBIGATION_PAGE:
                continue

            for instance_of in wikidata_API.get_subclasses_for_entity(ent):
                g.add_node(instance_of)
                g.add_edge(ent, instance_of)
                next_level_entities.append(instance_of)
        this_level_entities = next_level_entities

    return g


def check_if_target_entity_is_in_graph(g: nx.Graph) -> bool:
    """
    Check if any of target entities is in graph.

    Args:
        g: Entity graph.

    Returns:
        True if on of target entities is in graph, false instead.
    """
    nodes: List = list(g.nodes)
    for target_e in TARGET_ENTITIES:
        if target_e in nodes:
            return True

    return False


def get_graph_score(g: nx.Graph, entity: str) -> float:
    nodes: List = list(g.nodes)
    results = []

    for target_e in TARGET_ENTITIES:
        if target_e in nodes:
            score = 0.0
            for x in nx.all_simple_paths(g, source=entity, target=target_e):
                score += 1.0 / len(x)
            results.append(score)

    return max(results)


def get_graph_similarity(g1: nx.Graph, g2: nx.Graph) -> float:
    pass
