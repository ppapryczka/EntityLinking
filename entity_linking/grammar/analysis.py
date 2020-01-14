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
        return self.lemma == other.lemma and \
            self.tag == other.tag and \
            self.add_info_1 == other.add_info_1 and \
            self.add_info_2 == other.add_info_2

    def __ne__(self, other):
        return not self == other

    @property
    def lemma(self):
        return self._lemma

    @property
    def tag(self):
        return self._tag

    @property
    def add_info_1(self):
        return self._add_info1

    @property
    def add_info_2(self):
        return self._add_info2

    @staticmethod
    def from_analysis(analysis):

        if len(analysis) != ANALYSIS_LENGTH:
            raise AnalysisError(len(analysis))

        return Analysis(lemma=analysis[1], tag=analysis[2],
                        add_info_1=analysis[3], add_info_2=analysis[4])
