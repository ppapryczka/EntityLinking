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


class TokenNode(StructuredNode):
    token = StringProperty(unique_index=True)

    # relations
    page = RelationshipTo('EntityNode', 'PAGE')


class EntityNode(StructuredNode):
    entity_id = StringProperty(unique_index=True)
    token = StringProperty(default="")

    # relations
    instance_of = RelationshipTo('EntityNode', 'IS_INSTANCE_OF')
    subclass_of = RelationshipTo('EntityNode', 'IS_SUBCLASS_OF')
    facet_of = RelationshipTo('EntityNode', 'IS_FACET_OF')


class GraphBuilder:
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379,
                 db_host: str = 'localhost', db_port: int = 7687):
        self._api = WikidataApi()
        self._redis = Redis(host=redis_host, port=redis_port, db=0)
        # omit DISAMBIGATION_PAGE - it cause errors
        self._save_entity_in_cache(entity_id=DISAMBIGATION_PAGE)
        db.set_connection("bolt://neo4j:test@{}:{}".format(db_host, db_port))

    def build_pages(self, token: str):
        logger.info("Building pages for token: {}".format(token))
        if not self._token_node_exists(token):
            token_node = TokenNode(token=token).save()
            pages: List[str] = WikidataApi.get_pages(token=token)
            for page in pages:
                self.build_and_save_graph(entity_id=page)
                self._connect_token_with_page(token_node=token_node, page=page)

            self._save_token_in_cache(token)

    def _token_node_exists(self, token: str) -> bool:
        if self._token_node_exists_in_redis(token):
            return True
        else:
            # save in redis
            exists: bool = self._token_node_exists_in_database(token)
            if exists:
                self._save_token_in_cache(token)

            return exists

    def _token_node_exists_in_redis(self, token: str) -> bool:
        return self._redis.exists(token)

    @classmethod
    def _token_node_exists_in_database(cls, token: str) -> bool:
        return TokenNode.nodes.get_or_none(token=token) is not None

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
                if self._entity_node_exists(ent):
                    continue

                entity = self.fetch_entity_data(ent)
                graph.append(entity)
                self._save_entity_in_cache(ent)

                next_level_entities.extend(entity.instance_of)
                next_level_entities.extend(entity.subclass_of)
                next_level_entities.extend(entity.facet_of)

            this_level_entities = next_level_entities

        return graph

    def _entity_node_exists(self, entity_id: str) -> bool:
        if self._entity_node_exists_in_redis(entity_id):
            return True
        else:
            # save in redis
            exists: bool = self._entity_node_exists_in_database(entity_id)
            if exists:
                self._save_entity_in_cache(entity_id)

            return exists

    def _entity_node_exists_in_redis(self, entity_id) -> bool:
        return self._redis.exists(entity_id)

    @classmethod
    def _entity_node_exists_in_database(cls, entity_id) -> bool:
        return EntityNode.nodes.get_or_none(entity_id=entity_id) is not None

    def _save_token_in_cache(self, token: str):
        self._redis.set(token, "")

    def _save_entity_in_cache(self, entity_id: str):
        self._redis.set(entity_id, "")

    def fetch_entity_data(self, entity_id: str) -> Entity:
        logger.info("Fetching data for: {}".format(entity_id))
        return self._api.get_entity_data(entity_id)

    @classmethod
    def _connect_token_with_page(cls, token_node: TokenNode, page: str):
        entity_node = EntityNode.nodes.get_or_none(entity_id=page)
        if entity_node:
            token_node.page.connect(entity_node)
            if token_node.page.is_connected(entity_node):
                logger.info("Connected token: {} with page: {}".format(token_node.token, page))
            else:
                logger.error("Failed to connect token: {} with page: {}".format(token_node.token, page))
        else:
            logger.error("Unknown page: {} for token: {}".format(page, token_node.token))

    def save_graph(self, entities: List[Entity]):
        nodes: List[EntityNode] = list()
        for entity in entities:
            nodes.append(self._save_node(entity))

        for entity, node in zip(entities, nodes):
            self._save_relations(entity=entity, node=node)

    def _save_node(self, entity: Entity) -> EntityNode:
        node = EntityNode(entity_id=entity.id, token=entity.token).save()
        logger.info("Saved node: {}".format(entity.id))
        return node

    def _save_relations(self, entity: Entity, node: EntityNode):
        self._save_instance_of_relations(entity=entity, node=node)
        self._save_subclass_of_relations(entity=entity, node=node)
        self._save_facet_of_relations(entity=entity, node=node)

    @classmethod
    def _save_instance_of_relations(cls, entity: Entity, node: EntityNode):
        for entity_id in entity.instance_of:
            superclass = EntityNode.nodes.get_or_none(entity_id=entity_id)
            if superclass:
                node.instance_of.connect(superclass)
                if node.instance_of.is_connected(superclass):
                    logger.info("Saved node: {} as instance of: {}".format(entity.id, superclass.entity_id))
                else:
                    logger.error("Failed to connect: {} as instance of: {}".format(entity.id, entity_id))
            else:
                logger.error("Unknown superclass: {} for entity: {}".format(entity_id, entity.id))

    @classmethod
    def _save_subclass_of_relations(cls, entity: Entity, node: EntityNode):
        for entity_id in entity.subclass_of:
            superclass = EntityNode.nodes.get_or_none(entity_id=entity_id)
            if superclass:
                node.subclass_of.connect(superclass)
                if node.subclass_of.is_connected(superclass):
                    logger.info("Saved node: {} as subclass of: {}".format(entity.id, superclass.entity_id))
                else:
                    logger.error("Failed to connect: {} as subclass of: {}".format(entity.id, entity_id))
            else:
                logger.error("Unknown superclass: {} for entity: {}".format(entity_id, entity.id))

    @classmethod
    def _save_facet_of_relations(cls, entity: Entity, node: EntityNode):
        for entity_id in entity.facet_of:
            superclass = EntityNode.nodes.get_or_none(entity_id=entity_id)
            if superclass:
                node.facet_of.connect(superclass)
                if node.facet_of.is_connected(superclass):
                    logger.info("Saved node: {} as facet of: {}".format(entity.id, superclass.entity_id))
                else:
                    logger.error("Failed to connect: {} as facet of of: {}".format(entity.id, entity_id))

            else:
                logger.error("Unknown superclass: {} for entity: {}".format(entity_id, entity.id))
