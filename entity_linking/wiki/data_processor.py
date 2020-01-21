import csv
from typing import List
from entity_linking.grammar.token import Token
from entity_linking.wiki.graph import GraphBuilder
from entity_linking.parser.parser import Parser

PUNCTUATION_MARK_TAG = "interp"


class DataProcessor:
    def __init__(self, host: str = 'localhost', redis_port: int = 6379,
                 db_port: int = 7687):
        self._parser = Parser()
        self._graph_builder = GraphBuilder(redis_host=host, redis_port=redis_port, db_host=host,
                                           db_port=db_port)

    def process_file(self, filename):
        with open(filename) as tsv_file:
            tsv_reader = csv.reader(tsv_file, delimiter="\t")
            for line in tsv_reader:
                if not line:
                    continue
                tokens: List[Token] = self._parser.parse_text(line[1])
                for token in tokens:
                    for analysis in token.analyses:
                        if analysis.tag != PUNCTUATION_MARK_TAG:
                            lemma = analysis.lemma
                            r_index = lemma.rfind(":")
                            if r_index > -1:
                                lemma = lemma[:r_index]
                            self.store_token(lemma)

    def store_token(self, token: str):
        self._graph_builder.build_pages(token=token)
