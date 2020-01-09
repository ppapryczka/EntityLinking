from entity_linking import wikidata_api as api
from entity_linking import wikidata_graph as graph

from entity_linking.maintenance.logger import get_logger

def main():
    logger = get_logger("app")
    logger.info("Hello world!")


if __name__ == "__main__":
    main()
