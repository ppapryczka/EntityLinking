"""
Declarations of Tokenizer classes.
"""

from abc import ABC, abstractmethod
from typing import List

from entity_linking.database_api import WikidataAPI
from entity_linking.utils import (ExtendedTokensGroup, TokensGroup,
                                  TokensSequence)


class Tokenizer(ABC):
    """
    Base class for all tokenizers - they convert sequences to tokens groups
    that might connect to true entities.
    """

    wikidata_API: WikidataAPI

    def __init__(self, wikidata_API: WikidataAPI):
        """
        Set name of database to get pages for tokens.

        Args:
            wikidata_API: API to get wikidata pages.
        """
        self.wikidata_API = wikidata_API

    @abstractmethod
    def tokenize(self, sequence: TokensSequence) -> List[TokensGroup]:
        """
        Abstract metod to all tokenizers - from sequence create tokens.

        Args:
            sequence: Sequence of tokens to tokenize.

        Returns:
            List of tokens created from ``sequence``.
        """
        pass


class WikidataLengthTokenizer(Tokenizer):
    token_length: int

    def __init__(self, token_length: int, wikidata_API: WikidataAPI):
        super().__init__(wikidata_API)
        self.token_length = token_length

    def tokenize(self, sequence: TokensSequence) -> List[TokensGroup]:
        result: List[ExtendedTokensGroup] = []
        for x in range(len(sequence.sequence) - self.token_length + 1):
            if x + self.token_length < len(sequence.sequence):
                # check pages for form in text
                entities = self.wikidata_API.get_pages_for_token(
                    sequence.get_token_as_str(x, x + self.token_length),
                )

                if len(entities) > 0:
                    result.append(
                        ExtendedTokensGroup(
                            x,
                            x + self.token_length,
                            sequence.get_token_as_str(x, x + self.token_length),
                            entities,
                        )
                    )

                # check pages for lemma form
                entities = self.wikidata_API.get_pages_for_token(
                    sequence.get_token_as_str_from_lemma(x, x + self.token_length),
                )

                if len(entities) > 0:
                    result.append(
                        ExtendedTokensGroup(
                            x,
                            x + self.token_length,
                            sequence.get_token_as_str_from_lemma(
                                x, x + self.token_length
                            ),
                            entities,
                        )
                    )

        return result


class WikidataMorphTagsTokenizer(Tokenizer):
    token_length: int

    def __init__(self, token_length: int, wikidata_API: WikidataAPI):
        super().__init__(wikidata_API)
        self.token_length = token_length

    def tokenize(self, sequence: TokensSequence) -> List[TokensGroup]:
        result: List[ExtendedTokensGroup] = []
        for x in range(len(sequence.sequence) - self.token_length + 1):
            if x + self.token_length < len(sequence.sequence):
                # check pages for form in text
                entities = self.wikidata_API.get_pages_for_token(
                    sequence.get_token_as_str(x, x + self.token_length)
                )

                if len(entities) > 0:
                    result.append(
                        ExtendedTokensGroup(
                            x,
                            x + self.token_length,
                            sequence.get_token_as_str(x, x + self.token_length),
                            entities,
                        )
                    )

                # check pages for lemma form
                entities = self.wikidata_API.get_pages_for_token(
                    sequence.get_token_as_str_from_lemma(x, x + self.token_length)
                )

                if len(entities) > 0:
                    result.append(
                        ExtendedTokensGroup(
                            x,
                            x + self.token_length,
                            sequence.get_token_as_str_from_lemma(
                                x, x + self.token_length
                            ),
                            entities,
                        )
                    )

        return result
