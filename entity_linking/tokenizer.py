from typing import List

from entity_linking.utils import EntitySequence, ExtendedToken, Token
from entity_linking.wikidata_api import get_pages_ids_for_given_token


def simple_tokenize_for_entity_sequence(
    token_length: int, sequence: EntitySequence
) -> List[Token]:
    result: List[Token] = []
    for x in range(len(sequence.sequence)):
        if x + token_length < len(sequence.sequence):
            result.append(Token(x, x + token_length))
    return result


def tokenize_using_wikidata_result(
    token_length: int, sequence: EntitySequence
) -> List[ExtendedToken]:
    result: List[ExtendedToken] = []
    for x in range(len(sequence.sequence)):
        if x + token_length < len(sequence.sequence):
            entities = get_pages_ids_for_given_token(
                sequence.get_token_as_str(x, x + token_length)
            )
            if len(entities) > 0:
                result.append(ExtendedToken(x, x + token_length, entities))
    return result
