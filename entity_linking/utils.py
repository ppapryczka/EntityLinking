"""
Module with tools, constants and common class declarations.
"""
import argparse
import os
from dataclasses import dataclass
from typing import List

import morfeusz2
from wikidata.entity import EntityId

# test file 2 name - with extended data: lemmas and tags, ATTENTION! it is too big to read full
TEST_FILE_2: str = "tokens-with-entities-and-tags.tsv"

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

# sign for word not in Polish wikidata in test set
NOT_WIKIDATA_ENTITY_SIGN: str = "_"

# Entity Wikimedia disambiguation page, this page go to entity Q30642 and Q11862829 - this cause errors
DISAMBIGUATION_PAGE: EntityId = EntityId("Q4167410")

# tokens groups that occur most often
BEST_TOKEN_GROUPS: List[List[str]] = [
    ["subst"],
    ["subst", "subst"],
    ["subst", "adj"],
    ["adj"],
    ["adj", "subst"],
    ["subst", "subst", "subst"],
    ["num"],
    ["adj", "subst", "adj"],
]

# default number of processes to run
DEFAULT_PROCESSES_NUMBER: int = 8
# default score threshold for WikipediaContextGraphEntityClassifier
WIKIPEDIA_SIMILARITY_THRESHOLD: float = 0.1


# default graph levels
MAX_DEPTH_LEVEL: int = 5

# ID of "instance of" property
ID_INSTANCE_OF: str = "P31"
# ID of "subclass of" property
ID_SUBCLASS_OF: str = "P279"
# ID of facet of
ID_FACET_OF: str = "P1269"

# address of wikidata
WIKIDATA_URL: str = "https://www.wikidata.org/wiki/"
# address of wikidata sparql API
WIKIDATA_URL_SPARQL: str = 'https://query.wikidata.org/sparql'
# default max results
DEFAULT_RESULTS_LIMIT: int = 5
# user agent
USER_AGENT: str = "EntityLinking/1.0 (https://github.com/ppapryczka/EntityLinking) Python/Wikidata/0.6.1"

# it is important that it must be global object! It cause strange memory leak!
MORFEUSZ: morfeusz2.Morfeusz = morfeusz2.Morfeusz()
# max length of content from wikipedia site.
MAX_WIKIPEDIA_PAGE_CONTENT_LEN: int = 1000


def parser_check_if_file_exists(parser: argparse.ArgumentParser, file_path: str) -> str:
    """
    Check if file exists - if not call parser.error, else return ``file_path``
    as a result.

    Args:
        parser: Command parser.
        file_path: Path to file.
    """
    if not os.path.isfile(file_path):
        return file_path
    else:
        parser.error(f"The file {file_path} doesn't exist!")


@dataclass
class Token:
    """
    Token - description of single word to classification.

    Attributes:
        token_value: Word in original form.
        preceding_token: 1 - token was preceded by a blank character, 0 - otherwise
        link_title: title of the Wikidata article
        entity_id: ID of the entity in Wikidata
        lemma: Lemma of ``token_value``
        morph_tags: Morphological tags of ``token_value``.
    """

    token_value: str
    preceding_token: int
    link_title: str
    entity_id: str
    lemma: str
    morph_tags: str

    def get_first_morph_tags_part(self) -> str:
        """
        Get first, most significant part of token produced
        by Morfeusz.

        Returns:
            First morphological tag as str.
        """
        return self.morph_tags.split(":")[0]


@dataclass
class TokensGroup:
    """
    Group of tokens from sequence chosen to classification.

    Attributes:
        start: ID of start token from sequence.
        end: ID of end token from sequence.
        token: Value to classification.
        pages: IDs of pages from wikidata for this tokens group.
    """

    start: int
    end: int
    token: str
    pages: List[str]


@dataclass
class ClassificationResult:
    """
    Description of classification result for TokensGroup.

    Attributes:
        result_entity: Result wikidata ID of token.
        score: Score of classification.
    """

    result_entity: str
    score: float

    def __init__(self, result_entity: str, score: float = 0.0) -> None:
        """
        Set class attributes.

        Args:
            result_entity: Result wikidata ID of token.
            score: Score of classification.
        """
        self.result_entity = result_entity
        self.score = score


@dataclass
class TokensSequence:
    """
    Sequence build from Token objects.

    Attributes.
        sequence: List of tokens.
        id: ID of sequence, useful to identification and progress reporting.
    """

    sequence: List[Token]
    id: int

    def get_token_str_original_form(self, start: int, end: int) -> str:
        """
        Take ``start`` and ``end`` and return string representation of
        such range from original form.

        Args:
            start: Start of token group.
            end: End of token group.

        Returns:
            Token as string from its original form.
        """
        result = ""
        for i in range(start, end):
            result += self.sequence[i].token_value + " "

        return result[:-1]

    def get_token_str_lemma_form(self, start: int, end: int) -> str:
        """
        Take ``start`` and ``end`` and return string representation of
        such range from original form.

        Args:
            start: Start of token group.
            end: End of token group.

        Returns:
            Token as string from its original form.
        """
        result = ""
        for i in range(start, end):
            result += self.sequence[i].lemma + " "

        return result[:-1]

    def append(self, token: Token) -> None:
        """
        Add ``token`` to sequence list.

        Args:
            token: Token to add.
        """
        self.sequence.append(token)
