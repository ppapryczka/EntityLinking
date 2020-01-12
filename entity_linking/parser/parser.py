from morfeusz2 import Morfeusz
from typing import List
from entity_linking.grammar.token import Token


class Parser():
    def __init__(self):
        self._morfeusz = Morfeusz()

    def parse_text(self, text: str):
        tokens = dict()
        analyses = self.analyse_text(text)
        for i, j, analysis in analyses:
            if (i, j) in tokens.keys():
                tokens[(i, j)].add_analysis(analysis=analysis)
            else:
                tokens[(i, j)] = Token.from_analysis(
                    start=i, end=j, analysis=analysis)

        return [token for pos, token in tokens.items()]

    def analyse_text(self, text: str):
        return self._morfeusz.analyse(text)
