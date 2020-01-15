"""
Module that holds entity classifiers declarations.
"""

import csv
import time
from abc import ABC, abstractmethod
from typing import List

import networkx as nx
import pandas as pd
from sklearn.metrics import confusion_matrix
from wikidata.entity import EntityId

from entity_linking.database_api import WikidataAPI
from entity_linking.load_test_data import get_sequences_from_file
from entity_linking.tokenizer import Tokenizer, WikidataLengthTokenizer
from entity_linking.utils import (NOT_WIKIDATA_ENTITY_SIGN, TokensGroup,
                                  TokensSequence)
from entity_linking.wikidata_graph import (check_if_target_entity_is_in_graph,
                                           create_graph_for_entity)


class EntityClassifier(ABC):
    """
    Abstract class for entity classifier.
    """

    tokenizer: Tokenizer
    wikidata_API: WikidataAPI

    def __init__(self, tokenizer: Tokenizer, wikidata_API: WikidataAPI) -> None:
        self.tokenizer = tokenizer
        self.wikidata_API = wikidata_API

    @abstractmethod
    def classify_sequence(self, sequence: TokensSequence) -> pd.DataFrame:
        """
        Classify ``sequence`` abstract method.

        Args:
            sequence:

        Returns:
            Pandas DataFrame with results.
        """
        pass

    @abstractmethod
    def classify_sequences_from_file(
        self, file_name: str, seq_number: int
    ) -> pd.DataFrame:
        """
        Classify sequences from file ``file_name`` abstract method.

        Args:
            file_name: Name of file with sequences.
            seq_number: Number of sequence to read and classify from file.

        Returns:
            Pandas DataFrame with results.
        """
        pass


class GraphEntityClassifier(EntityClassifier):
    """
    Classifier that uses graphs to classify entities.
    """

    def __init__(self, tokenizer: Tokenizer, wikidata_API: WikidataAPI) -> None:
        super().__init__(tokenizer, wikidata_API)

    def classify_sequence(self, sequence: TokensSequence) -> pd.DataFrame:
        start_time = time.time()
        chosen_tokens: List[TokensGroup] = self.tokenizer.tokenize(sequence)

        token_results = []
        for token in chosen_tokens:
            result: str = NOT_WIKIDATA_ENTITY_SIGN
            for page in token.pages:
                graph: nx.Graph = create_graph_for_entity(
                    EntityId(page), self.wikidata_API
                )

                if check_if_target_entity_is_in_graph(graph):
                    result = page
                    break
            token_results.append(result)

        print(f"{sequence.id} done! ", "time: ", time.time() - start_time)
        return sequence.create_result_table(chosen_tokens, token_results)

    def classify_sequences_from_file(
        self, file_name: str, seq_number: int
    ) -> pd.DataFrame:
        with open(file_name) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter="\t")

            iter = get_sequences_from_file(csv_reader)
            results = []

            for x in range(seq_number):
                if x > 2300:
                    results.append(self.classify_sequence(next(iter)))

            full_result_pd = pd.DataFrame(columns=["original", "prediction"])

            for r in results:
                full_result_pd = full_result_pd.append(r)

            full_result_pd = full_result_pd.reset_index(drop=True)

            print(full_result_pd)
            [[tn, fp], [fn, tp]] = confusion_matrix(
                full_result_pd.loc[:, "original"].tolist(),
                full_result_pd.loc[:, "prediction"].tolist(),
            )

            print("tn", tn)
            print("fp", fp)
            print("fn", fn)
            print("tp", tp)
            print("all", tn + fp + fn + tp)

            return full_result_pd


class ContextGraphEntityClassifier(EntityClassifier):
    """
    Classifier that uses token graphs to create context and classify entities.
    """

    def __init__(self, tokenizer: Tokenizer, wikidata_API: WikidataAPI) -> None:
        super().__init__(tokenizer, wikidata_API)

    def classify_sequence(self, sequence: TokensSequence) -> pd.DataFrame:
        pass

    def classify_sequences_from_file(
        self, file_name: str, seq_number: int
    ) -> pd.DataFrame:
        pass


def result_report(result_df: pd.DataFrame) -> None:
    [[tn, fp], [fn, tp]] = confusion_matrix(
        result_df.loc[:, "original"].tolist(), result_df.loc[:, "prediction"].tolist(),
    )

    print("tn", tn)
    print("fp", fp)
    print("fn", fn)
    print("tp", tp)
    print("all", tn + fp + fn + tp)


if __name__ == "__main__":
    DEFAULT_DATA_BASE: str = "./entity_linking.db"
    api = WikidataAPI(True, DEFAULT_DATA_BASE)
    tokenizer = WikidataLengthTokenizer(2, api)
    test = GraphEntityClassifier(tokenizer, api)
    test.classify_sequences_from_file("../tokens-with-entities-and-tags.tsv", 10000)
