"""
Declaration of Wikidata api - first by direct request to wikidata website, second by simple database.
"""

from abc import ABC, abstractmethod
from typing import List

from wikidata.entity import EntityId

from entity_linking.wikidata_db_api import (get_pages_for_token_db,
                                            get_subclasses_for_entity_db)
from entity_linking.wikidata_web_api import (
    get_pages_for_token_wikidata, get_subclasses_for_entity_wikidata)


class WikidataAPI(ABC):
    @abstractmethod
    def get_subclasses_for_entity(self, entity: EntityId) -> List[str]:
        pass

    @abstractmethod
    def get_pages_for_token(self, token: str) -> List[str]:
        pass


class WikidataWebAPI(WikidataAPI):
    def get_subclasses_for_entity(self, entity: str) -> List[str]:
        return get_subclasses_for_entity_wikidata(EntityId(entity))

    def get_pages_for_token(self, token: str) -> List[str]:
        return get_pages_for_token_wikidata(token)


class WikidataDBAPI(WikidataAPI):
    database_name: str

    def __init__(self, database_name: str):
        self.database_name = database_name

    def get_subclasses_for_entity(self, entity: str) -> List[str]:
        return get_subclasses_for_entity_db(self.database_name, entity)

    def get_pages_for_token(self, token: str) -> List[str]:
        return get_pages_for_token_db(self.database_name, token)
