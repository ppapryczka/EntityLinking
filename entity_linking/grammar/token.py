from entity_linking.grammar.range import Range
from entity_linking.grammar.analysis import Analysis, AnalysisError, ANALYSIS_LENGTH


class Token():
    def __init__(self, start: int, end: int, analysis):
        self._range = Range(start=start, end=end)
        self._word = analysis[0]
        self._analyses = list()
        self.add_analysis(analysis=analysis)

    def __eq__(self, other):
        return self.range == other.range and \
            self.word == other.word and \
            self.analyses == other.analyses

    def __ne__(self, other):
        return not self == other

    @staticmethod
    def from_analysis(start: int, end: int, analysis):
        if len(analysis) != ANALYSIS_LENGTH:
            raise AnalysisError(len(analysis))

        return Token(start=start, end=end, analysis=analysis)

    @property
    def range(self):
        return self._range

    @property
    def analyses(self):
        return self._analyses

    @property
    def word(self) -> str:
        return self._word

    def add_analysis(self, analysis):
        self._analyses.append(Analysis.from_analysis(analysis=analysis))
