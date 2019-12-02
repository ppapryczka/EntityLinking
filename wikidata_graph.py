from wikidata_api import get_instance_of_for_entity
from wikidata.entity import EntityId
import matplotlib.pyplot as plt

import networkx as nx

MAX_DEPTH_LEVEL = 2

def create_graph_for_entity(entity: EntityId) -> nx.Graph():
    g = nx.DiGraph()
    g.add_node(entity)

    this_level_entities = [entity]
    for depth in range(MAX_DEPTH_LEVEL):
        next_level_entities = []

        # iterate over this level entities
        for ent in this_level_entities:
            if ent not in g:
                g.add_node(ent)

            for instance_of in get_instance_of_for_entity(ent):
                g.add_node(instance_of)
                g.add_edge(ent, instance_of)
                next_level_entities.append(instance_of)

        this_level_entities = next_level_entities


    nx.draw(g, with_labels=True, font_weight='bold')
    plt.show()


if __name__ == "__main__":
    create_graph_for_entity("Q231593")