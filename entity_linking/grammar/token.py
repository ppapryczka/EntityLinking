from entity_linking.grammar.range import Range
from entity_linking.grammar.analysis import Analysis, AnalysisError, ANALYSIS_LENGTH


class Token():
    def __init__(self, start: int, end: int, analysis):
        self._range = Range(start=start, end=end)
        self._word = analysis[0]
        self._analyses = list()
        self.add_analysis(analysis=analysis)

    def __eq__(self, other):
        return self.get_range() == other.get_range() and \
            self.get_word() == other.get_word() and \
            self.get_analyses() == other.get_analyses()

    def __ne__(self, other):
        return not self == other

    @staticmethod
    def from_analysis(start: int, end: int, analysis):
        if len(analysis) != ANALYSIS_LENGTH:
            raise AnalysisError(len(analysis))

        return Token(start=start, end=end, analysis=analysis)

    def get_range(self) -> Range:
        return self._range

    def get_analyses(self):
        return self._analyses

    def get_word(self) -> str:
        return self._word

    def add_analysis(self, analysis):
        self._analyses.append(Analysis.from_analysis(analysis=analysis))
