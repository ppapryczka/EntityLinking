"""
Declarations of Tokenizer classes.
"""

from abc import ABC, abstractmethod
from typing import List

from entity_linking.utils import BEST_TOKEN_GROUPS, TokensGroup, TokensSequence
from entity_linking.wikdata_api import WikidataAPI


class Tokenizer(ABC):
    """
    Base class for all tokenizers - they convert sequences to tokens groups
    that might connect to true entities.
    """

    wikidata_API: WikidataAPI
    max_token_length: int

    def __init__(self, wikidata_API: WikidataAPI, max_token_length: int):
        """
        Set fields: wikidata API and token length.

        Args:
            wikidata_API: API to get wikidata pages.
            max_token_length: Max length of token.
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
    """
    Simple tokenizer that takes ``max_token_length`` long parts of sequences.
    """

    def __init__(self, wikidata_API: WikidataAPI, max_token_length: int):
        """
        Set fields: wikidata API and token length.

        Args:
            wikidata_API: API to get wikidata pages.
            max_token_length: Max length of token.
        """
        super().__init__(wikidata_API, max_token_length)

    def tokenize(self, sequence: TokensSequence) -> List[TokensGroup]:
        """
        Iterate over sequence tokens and take ``max_token_length`` parts of sequence.
        Search for pages in wikidata and if find any add to result list.

        Args:
            sequence: Sequence to tokenize.

        Returns:
            List of token groups.
        """
        result: List[TokensGroup] = []
        for x in range(len(sequence.sequence) - self.max_token_length + 1):
            if x + self.max_token_length < len(sequence.sequence):

                # check pages for token group in text
                entities = self.wikidata_API.get_pages_for_token(
                    sequence.get_token_str_original_form(x, x + self.max_token_length),
                )
                if len(entities) > 0:
                    result.append(
                        TokensGroup(
                            x,
                            x + self.max_token_length,
                            sequence.get_token_str_original_form(
                                x, x + self.max_token_length
                            ),
                            entities,
                        )
                    )

                # check pages for lemma form
                entities = self.wikidata_API.get_pages_for_token(
                    sequence.get_token_str_lemma_form(x, x + self.max_token_length),
                )

                if len(entities) > 0:
                    result.append(
                        TokensGroup(
                            x,
                            x + self.max_token_length,
                            sequence.get_token_str_lemma_form(
                                x, x + self.max_token_length
                            ),
                            entities,
                        )
                    )

        return result


class WikidataMorphTagsTokenizer(Tokenizer):
    """
    Tokenizer that takes only best token groups by morph tags - look BEST_TOKEN_GROUPS.
    """

    def __init__(self, wikidata_API: WikidataAPI, max_token_length: int):
        """
        Set fields: wikidata API and token length.

        Args:
            wikidata_API: API to get wikidata pages.
            max_token_length: Max length of token.
        """
        super().__init__(wikidata_API, max_token_length)

    def get_possible_tokens(self, sequence: TokensSequence) -> List:
        """
        Get possible tokens from ``sequence`` by taking morph tags.

        Args:
            sequence: Sequence to tokenize.

        Returns:
            List of tuples(end, start) that describe possible tokens.
        """
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
        """
        Iterate over sequence tokens using ``get_possible_tokens``.
        Search for pages in wikidata and if find any add to result list.

        sequence:

        Returns:
            List of token groups.
        """
        result: List[TokensGroup] = []

        possible_tokens = self.get_possible_tokens(sequence)

        for possible_token in possible_tokens:

            # check pages for token group in text
            entities = self.wikidata_API.get_pages_for_token(
                sequence.get_token_str_original_form(
                    possible_token[0], possible_token[1]
                ),
            )
            if len(entities) > 0:
                result.append(
                    TokensGroup(
                        possible_token[0],
                        possible_token[1],
                        sequence.get_token_str_original_form(
                            possible_token[0], possible_token[1]
                        ),
                        entities,
                    )
                )

            # check pages for lemma form
            entities = self.wikidata_API.get_pages_for_token(
                sequence.get_token_str_lemma_form(possible_token[0], possible_token[1]),
            )

            if len(entities) > 0:
                result.append(
                    TokensGroup(
                        possible_token[0],
                        possible_token[1],
                        sequence.get_token_str_lemma_form(
                            possible_token[0], possible_token[1]
                        ),
                        entities,
                    )
                )

        return result
