from typing import List
from termcolor import colored

from neomodel import db, StructuredNode, StringProperty, RelationshipTo, BooleanProperty
from redis import Redis

from entity_linking.maintenance.logger import get_logger
from entity_linking.wiki.api import WikidataApi
from entity_linking.wiki.entity import Entity

TARGET_ENTITIES = [
    "Q5",
    "Q2221906",
    "Q11862829",
    "Q4936952",
    "Q12737077",
    "Q29048322"
    "Q811430",
    "Q47461344",
    "Q6999",
    "Q11460",
    "Q16521",
    "Q24334685",
    "Q31629",
    "Q28855038",
    "Q11435",
    "Q28108",
    "Q16334298",
    "Q43460564",
    "Q732577",
    "Q271669",
    "Q34770",
    "Q2198779",
    "Q20719696",
    "Q15621286",
    "Q39546",
    "Q7239",
    "Q2095",
]
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
    qualified = BooleanProperty(default=False)

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
                graph = self.build_graph(entity_id=page)
                if graph:
                    self._connect_token_with_page(token_node=token_node, page=graph)

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

    @classmethod
    def _get_entity_node(cls, entity_id) -> EntityNode:
        return EntityNode.nodes.get_or_none(entity_id=entity_id)

    @classmethod
    def _is_target_entity(cls, entity_id) -> bool:
        return entity_id in TARGET_ENTITIES

    def _build_instance_of_entities(self, child: EntityNode, entities: List[str]):
        for instance_of in entities:
            parent: EntityNode = self._build_entity_node(entity_id=instance_of)
            if parent:
                child.qualified = child.qualified or parent.qualified
                child.save()
                self._save_instance_of_relation(entity_from=child, entity_to=parent)
            else:
                logger.error("Unexpected error while building entity: {}".format(instance_of))

    def _build_subclass_of_entities(self, child: EntityNode, entities: List[str]):
        for subclass_of in entities:
            parent: EntityNode = self._build_entity_node(entity_id=subclass_of)
            if parent:
                child.qualified = child.qualified or parent.qualified
                child.save()
                self._save_subclass_of_relation(entity_from=child, entity_to=parent)
            else:
                logger.error("Unexpected error while building entity: {}".format(subclass_of))

    def _build_facet_of_entities(self, child: EntityNode, entities: List[str]):
        for facet_of in entities:
            parent: EntityNode = self._build_entity_node(entity_id=facet_of)
            if parent:
                child.qualified = child.qualified or parent.qualified
                child.save()
                self._save_facet_of_relation(entity_from=child, entity_to=parent)
            else:
                logger.error("Unexpected error while building entity: {}".format(facet_of))

    def _build_entity_node(self, entity_id: str) -> EntityNode:
        if self._entity_node_exists(entity_id):
            return self._get_entity_node(entity_id)

        entity: Entity = self.fetch_entity_data(entity_id=entity_id)

        entity_node = self._save_node(entity=entity)
        entity_node.qualified = self._is_target_entity(entity_id)

        self._build_instance_of_entities(child=entity_node, entities=entity.instance_of)
        self._build_subclass_of_entities(child=entity_node, entities=entity.subclass_of)
        self._build_facet_of_entities(child=entity_node, entities=entity.facet_of)

        entity_node.save()
        return entity_node

    def build_graph(self, entity_id: str) -> EntityNode:
        logger.info("Building graph for: {}".format(entity_id))
        return self._build_entity_node(entity_id=entity_id)

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
    def _connect_token_with_page(cls, token_node: TokenNode, page: EntityNode):
        if page:
            token_node.page.connect(page)
            if token_node.page.is_connected(page):
                logger.info("Connected token: {} with page: {}".format(token_node.token, page.entity_id))
            else:
                logger.error("Failed to connect token: {} with page: {}".format(token_node.token, page.entity_id))
        else:
            logger.error("Unknown page: {} for token: {}".format(page.entity_id, token_node.token))

    @classmethod
    def _save_node(cls, entity: Entity) -> EntityNode:
        node = EntityNode(entity_id=entity.id, token=entity.token).save()
        logger.info("Saved node: {}".format(entity.id))
        return node

    @classmethod
    def _save_instance_of_relation(cls, entity_from: EntityNode, entity_to: EntityNode):
        entity_from.instance_of.connect(entity_to)
        if entity_from.instance_of.is_connected(entity_to):
            logger.info("Saved node: {} as instance of: {}".format(entity_from.entity_id, entity_to.entity_id))
        else:
            logger.error("Failed to connect: {} as instance of: {}".format(entity_from.entity_id, entity_to.entity_id))

    @classmethod
    def _save_subclass_of_relation(cls, entity_from: EntityNode, entity_to: EntityNode):
        entity_from.subclass_of.connect(entity_to)
        if entity_from.subclass_of.is_connected(entity_to):
            logger.info("Saved node: {} as subclass of: {}".format(entity_from.entity_id, entity_to.entity_id))
        else:
            logger.error("Failed to connect: {} as subclass of: {}".format(entity_from.entity_id, entity_to.entity_id))

    @classmethod
    def _save_facet_of_relation(cls, entity_from: EntityNode, entity_to: EntityNode):
        entity_from.facet_of.connect(entity_to)
        if entity_from.facet_of.is_connected(entity_to):
            logger.info("Saved node: {} as facet of: {}".format(entity_from.entity_id, entity_to.entity_id))
        else:
            logger.error("Failed to connect: {} as facet of of: {}".format(entity_from.entity_id, entity_to.entity_id))
