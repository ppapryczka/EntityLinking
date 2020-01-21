"""
Module that holds entity classifiers declarations.
"""

import time
from abc import ABC, abstractmethod
from multiprocessing import Pool
from typing import List

import networkx as nx
import pandas as pd
from wikidata.entity import EntityId

from entity_linking.classification_report import create_result_data_frame
from entity_linking.graph_wikidata import (
    MAX_DEPTH_LEVEL,
    check_if_target_entity_is_in_graph,
    create_graph_for_entity,
    get_graph_score,
)
from entity_linking.load_test_data import (
    load_sequences_from_test_file_with_lemmas_and_tags,
)
from entity_linking.tokenizer import Tokenizer
from entity_linking.utils import (
    DEFAULT_PROCESSES_NUMBER,
    NOT_WIKIDATA_ENTITY_SIGN,
    WIKIPEDIA_SIMILARITY_THRESHOLD,
    ClassificationResult,
    TokensGroup,
    TokensSequence,
)
from entity_linking.wikdata_api import WikidataAPI
from entity_linking.wikipedia_api import get_context_similarity_from_wikipedia


class EntityClassifier(ABC):
    """
    Abstract class for entity classifier.
    """

    max_graph_levels: int
    tokenizer: Tokenizer
    wikidata_api: WikidataAPI
    processes_num: int

    def __init__(
        self,
        tokenizer: Tokenizer,
        wikidata_api: WikidataAPI,
        max_graph_levels: int = MAX_DEPTH_LEVEL,
        processes_num: int = DEFAULT_PROCESSES_NUMBER,
    ) -> None:
        """
        Set object attributes.

        Args:
            tokenizer: Tokenizer use to tokenize sequences.
            wikidata_api: API to get from wikidata.
            max_graph_levels: Max levels of graph created to find possible entities.
            processes_num: All classifier uses multiprocessing - number of processes.
        """

        self.tokenizer = tokenizer
        self.wikidata_api = wikidata_api
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


class NoContextGraphEntityClassifier(EntityClassifier):
    def __init__(
        self,
        tokenizer: Tokenizer,
        wikidata_api: WikidataAPI,
        max_graph_levels: int,
        processes_num: int,
    ) -> None:
        """
        Set object attributes.

        Args:
            tokenizer: Tokenizer use to tokenize sequences.
            wikidata_api: API to get from wikidata.
            max_graph_levels: Max levels of graph created to find possible entities.
            processes_num: All classifier uses multiprocessing - number of processes.
        """
        super().__init__(tokenizer, wikidata_api, max_graph_levels, processes_num)

    def classify_sequence(self, sequence: TokensSequence) -> pd.DataFrame:
        """
        Classify ``sequence`` using graph created from wikidata data
        and return full result dataframe using ``create_result_data_frame`` function.

        Args:
            sequence: Sequence to classify entities.

        Returns:
            Pandas DataFrame with classification results.
        """
        # simple function to sort classification result by score
        def sort_fun(cr: ClassificationResult):
            return cr.score

        start_time = time.time()

        # tokenize
        chosen_tokens: List[TokensGroup] = self.tokenizer.tokenize(sequence)

        # iterate over chosen tokens create graph and check if it
        # contains any of target entities
        classify_result: List[ClassificationResult] = []

        for token in chosen_tokens:
            graph_results = [ClassificationResult(NOT_WIKIDATA_ENTITY_SIGN)]

            for page in token.pages:
                graph: nx.Graph = create_graph_for_entity(
                    EntityId(page), self.wikidata_api, self.max_graph_levels
                )

                if check_if_target_entity_is_in_graph(graph):
                    score = get_graph_score(graph, EntityId(page))
                    graph_results.append(ClassificationResult(page, score))

            # sort by score
            graph_results.sort(reverse=True, key=sort_fun)

            classify_result.append(graph_results[0])

        print(f"{sequence.id} done!", "Time: ", time.time() - start_time)

        return create_result_data_frame(sequence, chosen_tokens, classify_result)

    def classify_sequences_from_file(
        self, file_name: str, seq_number: int
    ) -> pd.DataFrame:
        sequences = load_sequences_from_test_file_with_lemmas_and_tags(
            file_name, seq_number
        )

        with Pool(self.processes_num) as p:
            map_results = p.map(self.classify_sequence, sequences)

        result_df = pd.DataFrame()

        for r in map_results:
            result_df = result_df.append(r)

        result_df = result_df.reset_index(drop=True)
        return result_df

    def classify_sequence_get_chosen_tokens(self, sequence: TokensSequence) -> List:
        # TODO!
        pass


class WikipediaContextGraphEntityClassifier(EntityClassifier):
    """
    Classifier that uses wikpedia site of entity to create context and classify entities.
    """

    score_threshold: float

    def __init__(
        self,
        tokenizer: Tokenizer,
        wikidata_api: WikidataAPI,
        max_graph_levels: int,
        processes_num: int,
        score_threshold: float = WIKIPEDIA_SIMILARITY_THRESHOLD,
    ) -> None:
        """
        Set object attributes.

        Args:
            tokenizer: Tokenizer use to tokenize sequences.
            wikidata_api: API to get from wikidata.
            max_graph_levels: Max levels of graph created to find possible entities.
            processes_num: All classifier uses multiprocessing - number of processes.
            score_threshold: Score threshold for wikipedia page similarity.
        """
        super().__init__(tokenizer, wikidata_api, max_graph_levels, processes_num)
        self.score_threshold = score_threshold

    def classify_sequence(self, sequence: TokensSequence) -> pd.DataFrame:
        def sort_fun(cr: ClassificationResult):
            return cr.score

        start_time = time.time()

        # tokenize
        chosen_tokens: List[TokensGroup] = self.tokenizer.tokenize(sequence)

        # iterate over chosen tokens create graph and check if it
        # contains any of target entities
        classify_result: List[ClassificationResult] = []

        for token in chosen_tokens:
            graph_results = [ClassificationResult(NOT_WIKIDATA_ENTITY_SIGN)]

            for page in token.pages:
                graph: nx.Graph = create_graph_for_entity(
                    EntityId(page), self.wikidata_api, self.max_graph_levels
                )

                if check_if_target_entity_is_in_graph(graph):
                    score = get_context_similarity_from_wikipedia(
                        sequence, EntityId(page)
                    )
                    graph_results.append(ClassificationResult(page, score))

                    if score > self.score_threshold:
                        break

            graph_results.sort(reverse=True, key=sort_fun)

            if graph_results[0].score < self.score_threshold:
                classify_result.append(ClassificationResult(NOT_WIKIDATA_ENTITY_SIGN))
            else:
                classify_result.append(graph_results[0])

        print(f"{sequence.id} done! ", "Time: ", time.time() - start_time)

        return create_result_data_frame(sequence, chosen_tokens, classify_result)

    def classify_sequences_from_file(
        self, file_name: str, seq_number: int
    ) -> pd.DataFrame:
        sequences = load_sequences_from_test_file_with_lemmas_and_tags(
            file_name, seq_number
        )

        with Pool(self.processes_num) as p:
            map_results = p.map(self.classify_sequence, sequences)

        result_df = pd.DataFrame()

        for r in map_results:
            result_df = result_df.append(r)

        result_df = result_df.reset_index(drop=True)

        return result_df

    def classify_sequence_get_chosen_tokens(self, sequence: TokensSequence) -> List:
        # TODO!
        pass
