"""
Module that contain functions design to deal with entities graphs.
"""
from typing import List

import networkx as nx
from wikidata.entity import EntityId

from entity_linking.utils import DISAMBIGUATION_PAGE, MAX_DEPTH_LEVEL, TARGET_ENTITIES
from entity_linking.wikdata_api import WikidataAPI


def create_graph_for_entity(
    entity: EntityId, wikidata_api: WikidataAPI, graph_levels: int = MAX_DEPTH_LEVEL
) -> nx.Graph():
    """
    Create directed graph for given ``entity``. Nodes are entity names.

    Args:
        entity: Name of entity, in format Q{Number}.
        graph_levels: Max graph levels. Default: MAX_DEPTH_LEVEL.
        wikidata_api: API to get data from wikidata.

    Returns:
        Graph for given ``entity``.
    """

    g = nx.DiGraph()

    this_level_entities = [entity]

    for depth in range(graph_levels):
        next_level_entities = []

        # iterate over this level entities
        for ent in this_level_entities:
            # omit DISAMBIGUATION_PAGE - it cause errors
            if ent == DISAMBIGUATION_PAGE:
                continue

            for instance_of in wikidata_api.get_subclasses_for_entity(EntityId(ent)):
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


def get_graph_score(g: nx.Graph, entity: EntityId) -> float:
    """
    Score graph using information about length of path.

    Args:
        g: Graph to score.
        entity: Entity which for was build graph.

    Returns:
        Score of ``g``.
    """
    nodes: List = list(g.nodes)
    results = []

    for target_e in TARGET_ENTITIES:
        if target_e in nodes:
            score = 0.0
            for x in nx.all_simple_paths(g, source=entity, target=target_e):
                score += 1.0 / len(x)
            results.append(score)

    return max(results)
