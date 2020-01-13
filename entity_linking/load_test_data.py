import csv
from typing import List

from entity_linking.utils import (
    PUNCTUATION_SIGNS,
    TEST_FILE_1,
    TEST_FILE_2,
    EntitySequence,
    EntityWord,
    ExtendedEntityWord,
)


def load_entity_sequence_list_from_test_file_1(
    sequences_number: int,
) -> List[EntitySequence]:
    # take only first sequences_number sequences
    result: List[EntitySequence] = []
    cur_seq_id: int = 0

    with open(TEST_FILE_1) as csvfile:
        reader = csv.reader(csvfile, delimiter="\t")

        es: EntitySequence = EntitySequence([], cur_seq_id)
        for cur_row in reader:
            # row is empty - next sentence
            if not cur_row:
                result.append(es)
                if len(result) == sequences_number:
                    break
                es = EntitySequence([], cur_seq_id)
                cur_seq_id += 1
            else:
                if cur_row[1] not in PUNCTUATION_SIGNS:
                    es.sequence.append(
                        EntityWord(cur_row[1], cur_row[2], cur_row[3], cur_row[4])
                    )

    return result


def load_entity_sequence_list_from_test_file_2(
    sequences_number: int,
) -> List[EntitySequence]:
    # take only first sequences_number sequences
    result: List[EntitySequence] = []
    cur_seq_id: int = 0

    with open(TEST_FILE_2) as csvfile:
        reader = csv.reader(csvfile, delimiter="\t")

        es: EntitySequence = EntitySequence([], cur_seq_id)
        for cur_row in reader:
            # row is empty - next sentence
            if not cur_row:
                result.append(es)
                if len(result) == sequences_number:
                    break
                es = EntitySequence([], cur_seq_id)
                cur_seq_id += 1
            # row is not empty - append EntityWord
            else:
                if cur_row[1] not in PUNCTUATION_SIGNS:
                    es.sequence.append(
                        ExtendedEntityWord(
                            cur_row[1],
                            cur_row[3],
                            cur_row[5],
                            cur_row[6],
                            cur_row[2],
                            cur_row[4],
                        )
                    )

    return result


if __name__ == "__main__":
    sequences: List[EntitySequence] = load_entity_sequence_list_from_test_file_1(2)
    print(sequences)

    sequences_extended: List[
        EntitySequence
    ] = load_entity_sequence_list_from_test_file_2(2)
    print(sequences_extended)
