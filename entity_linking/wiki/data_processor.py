from entity_linking.wiki.graph import GraphBuilder


class DataProcessor:
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379,
                 db_host: str = 'localhost', db_port: int = 7687):
        self._graph_builder = GraphBuilder(redis_host=redis_host, redis_port=redis_port, db_host=db_host,
                                           db_port=db_port)

    def store_token(self, token: str):
        self._graph_builder.build_pages(token=token)
