"""
Module that contains functions design to read data from test files.
"""
import csv
from typing import Iterator, List

import pandas as pd

from entity_linking.utils import (NOT_WIKIDATA_ENTITY_SIGN, ExtendedToken,
                                  Token, TokensSequence)


def load_sequences_from_test_file_without_tags_and_lemmas(
    file_name: str, seq_number: int,
) -> List[TokensSequence]:
    """
    Load sequences from ``file``. Words in this file can't have tags and lemmas.

    Args:
        file_name: Name of input file.
        seq_number: Number of sequences to read from file.

    Returns:
        List of sequences, that contain Token class list.
    """
    # take only first sequences_number sequences
    result: List[TokensSequence] = []
    idx: int = 0

    with open(file_name) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter="\t")

        es: TokensSequence = TokensSequence([], 0)
        for cur_row in csv_reader:
            # row is empty - next sentence
            if not cur_row:
                result.append(es)
                if len(result) == seq_number:
                    break
                es = TokensSequence([], idx)
                idx += 1
            # row not empty - append token to sequence
            else:
                es.sequence.append(
                    Token(cur_row[1], cur_row[2], cur_row[3], cur_row[4])
                )

    return result


def load_sequences_from_test_file_with_lemmas_and_tags(
    file_name: str, seq_number: int,
) -> List[TokensSequence]:
    """
    Load sequences from ``file_name``. Words in this file must have tags and lemmas.

    Args:
        file_name: Name of file with
        seq_number: Number of sequences to read from file.

    Returns:
        List of sequences, that contain ExtendedToken class list.
    """

    # take only first sequences_number sequences
    result: List[TokensSequence] = []
    idx: int = 0

    with open(file_name) as csv_file:
        reader = csv.reader(csv_file, delimiter="\t")

        es: TokensSequence = TokensSequence([], idx)
        for cur_row in reader:
            # row is empty - next sentence
            if not cur_row:
                result.append(es)
                if len(result) == seq_number:
                    break
                es = TokensSequence([], idx)
                idx += 1
            # row not empty - append token to sequence
            else:
                es.sequence.append(
                    ExtendedToken(
                        cur_row[1],
                        cur_row[3],
                        cur_row[5],
                        cur_row[6],
                        cur_row[2],
                        cur_row[4],
                    )
                )

    return result


def get_sequences_from_file(csv_reader) -> Iterator[TokensSequence]:
    """
    Load sequences from in same format as TEST_FILE_2 - with lemmas and tags.
    File must be open before!

    Args:
        csv_reader: CSV reader open by csv.reader.

    Returns:
        Iterator to sequences.
    """
    idx: int = 0
    es: TokensSequence = TokensSequence([], idx)

    for cur_row in csv_reader:
        # row is empty - next sentence
        if not cur_row:
            idx += 1
            yield es
            es = TokensSequence([], idx)

        # row is not empty - append
        else:
            es.sequence.append(
                ExtendedToken(
                    cur_row[1],
                    cur_row[3],
                    cur_row[5],
                    cur_row[6],
                    cur_row[2],
                    cur_row[4],
                )
            )


def get_entities_from_test_file_and_save(
    test_file_name: str, result_file_name: str, sequences_number: int
) -> None:
    """"
    Load sequences from test_file_name using ``get_sequences_from_file`` and take tokens groups that with same
    result entity. Save it first part morph tags to ``result_file_name``.

    Args:
        test_file_name: File with test sequences - it must contain tags and lemmas.
        result_file_name: Result file name.
        sequences_number: Number of sequences to read from ``test_file_name``.
    """
    df = pd.DataFrame()

    # open csv test file
    with open(test_file_name) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter="\t")

        # get iterator and iterate over sequences
        csv_iter = get_sequences_from_file(csv_reader)
        for i in range(sequences_number):
            seq = next(csv_iter)

            entity_morph_tags = []
            last = ""

            for _, w in enumerate(seq.sequence):
                if w.entity_id != NOT_WIKIDATA_ENTITY_SIGN:
                    if w.entity_id == last:
                        entity_morph_tags.append(w.get_first_morph_tags_part())
                    else:
                        if len(entity_morph_tags) > 0:
                            df = df.append(pd.DataFrame([entity_morph_tags]))
                        entity_morph_tags = [w.get_first_morph_tags_part()]
                        last = w.entity_id

            if len(entity_morph_tags) > 0:
                df = df.append(pd.DataFrame([entity_morph_tags]))
            print(i)

    df = df.reset_index(drop=True)
    df.to_csv(result_file_name)
