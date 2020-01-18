"""
Module that holds entity classifiers declarations.
"""

import csv
import time
from abc import ABC, abstractmethod
from typing import List, Union

import networkx as nx
import pandas as pd
from wikidata.entity import EntityId
from multiprocessing import Pool

from entity_linking.classification_report import create_result_data_frame
from entity_linking.database_api import WikidataAPI
from entity_linking.load_test_data import (
    get_sequences_from_file,
    load_sequences_from_test_file_with_lemmas_and_tags,
)
from entity_linking.tokenizer import Tokenizer
from entity_linking.utils import (
    NOT_WIKIDATA_ENTITY_SIGN,
    ClassificationResult,
    TokensGroup,
    TokensSequence,
    DEFAULT_PROCESSES_NUMBER,
)
from entity_linking.wikidata_graph import (
    check_if_target_entity_is_in_graph,
    create_graph_for_entity,
    get_graph_score,
    MAX_DEPTH_LEVEL,
)


class EntityClassifier(ABC):
    """
    Abstract class for entity classifier.
    """

    max_graph_levels: int
    tokenizer: Tokenizer
    wikidata_API: WikidataAPI
    processes_num: int

    def __init__(
        self,
        tokenizer: Tokenizer,
        wikidata_API: WikidataAPI,
        max_graph_levels: int = MAX_DEPTH_LEVEL,
        processes_num: int = DEFAULT_PROCESSES_NUMBER,
    ) -> None:
        self.tokenizer = tokenizer
        self.wikidata_API = wikidata_API
        self.max_graph_levels = max_graph_levels
        self.processes_num = processes_num

    @abstractmethod
    def classify_sequence(self, sequence: TokensSequence) -> pd.DataFrame:
        """
        Classify ``sequence`` and return full result dataframe.

        Args:
            sequence: Sequence to classify entities.

        Returns:
            Pandas DataFrame with classification results.
        """
        pass

    @abstractmethod
    def classify_sequences_from_file(
        self, file_name: str, seq_number: int
    ) -> pd.DataFrame:
        """
        Classify sequences from file ``file_name`` and return result pandas dataframe.

        Args:
            file_name: Name of file with sequences.
            seq_number: Number of sequence to read and classify from file.

        Returns:
            Pandas DataFrame with classification results.
        """
        pass

    @abstractmethod
    def classify_sequence_get_chosen_tokens(self, sequence: TokensSequence) -> List:
        """
        Classify sequence from ``sequence`` and return chosen tokens and classification result only.

        Args:
            sequence: Sequence to classify entities.

        Returns:
            List of chosen tokens and result entities.
        """
        pass


class MultiProcessGraphEntityClassifier(EntityClassifier):
    def __init__(
        self,
        tokenizer: Tokenizer,
        wikidata_API: WikidataAPI,
        max_graph_levels: int,
        processes_num: int,
    ) -> None:
        super().__init__(tokenizer, wikidata_API, max_graph_levels, processes_num)

    def classify_sequence(self, sequence: TokensSequence) -> pd.DataFrame:
        start_time = time.time()

        # tokenize
        chosen_tokens: List[TokensGroup] = self.tokenizer.tokenize(sequence)

        # iterate over chosen tokens create graph and check if it
        # contains any of target entities
        classify_result: List[ClassificationResult] = []

        for token in chosen_tokens:
            graph_result = ClassificationResult(NOT_WIKIDATA_ENTITY_SIGN)
            for page in token.pages:
                graph: nx.Graph = create_graph_for_entity(
                    EntityId(page), self.wikidata_API, self.max_graph_levels
                )

                if check_if_target_entity_is_in_graph(graph):
                    score = get_graph_score(graph, page)
                    graph_result = ClassificationResult(page, score)
                    break
            classify_result.append(graph_result)

        print(f"{sequence.id} done! ", "time: ", time.time() - start_time)

        return create_result_data_frame(sequence, chosen_tokens, classify_result)

    def classify_sequences_from_file(
        self, file_name: str, seq_number: int
    ) -> pd.DataFrame:
        sequences = load_sequences_from_test_file_with_lemmas_and_tags(
            file_name, seq_number
        )

        result_df = pd.DataFrame()

        with Pool(self.processes_num) as p:
            map_results = p.map(self.classify_sequence, sequences)

        result_df = pd.DataFrame()

        for r in map_results:
            result_df = result_df.append(r)

        result_df = result_df.reset_index(drop=True)
        return result_df

    def classify_sequence_get_chosen_tokens(self, sequence: TokensSequence) -> List:
        start_time = time.time()

        # tokenize
        chosen_tokens: List[TokensGroup] = self.tokenizer.tokenize(sequence)

        # iterate over chosen tokens create graph and check if it
        # contains any of target entities
        classify_result: List[ClassificationResult] = []

        for token in chosen_tokens:
            graph_result = ClassificationResult(NOT_WIKIDATA_ENTITY_SIGN)

            # iterate over pages
            for page in token.pages:
                # create graph for page
                graph: nx.Graph = create_graph_for_entity(
                    EntityId(page), self.wikidata_API, self.max_graph_levels
                )
                # check if graph contains target entity
                if check_if_target_entity_is_in_graph(graph):
                    score = get_graph_score(graph, page)
                    graph_result = ClassificationResult(page, score)
                    break
            classify_result.append(graph_result)

        print(f"{sequence.id} done! ", "time: ", time.time() - start_time)

        fun_result = []

        for token, result in zip(chosen_tokens, classify_result):
            if result != NOT_WIKIDATA_ENTITY_SIGN:
                fun_result.append((token, result))

        return fun_result


class ContextGraphEntityClassifier(EntityClassifier):
    """
    Classifier that uses token graphs to create context and classify entities.
    """

    def __init__(
        self, tokenizer: Tokenizer, wikidata_API: WikidataAPI, max_graph_levels: int
    ) -> None:
        super().__init__(tokenizer, wikidata_API, max_graph_levels)

    def classify_sequence(self, sequence: TokensSequence) -> pd.DataFrame:
        pass

    def classify_sequences_from_file(
        self, file_name: str, seq_number: int
    ) -> pd.DataFrame:
        pass
