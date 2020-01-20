from typing import List
from termcolor import colored

from neomodel import db, StructuredNode, StringProperty, RelationshipTo
from redis import Redis

from entity_linking.maintenance.logger import get_logger
from entity_linking.wiki.api import WikidataApi
from entity_linking.wiki.entity import Entity

# Entity Wikimedia disambiguation page, this page go to entity Q30642 and Q11862829 - this cause errors
DISAMBIGATION_PAGE: str = "Q4167410"

logger = get_logger("entity_linking.wiki.graph")


class GraphEntity(StructuredNode):
    entity_id = StringProperty(unique_index=True)
    token = StringProperty(default="")

    # relations
    instance_of = RelationshipTo('GraphEntity', 'IS_INSTANCE_OF')
    subclass_of = RelationshipTo('GraphEntity', 'IS_SUBCLASS_OF')
    facet_of = RelationshipTo('GraphEntity', 'IS_FACET_OF')


class GraphBuilder:
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379,
                 db_host: str = 'localhost', db_port: int = 7687):
        self._api = WikidataApi()
        self._redis = Redis(host=redis_host, port=redis_port, db=0)
        # omit DISAMBIGATION_PAGE - it cause errors
        self._save_in_cache(entity_id=DISAMBIGATION_PAGE)
        db.set_connection("bolt://neo4j:test@{}:{}".format(db_host, db_port))

    def build_and_save_graph(self, entity_id: str):
        logger.info("Building graph for: {}".format(entity_id))
        graph: List[Entity] = self.build_graph(entity_id)
        logger.info("Saving graph for: {}".format(entity_id))
        self.save_graph(graph)

    def build_graph(self, entity_id: str) -> List[Entity]:
        graph: List[Entity] = list()

        this_level_entities = [entity_id]

        while this_level_entities:
            next_level_entities = []
            for ent in this_level_entities:
                if self._node_exists(ent):
                    continue

                entity = self.fetch_entity_data(ent)
                graph.append(entity)
                self._save_in_cache(ent)

                next_level_entities.extend(entity.instance_of)
                next_level_entities.extend(entity.subclass_of)
                next_level_entities.extend(entity.facet_of)

            this_level_entities = next_level_entities

        return graph

    def _node_exists(self, entity_id: str) -> bool:
        if self._node_exists_in_redis(entity_id):
            return True
        else:
            # save in redis
            exists: bool = self._node_exists_in_database(entity_id)
            if exists:
                self._save_in_cache(entity_id)

            return exists

    def _node_exists_in_redis(self, entity_id) -> bool:
        return self._redis.exists(entity_id)

    @classmethod
    def _node_exists_in_database(cls, entity_id) -> bool:
        return GraphEntity.nodes.get_or_none(entity_id=entity_id) is not None

    def _save_in_cache(self, entity_id: str):
        self._redis.set(entity_id, "")

    def fetch_entity_data(self, entity_id: str) -> Entity:
        logger.info("Fetching data for: {}".format(entity_id))
        return self._api.get_entity_data(entity_id)

    def save_graph(self, entities: List[Entity]):
        nodes: List[GraphEntity] = list()
        for entity in entities:
            nodes.append(self._save_node(entity))

        for entity, node in zip(entities, nodes):
            self._save_relations(entity=entity, node=node)

    def _save_node(self, entity: Entity) -> GraphEntity:
        node = GraphEntity(entity_id=entity.id, token=entity.token).save()
        logger.info("Saved node: {}".format(entity.id))
        return node

    def _save_relations(self, entity: Entity, node: GraphEntity):
        self._save_instance_of_relations(entity=entity, node=node)
        self._save_subclass_of_relations(entity=entity, node=node)
        self._save_facet_of_relations(entity=entity, node=node)

    @classmethod
    def _save_instance_of_relations(cls, entity: Entity, node: GraphEntity):
        for entity_id in entity.instance_of:
            superclass = GraphEntity.nodes.get_or_none(entity_id=entity_id)
            if superclass:
                node.instance_of.connect(superclass)
                if node.instance_of.is_connected(superclass):
                    logger.info("Saved node: {} as instance of: {}".format(entity.id, superclass.entity_id))
                else:
                    logger.error("Failed to connect: {} as instance of: {}".format(entity.id, entity_id))
            else:
                logger.error("Unknown superclass: {} for entity: {}".format(entity_id, entity.id))

    @classmethod
    def _save_subclass_of_relations(cls, entity: Entity, node: GraphEntity):
        for entity_id in entity.subclass_of:
            superclass = GraphEntity.nodes.get_or_none(entity_id=entity_id)
            if superclass:
                node.subclass_of.connect(superclass)
                if node.subclass_of.is_connected(superclass):
                    logger.info("Saved node: {} as subclass of: {}".format(entity.id, superclass.entity_id))
                else:
                    logger.error("Failed to connect: {} as subclass of: {}".format(entity.id, entity_id))
            else:
                logger.error("Unknown superclass: {} for entity: {}".format(entity_id, entity.id))

    @classmethod
    def _save_facet_of_relations(cls, entity: Entity, node: GraphEntity):
        for entity_id in entity.facet_of:
            superclass = GraphEntity.nodes.get_or_none(entity_id=entity_id)
            if superclass:
                node.facet_of.connect(superclass)
                if node.facet_of.is_connected(superclass):
                    logger.info("Saved node: {} as facet of: {}".format(entity.id, superclass.entity_id))
                else:
                    logger.error("Failed to connect: {} as facet of of: {}".format(entity.id, entity_id))

            else:
                logger.error("Unknown superclass: {} for entity: {}".format(entity_id, entity.id))
