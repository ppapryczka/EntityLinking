"""
Module that contains functions that get data from wikidata website.
"""
from typing import Any, Dict, List, Union

import requests
from wikidata.client import Client
from wikidata.entity import EntityId

from entity_linking.utils import (
    ID_FACET_OF,
    ID_INSTANCE_OF,
    ID_SUBCLASS_OF,
    USER_AGENT,
    WIKIDATA_URL,
    WIKIDATA_URL_SPARQL,
    DEFAULT_RESULTS_LIMIT
)


def get_wikidata_link_for_entity(entity: str) -> str:
    """
    Get wikidata address for given ``entity``.

    Args:
        entity: Name of entity, in format Q{Number}.

    Returns:
        Wikidata address to given entity.
    """
    return f"{WIKIDATA_URL}/{entity}"


def get_data_for_given_entity(entity: EntityId) -> Dict[str, Any]:
    """
    Get most important data for given ``entity``: title, labels, descriptions,
    instance of and subclass of. It uses wikidata library.

    Args:
        entity: Name of entity, in format Q{Number}.

    Returns:
        Dict with mentioned data.
    """

    # load data
    client = Client()
    entity = client.get(entity, load=True)
    entity_data = entity.data

    # get only important data - title, labels, descriptions and instance of
    title = entity_data["title"]
    labels = []
    if "labels" in entity_data:
        # it doesn't matter if Polish description is not defined
        if "pl" in entity_data["labels"]:
            labels.append(entity_data["labels"]["pl"]["value"])
        else:
            labels.append("")

        if "en" in entity_data["labels"]:
            labels.append(entity_data["labels"]["en"]["value"])
        else:
            labels.append("")

    descriptions = []
    if "descriptions" in entity_data:
        # it doesn't matter if Polish description is not defined
        if "pl" in entity_data["descriptions"]:
            descriptions.append(entity_data["descriptions"]["pl"]["value"])
        else:
            descriptions.append("")

        if "en" in entity_data["descriptions"]:
            descriptions.append(entity_data["descriptions"]["en"]["value"])
        else:

            descriptions.append("")

    instance_of = []
    if "claims" in entity_data:
        # take instance of entity
        if ID_INSTANCE_OF in entity_data["claims"]:
            for _, obj in enumerate(entity_data["claims"][ID_INSTANCE_OF]):
                mainsnak = obj["mainsnak"]
                if mainsnak["snaktype"] != "novalue":
                    instance_of.append(mainsnak["datavalue"]["value"]["id"])

        # take subclass of entity
        if ID_SUBCLASS_OF in entity_data["claims"]:
            for _, obj in enumerate(entity_data["claims"][ID_SUBCLASS_OF]):
                mainsnak = obj["mainsnak"]
                if mainsnak["snaktype"] != "novalue":
                    instance_of.append(mainsnak["datavalue"]["value"]["id"])

        # take facet of
        if ID_FACET_OF in entity_data["claims"]:
            for _, obj in enumerate(entity_data["claims"][ID_FACET_OF]):
                mainsnak = obj["mainsnak"]
                if mainsnak["snaktype"] != "novalue":
                    instance_of.append(mainsnak["datavalue"]["value"]["id"])

    return {
        "title": title,
        "labels": labels,
        "descriptions": descriptions,
        "instance of": instance_of,
    }


def get_subclasses_for_entity_wikidata(entity: EntityId) -> List:
    """
    Get data using Wikidata library and only instance of part.

    Args:
        entity: Name of entity, in format Q{Number}.

    Returns:
       List of "instance of" and "subclass of" for entity.
    """
    # load data
    client = Client()
    entity = client.get(entity, load=True)
    entity_data = entity.data

    instance_of = []
    if "claims" in entity_data:
        # take instance of entity
        if ID_INSTANCE_OF in entity_data["claims"]:
            for _, obj in enumerate(entity_data["claims"][ID_INSTANCE_OF]):
                mainsnak = obj["mainsnak"]
                if mainsnak["snaktype"] != "novalue":
                    if "datavalue" in mainsnak:
                        instance_of.append(mainsnak["datavalue"]["value"]["id"])

        # take subclass of entity
        if ID_SUBCLASS_OF in entity_data["claims"]:
            for _, obj in enumerate(entity_data["claims"][ID_SUBCLASS_OF]):
                mainsnak = obj["mainsnak"]
                if mainsnak["snaktype"] != "novalue":
                    if "datavalue" in mainsnak:
                        instance_of.append(mainsnak["datavalue"]["value"]["id"])

        # take facet of entity
        if ID_FACET_OF in entity_data["claims"]:
            for _, obj in enumerate(entity_data["claims"][ID_FACET_OF]):
                mainsnak = obj["mainsnak"]
                if mainsnak["snaktype"] != "novalue":
                    if "datavalue" in mainsnak:
                        instance_of.append(mainsnak["datavalue"]["value"]["id"])
    return instance_of


def get_pages_for_token_wikidata(token: str) -> List[str]:
    """
    Get wikidata results for given ``token`` using SPARQL language.

    Args:
        token: Query to search in wikidata base.

    Returns:
        List of results as a entities IDs.
    """

    # omit tokens with '\' sign - that tokens cause wikidata error
    for w in token.split():
        if w == "\\":
            return []

    # crete request for given token, ref:
    # https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual/MWAPI#Examples
    q = (
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
        f" LIMIT {DEFAULT_RESULTS_LIMIT}"
    )

    # request for json
    headers = {"User-Agent": USER_AGENT}
    r: requests.Response = requests.get(
        WIKIDATA_URL_SPARQL, headers=headers, params={"format": "json", "query": q}
    )

    # parse json
    data = r.json()

    # take entities
    entities = []
    for x in data["results"]["bindings"]:
        entities.append(x["item"]["value"].split("/")[-1])

    return entities


def get_title_in_polish_wikipedia(entity: EntityId) -> Union[None, str]:
    """
    Get title of wikipedia page for ``entity``.

    Args:
        entity: ID of entity in format Q{NUM}.

    Returns:
        Title of page in wikipedia or None if value is missing.
    """
    # load data
    client = Client()
    entity = client.get(entity, load=True)
    entity_data = entity.data

    if "sitelinks" in entity_data:
        if "plwiki" in entity_data["sitelinks"]:
            if "url" in entity_data["sitelinks"]["plwiki"]:
                return entity_data["sitelinks"]["plwiki"]["title"]

    return None


def get_url_to_polish_wikipedia(entity: EntityId) -> Union[None, str]:
    """
    Get url to wikipedia page for ``entity``.

    Args:
        entity: ID of entity in format Q{NUM}.

    Returns:
        Url to wikipedia page for ``entity`` or None if value is missing.
    """

    # load data
    client = Client()
    entity = client.get(entity, load=True)
    entity_data = entity.data

    if "sitelinks" in entity_data:
        if "plwiki" in entity_data["sitelinks"]:
            if "url" in entity_data["sitelinks"]["plwiki"]:
                return entity_data["sitelinks"]["plwiki"]["url"]

    return None
