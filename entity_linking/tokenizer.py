from typing import List

from entity_linking.utils import TokensSequence, TokensGroup, ExtendedTokensGroup
from entity_linking.wikidata_api import get_pages_ids_for_given_token

from abc import ABC, abstractmethod


def simple_tokenize_for_entity_sequence(
    token_length: int, sequence: TokensSequence
) -> List[TokensGroup]:
    result: List[TokensGroup] = []
    for x in range(len(sequence.sequence)):
        if x + token_length < len(sequence.sequence):
            result.append(TokensGroup(x, x + token_length))
    return result


def tokenize_using_wikidata_result(
    token_length: int, sequence: TokensSequence
) -> List[ExtendedTokensGroup]:
    result: List[ExtendedTokensGroup] = []
    for x in range(len(sequence.sequence)):
        if x + token_length < len(sequence.sequence):
            entities = get_pages_ids_for_given_token(
                sequence.get_token_as_str(x, x + token_length)
            )
            if len(entities) > 0:
                result.append(ExtendedTokensGroup(x, x + token_length, entities))
    return result


class Tokenizer(ABC):
    @abstractmethod
    def tokenize(self, sequence: TokensSequence)->List[TokensGroup]:
        pass

