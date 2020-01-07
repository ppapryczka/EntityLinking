from wikidata.client import Client, EntityId
import datetime
from typing import List, Dict, Any
import requests

# ID of "instance of" property
ID_INSTANCE_OF: str = "P31"
# ID of "subclass of" property
ID_SUBCLASS_OF: str = "P279"
# address of wikidata
WIKIDATA_URL: str = "https://www.wikidata.org/wiki/"
# address of wikidata sparql API
WIKIDATA_URL_SPARQL: str = 'https://query.wikidata.org/sparql'
# default max results
DEFAULT_RESULTS_LIMIT: int = 2

# target entities
TARGET_ENTITIES: List[str] = [
    # human
    "Q5",
    # geographic location
    "Q2221906",
    # academic discipline
    "Q11862829",
    # anatomical structure
    "Q4936952",
    # occupation
    "Q12737077",
    # vehicle model
    "Q29048322",
    # construction
    "Q811430",
    # written work
    "Q47461344",
    # astronomical object
    "Q6999",
    # clothing
    "Q11460",
    # taxon
    "Q16521",
    # mythical entity
    "Q24334685",
    # type of sport
    "Q31629",
    # supernatural being
    "Q28855038",
    # liquid
    "Q11435",
    # political system
    "Q28108",
    # group of living things
    "Q16334298",
    # chemical entity
    "Q43460564",
    # publication
    "Q732577",
    # landform
    "Q271669",
    # language
    "Q34770",
    # unit
    "Q2198779",
    # physico-geographical object
    "Q20719696",
    # intellectual work
    "Q15621286",
    # tool
    "Q39546",
    # organism
    "Q7239",
    # food
    "Q2095"
]


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
    if "claims" in entity_data:
        # take instance of entity
        if ID_INSTANCE_OF in entity_data["claims"]:
            for _, obj in enumerate(entity_data["claims"][ID_INSTANCE_OF]):
                instance_of.append(obj["mainsnak"]["datavalue"]["value"]["id"])

        # take subclass of entity
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
    """
    Call ``get_data_for_entity`` function, get data and
    take only instance of part.

    Args:
        entity: Name of entity, in format Q{Number}.

    Returns:
       List of "instance of" and "subclass of" for entity.
    """
    data = get_data_for_given_entity(entity)
    return data["instance of"]


def get_pages_ids_for_given_token(token: str) -> List[str]:
    """
    Get wikidata results for given ``token`` using SPARQL le

    Args:
        token: Query to search in wikidata base.

    Returns:
        List of results as a entities IDs.
    """

    # crete request for given token, ref:
    # https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual/MWAPI#Examples
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
    r = requests.get(WIKIDATA_URL_SPARQL, params={'format': 'json', 'query': query})

    data = r.json()

    entities = []
    for x in data["results"]["bindings"]:
        entities.append(x["item"]["value"].split("/")[-1])

    return entities


if __name__=="__main__":
    '''
    now = datetime.datetime.now()
    get_data_for_given_entity("Q231593")
    print(datetime.datetime.now() - now)
    '''
    import datetime

    now = datetime.datetime.now()
    print(get_instance_of_for_entity(EntityId("Q231593")))
    print(datetime.datetime.now() - now)

    now = datetime.datetime.now()
    print(get_pages_ids_for_given_token("Nowy Targ"))
    print(datetime.datetime.now() - now)

