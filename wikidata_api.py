from wikidata.client import Client, EntityId

from typing import List, Dict, Any
import requests

ID_INSTANCE_OF: str = "P31"
ID_SUBCLASS_OF: str = "P279"
WIKIDATA_URL:str = 'https://query.wikidata.org/sparql'
DEFAULT_RESULTS_LIMIT: int = 2


def get_data_for_given_entity(entity: EntityId) -> Dict[str, Any]:
    # load data
    client = Client()
    entity = client.get(entity, load=True)
    entity_data = entity.data

    # get only important data - title, lables, descriptions and instance of
    title = entity_data["title"]

    labels = []
    if "lables" in entity_data:
        if "pl" in entity_data["lables"]:
            labels.append(entity_data["labels"]["pl"])

        if "en" in entity_data["lables"]:
            labels.append(entity_data["labels"]["en"])

    descriptions = []
    if "descriptions" in entity_data:
        if "pl" in entity_data["descriptions"]:
            descriptions.append(entity_data["labels"]["pl"])

        if "en" in entity_data["descriptions"]:
            descriptions.append(entity_data["labels"]["en"])

    instance_of = []
    # take instance of entities
    if "claims" in entity_data:
        if ID_INSTANCE_OF in entity_data["claims"]:
            for _, obj in enumerate(entity_data["claims"][ID_INSTANCE_OF]):
                instance_of.append(obj["mainsnak"]["datavalue"]["value"]["id"])

        # take subclass of entities
        if ID_SUBCLASS_OF in entity_data["claims"]:
            for _, obj in enumerate(entity_data["claims"][ID_SUBCLASS_OF]):
                instance_of.append(obj["mainsnak"]["datavalue"]["value"]["id"])

    return {
        "title": title,
        "labels": labels,
        "descriptions": descriptions,
        "instance of": instance_of
    }


def get_instance_of_for_entity(entity: EntityId) -> List:
    data = get_data_for_given_entity(entity)
    return data["instance of"]


def get_pages_ids_for_given_token(token: str) -> List[str]:
    # crete request for given token, ref:
    # https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual/MWAPI#Find_all_entities_with_labels_%22cheese%22_and_get_their_types
    query = "SELECT * WHERE { " \
            "   SERVICE wikibase:mwapi { "\
            "       bd:serviceParam wikibase:api \"EntitySearch\" . " \
            "       bd:serviceParam wikibase:endpoint \"www.wikidata.org\" . " \
            f"      bd:serviceParam mwapi:search \"{token}\" . " \
            f"      bd:serviceParam mwapi:language \"pl\" . " \
            "       ?item wikibase:apiOutputItem mwapi:item . " \
            "       ?num wikibase:apiOrdinal true . " \
            "   } " \
            "} ORDER BY ASC(?num)"f" LIMIT {DEFAULT_RESULTS_LIMIT}"

    # request for json
    r = requests.get(WIKIDATA_URL, params={'format': 'json', 'query': query})
    data = r.json()

    entities = []
    for x in data["results"]["bindings"]:
        entities.append(x["item"]["value"].split("/")[-1])

    return entities


if __name__=="__main__":
    print(get_instance_of_for_entity("Q231593"))
    print(get_pages_ids_for_given_token("Nowy Targ"))

