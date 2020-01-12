from dataclasses import dataclass
from typing import List
import pandas as pd

# test file 1 name, ATTENTION! it is too big to read full
TEST_FILE_1: str = "../tokens-with-entities.tsv"
# test file 2 name - with extended data, ATTENTION! it is too big to read full
TEST_FILE_2: str = "../tokens-with-entities-and-tags.tsv"
# number of full sequences to read
SEQUENCE_NUMBER_TO_READ: int = 100000
# target entities
TARGET_ENTITIES: List[str] = [
    # human
    "Q5",
    # geographic location
    "Q2221906",
    # academic discipline
    "Q11862829",
    # anatomical structure
    "Q4936952",
    # occupation
    "Q12737077",
    # vehicle model
    "Q29048322",
    # construction
    "Q811430",
    # written work
    "Q47461344",
    # astronomical object
    "Q6999",
    # clothing
    "Q11460",
    # taxon
    "Q16521",
    # mythical entity
    "Q24334685",
    # type of sport
    "Q31629",
    # supernatural being
    "Q28855038",
    # liquid
    "Q11435",
    # political system
    "Q28108",
    # group of living things
    "Q16334298",
    # chemical entity
    "Q43460564",
    # publication
    "Q732577",
    # landform
    "Q271669",
    # language
    "Q34770",
    # unit
    "Q2198779",
    # physico-geographical object
    "Q20719696",
    # intellectual work
    "Q15621286",
    # tool
    "Q39546",
    # organism
    "Q7239",
    # food
    "Q2095",
]
# Punctuation signs to omit
PUNCTUATION_SIGNS: List[str] = [
    ";",
    ",",
    ":",
    "-",
    ".",
    "!",
    "?",
    "(",
    ")",
    "-",
    "...",
    '"',
    "–",
]


@dataclass
class EntityWord:
    token: str
    preceding_token: int
    link_title: str
    entity_id: str


@dataclass
class ExtendedEntityWord(EntityWord):
    lemma: str
    morph_tags: str


@dataclass
class Token:
    start: int
    end: int


@dataclass
class ExtendedToken(Token):
    pages: List[str]


@dataclass
class EntitySequence:
    sequence: List[EntityWord]

    def get_token_as_str(self, start: int, end: int) -> str:
        result = ""
        for i in range(start, end):
            result += self.sequence[i].token + " "

        return result[:-1]

    def create_result_table(
        self, tokens: List[Token], results: List[str]
    ) -> pd.DataFrame:
        result_df = pd.DataFrame(columns=["original", "prediction"],)

        assert len(tokens) == len(results)

        if len(tokens) > 0:
            cur_index: int = 0

            for t_idx, t in enumerate(tokens):
                while cur_index < t.start:
                    ground_truth = self.sequence[cur_index].entity_id != "_"
                    if ground_truth:
                        ground_truth = 1
                    else:
                        ground_truth = 0

                    result_df = result_df.append(
                        pd.DataFrame(
                            [[ground_truth, 0]], columns=["original", "prediction"]
                        )
                    )
                    cur_index = cur_index + 1

                while cur_index < t.end:
                    ground_truth = self.sequence[cur_index].entity_id != "_"
                    if ground_truth:
                        ground_truth = 1
                    else:
                        ground_truth = 0

                    prediction = results[t_idx] != "_"
                    if prediction:
                        prediction = 1
                    else:
                        prediction = 0

                    result_df = result_df.append(
                        pd.DataFrame(
                            [[ground_truth, prediction]],
                            columns=["original", "prediction"],
                        )
                    )
                    cur_index = cur_index + 1

            while cur_index < len(self.sequence):
                ground_truth = self.sequence[cur_index].entity_id != "_"

                if ground_truth:
                    ground_truth = 1
                else:
                    ground_truth = 0

                result_df = result_df.append(
                    pd.DataFrame(
                        [[ground_truth, 0]], columns=["original", "prediction"]
                    )
                )
                cur_index = cur_index + 1

        return result_df
