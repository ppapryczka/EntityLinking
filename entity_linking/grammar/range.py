class Range():
    def __init__(self, start: int, end: int):
        self._start = start
        self._end = end

    def __eq__(self, other):
        return self.start == other.start and \
            self.end == other.end

    def __ne__(self, other):
        return not self == other

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end
