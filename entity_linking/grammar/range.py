class Range():
    def __init__(self, start: int, end: int):
        self._start = start
        self._end = end

    def __eq__(self, other):
        return self.get_start() == other.get_start() and \
            self.get_end() == other.get_end()

    def __ne__(self, other):
        return not self == other

    def get_start(self) -> int:
        return self._start

    def get_end(self) -> int:
        return self._end
