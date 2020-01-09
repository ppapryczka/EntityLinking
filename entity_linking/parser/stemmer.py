from stempel import StempelStemmer


class Stemmer():
    stemmer = StempelStemmer.polimorf()

    def stem(self, token: str) -> str:
        return self.stemmer.stem(token)
