"""
Declarations of Tokenizer classes.
"""

from abc import ABC, abstractmethod
from typing import List

from entity_linking.database_api import WikidataAPI
from entity_linking.utils import (
    BEST_TOKEN_GROUPS,
    ExtendedTokensGroup,
    TokensGroup,
    TokensSequence,
)


class Tokenizer(ABC):
    """
    Base class for all tokenizers - they convert sequences to tokens groups
    that might connect to true entities.
    """

    wikidata_API: WikidataAPI
    max_token_length: int

    def __init__(self, wikidata_API: WikidataAPI, max_token_length: int):
        """
        Set name of database to get pages for tokens.

        Args:
            wikidata_API: API to get wikidata pages.
        """
        self.wikidata_API = wikidata_API
        self.max_token_length = max_token_length

    @abstractmethod
    def tokenize(self, sequence: TokensSequence) -> List[TokensGroup]:
        """
        Abstract method to all tokenizers - from sequence create tokens.

        Args:
            sequence: Sequence of tokens to tokenize.

        Returns:
            List of tokens created from ``sequence``.
        """
        pass


class WikidataLengthTokenizer(Tokenizer):
    max_token_length: int

    def __init__(
        self, token_length: int, wikidata_API: WikidataAPI, max_token_length: int
    ):
        super().__init__(wikidata_API, max_token_length)

    def tokenize(self, sequence: TokensSequence) -> List[TokensGroup]:
        result: List[ExtendedTokensGroup] = []
        for x in range(len(sequence.sequence) - self.max_token_length + 1):
            if x + self.max_token_length < len(sequence.sequence):

                # check pages for token group in text
                entities = self.wikidata_API.get_pages_for_token(
                    sequence.get_token_as_str(x, x + self.max_token_length),
                )
                if len(entities) > 0:
                    result.append(
                        ExtendedTokensGroup(
                            x,
                            x + self.max_token_length,
                            sequence.get_token_as_str(x, x + self.max_token_length),
                            entities,
                        )
                    )

                # check pages for lemma form
                entities = self.wikidata_API.get_pages_for_token(
                    sequence.get_token_as_str_from_lemma(x, x + self.max_token_length),
                )

                if len(entities) > 0:
                    result.append(
                        ExtendedTokensGroup(
                            x,
                            x + self.max_token_length,
                            sequence.get_token_as_str_from_lemma(
                                x, x + self.max_token_length
                            ),
                            entities,
                        )
                    )

        return result


class WikidataMorphTagsTokenizer(Tokenizer):
    def __init__(self, wikidata_API: WikidataAPI, max_token_length: int):
        super().__init__(wikidata_API, max_token_length)

    def get_possible_tokens(self, sequence: TokensSequence) -> List:
        possible_tokens = []

        for token_l in range(1, self.max_token_length + 1):
            for x in range(len(sequence.sequence) - self.max_token_length + 1):
                morph_tags = [
                    t.get_first_morph_tags_part()
                    for t in sequence.sequence[x: x + token_l]
                ]
                if morph_tags in BEST_TOKEN_GROUPS:
                    possible_tokens.append((x, x + token_l))

        return possible_tokens

    def tokenize(self, sequence: TokensSequence) -> List[TokensGroup]:
        result: List[ExtendedTokensGroup] = []

        possible_tokens = self.get_possible_tokens(sequence)

        for possible_token in possible_tokens:

            # check pages for token group in text
            entities = self.wikidata_API.get_pages_for_token(
                sequence.get_token_as_str(possible_token[0], possible_token[1]),
            )
            if len(entities) > 0:
                result.append(
                    ExtendedTokensGroup(
                        possible_token[0],
                        possible_token[1],
                        sequence.get_token_as_str(possible_token[0], possible_token[1]),
                        entities,
                    )
                )

            # check pages for lemma form
            entities = self.wikidata_API.get_pages_for_token(
                sequence.get_token_as_str_from_lemma(
                    possible_token[0], possible_token[1]
                ),
            )

            if len(entities) > 0:
                result.append(
                    ExtendedTokensGroup(
                        possible_token[0],
                        possible_token[1],
                        sequence.get_token_as_str_from_lemma(
                            possible_token[0], possible_token[1]
                        ),
                        entities,
                    )
                )

        return result
