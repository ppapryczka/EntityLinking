ANALYSIS_LENGTH = 5


class AnalysisError(RuntimeError):
    def __init__(self, analysis_length: int):
        super().__init__("Invalid analysis length, expected: {}, got: {}".format(
            ANALYSIS_LENGTH, analysis_length))


class Analysis():
    def __init__(self, lemma: str, tag: str, add_info_1, add_info_2):
        self._lemma = lemma
        self._tag = tag
        self._add_info1 = add_info_1
        self._add_info2 = add_info_2

    def __eq__(self, other):
        return self.get_lemma() == other.get_lemma() and \
            self.get_tag() == other.get_tag() and \
            self.get_add_info_1() == other.get_add_info_1() and \
            self.get_add_info_2() == other.get_add_info_2()

    def __ne__(self, other):
        return not self == other

    def get_lemma(self) -> str:
        return self._lemma

    def get_tag(self) -> str:
        return self._tag

    def get_add_info_1(self):
        return self._add_info1

    def get_add_info_2(self):
        return self._add_info2

    @staticmethod
    def from_analysis(analysis):

        if len(analysis) != ANALYSIS_LENGTH:
            raise AnalysisError(len(analysis))

        return Analysis(lemma=analysis[1], tag=analysis[2],
                        add_info_1=analysis[3], add_info_2=analysis[4])
