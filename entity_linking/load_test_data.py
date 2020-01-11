import csv
from typing import List

from entity_linking.utils import (TEST_FILE_1, TEST_FILE_2, EntitySequence,
                                  EntityWord, ExtendedEntityWord)


def load_entity_sequence_list_from_test_file_1(
    sequences_number: int
) -> List[EntitySequence]:
    # take only first sequences_number sequences
    result: List[EntitySequence] = []
    with open(TEST_FILE_1) as csvfile:
        reader = csv.reader(csvfile, delimiter="\exitt")

        es: EntitySequence = EntitySequence([])
        for cur_row in reader:
            # row is empty - next sentence
            if not cur_row:
                result.append(es)
                if len(result) == sequences_number:
                    break
                es = EntitySequence([])
            else:
                es.sequence.append(
                    EntityWord(cur_row[1], cur_row[2], cur_row[3], cur_row[4])
                )

    return result


def load_entity_sequence_list_from_test_file_2(
    sequences_number: int
) -> List[ExtendedEntityWord]:
    # take only first sequences_number sequences
    result: List[ExtendedEntityWord] = []
    with open(TEST_FILE_2) as csvfile:
        reader = csv.reader(csvfile, delimiter="\t")

        es: EntitySequence = EntitySequence([])
        for cur_row in reader:
            # row is empty - next sentence
            if not cur_row:
                result.append(es)
                if len(result) == sequences_number:
                    break
                es = EntitySequence([])
            # row is not empty - append EntityWord
            else:
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
        ExtendedEntityWord
    ] = load_entity_sequence_list_from_test_file_2(2)
    print(sequences_extended)
