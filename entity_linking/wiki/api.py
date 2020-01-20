"""
Module that contains functions that get data from wikidata website.
"""
from typing import Any, Dict, List

import requests
from wikidata.client import Client, EntityId

# ID of "instance of" property
from entity_linking.wiki.entity import Entity

ID_INSTANCE_OF: str = "P31"
# ID of "subclass of" property
ID_SUBCLASS_OF: str = "P279"
# ID of facet of
ID_FACET_OF: str = "P1269"
# address of wikidata
WIKIDATA_URL: str = "https://www.wikidata.org/wiki/"
# address of wikidata sparql API
WIKIDATA_URL_SPARQL: str = "https://query.wikidata.org/sparql"
# default max results
DEFAULT_RESULTS_LIMIT: int = 5
# user agent
USER_AGENT: str = "EntityLinking/1.0 (https://github.com/ppapryczka/EntityLinking) Python/Wikidata/0.6.1"


class WikidataApi:

    def __init__(self):
        self._client = Client()

    @classmethod
    def _prepare_pages_query(cls, token: str, results_limit) -> str:
        # crete request for given token, ref:
        # https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual/MWAPI#Examples
        return (
            "SELECT * WHERE { "
            "   SERVICE wikibase:mwapi { "
            '       bd:serviceParam wikibase:api "EntitySearch" . '
            '       bd:serviceParam wikibase:endpoint "www.wikidata.org" . '
            f'      bd:serviceParam mwapi:search "{token}" . '
            f'      bd:serviceParam mwapi:language "pl" . '
            "       ?item wikibase:apiOutputItem mwapi:item . "
            "       ?num wikibase:apiOrdinal true . "
            "   } "
            "} ORDER BY ASC(?num)"
            f" LIMIT {results_limit}")

    @classmethod
    def get_pages(cls, token: str, results_limit=DEFAULT_RESULTS_LIMIT) -> List[str]:
        # omit tokens with '\' sign - that tokens cause wikidata error
        for w in token.split():
            if w == "\\":
                return list()

        headers = {"User-Agent": USER_AGENT}
        r: requests.Response = requests.get(
            WIKIDATA_URL_SPARQL,
            headers=headers,
            params={"format": "json", "query": cls._prepare_pages_query(token=token, results_limit=results_limit)}
        )

        data = r.json()

        # take pages
        pages: List[str] = []
        for x in data["results"]["bindings"]:
            pages.append(x["item"]["value"].split("/")[-1])

        return pages

    @classmethod
    def _get_entity_data_property(cls, data, property_id: str) -> List[str]:
        properties = list()
        if "claims" in data:
            # take instance of entity
            if property_id in data["claims"]:
                for _, obj in enumerate(data["claims"][property_id]):
                    mainsnak = obj["mainsnak"]
                    if mainsnak["snaktype"] != "novalue":
                        properties.append(mainsnak["datavalue"]["value"]["id"])
        return properties

    @classmethod
    def _get_token_from_data(cls, data) -> str:
        token = ""
        if "labels" in data:
            if "pl" in data["labels"]:
                token = data["labels"]["pl"]["value"]

        return token

    def get_entity_data(self, entity_id: str) -> Entity:
        entity = self._client.get(EntityId(entity_id), load=True)
        token = self._get_token_from_data(entity.data)
        instance_of = self._get_entity_data_property(data=entity.data, property_id=ID_INSTANCE_OF)
        subclass_of = self._get_entity_data_property(data=entity.data, property_id=ID_SUBCLASS_OF)
        facet_of = self._get_entity_data_property(data=entity.data, property_id=ID_FACET_OF)

        return Entity(id=entity_id, token=token, instance_of=instance_of, subclass_of=subclass_of,
                      facet_of=facet_of)
