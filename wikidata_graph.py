from wikidata_api import get_instance_of_for_entity
from wikidata.entity import EntityId

'''
DRAW GRAPH
import matplotlib.pyplot as plt
'''

import networkx as nx

MAX_DEPTH_LEVEL = 3

def create_graph_for_entity(entity: EntityId) -> nx.Graph():
    """
    Create directed graph for given ``entity``. Nodes are entity names.

    Args:
        entity: Name of entity, in format Q{Number}.

    Returns:
        Graph for given ``entity``.
    """

    g = nx.DiGraph()
    g.add_node(entity)

    this_level_entities = [entity]

    for depth in range(MAX_DEPTH_LEVEL):
        next_level_entities = []

        # iterate over this level entities
        for ent in this_level_entities:
            for instance_of in get_instance_of_for_entity(ent):
                g.add_node(instance_of)
                g.add_edge(ent, instance_of)
                next_level_entities.append(instance_of)

        this_level_entities = next_level_entities

    '''
    DRAW GRAPH
    nx.draw_kamada_kawai(g, with_labels=True, font_weight='bold', )
    plt.show()
    '''
    return g


if __name__ == "__main__":
    import datetime
    now = datetime.datetime.now()
    create_graph_for_entity(EntityId("Q231593"))
    print(datetime.datetime.now() - now)
