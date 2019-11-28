from wikidata.client import Client

from typing import List, Dict, Any
import requests
import pywikibot

ID_INSTANCE_OF = "P31"
WIKIDATA_URL = 'https://query.wikidata.org/sparql'
DEFAULT_RESULTS_LIMIT = 2

def get_data_for_given_entity(entity: str) -> Dict[str, Any]:
    # load data
    client = Client()
    entity = client.get(entity, load=True)
    entity_data = entity.data

    # get only important data - title, lables, descriptions and instance of
    title = entity_data["title"]
    labels = [entity_data["labels"]["pl"], entity_data["labels"]["en"]]
    descriptions = [entity_data['descriptions']["pl"], entity_data['descriptions']["en"]]

    instance_of = []
    for _, obj in enumerate(entity_data["claims"][ID_INSTANCE_OF]):
        instance_of.append(obj["mainsnak"]["datavalue"]["value"]["id"])

    return {
        "title": title,
        "labels": labels,
        "descriptions": descriptions,
        "instance of": instance_of
    }

def get_results_for_given_token(token: str) -> Any:


    site = pywikibot.Site("pl", "wikipedia")
    page = pywikibot.Page(site, token)
    item = pywikibot.ItemPage.fromPage(page)

    print(item)

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
    print(get_pages_ids_for_given_token("Nowy Targ"))
