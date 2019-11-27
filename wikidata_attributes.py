from wikidata.client import Client

INSTANCE_OF_ID = "P31"


def get_data_for_given_entity(entity: str) -> dict:
    # load data
    client = Client()
    entity = client.get(entity, load=True)
    entity_data = entity.data

    # get only important data - title, lables, descriptions and instance of
    title = entity_data["title"]
    labels = [entity_data["labels"]["pl"], entity_data["labels"]["en"]]
    descriptions = [entity_data['descriptions']["pl"], entity_data['descriptions']["en"]]

    instance_of = []
    for _, obj in enumerate(entity_data["claims"][INSTANCE_OF_ID]):
        instance_of.append(obj["mainsnak"]["datavalue"]["value"]["id"])

    return {
        "title": title,
        "labels": labels,
        "descriptions": descriptions,
        "instance of": instance_of
    }


if __name__=="__main__":
    print(get_data_for_given_entity('Q231593'))
