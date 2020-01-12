from typing import Any, List

import pandas as pd

import networkx as nx
from entity_linking.load_test_data import (
    load_entity_sequence_list_from_test_file_1,
    load_entity_sequence_list_from_test_file_2,
)

from entity_linking.tokenizer import (
    simple_tokenize_for_entity_sequence,
    tokenize_using_wikidata_result,
)
from entity_linking.utils import EntitySequence, ExtendedToken
from entity_linking.wikidata_graph import (
    check_if_target_entity_is_in_graph,
    create_graph_for_entity,
)
from wikidata.entity import EntityId
from sklearn.metrics import confusion_matrix


def simple_entity_graph_classifier_for_extended_tokens(
    tokens: List[ExtendedToken],
) -> List[EntityId]:
    tokens_result_entities: List[EntityId] = []
    for t in tokens:
        result_token: Any = None
        for page in t.pages:
            g: nx.Graph = create_graph_for_entity(EntityId(page))
            if check_if_target_entity_is_in_graph(g):
                result_token = EntityId
                break
        tokens_result_entities.append(result_token)

    return tokens_result_entities


def run_simple_graph_classifier_for_entities():
    seq_number: int = 100

    sequences: List[EntitySequence] = load_entity_sequence_list_from_test_file_2(
        seq_number
    )

    """
    1. iterate over sequences
    2. choose tokens
    3. iterate over tokens 
    4. create graph for pages 
    5. check if any target group is in graph 
    6. append result 
    """

    full_result_pd = pd.DataFrame(columns=["original", "prediction"])

    i: int = 0
    for sequence in sequences:

        chosen_tokens = tokenize_using_wikidata_result(2, sequence)

        token_results = []
        for token in chosen_tokens:
            print(sequence.get_token_as_str(token.start, token.end))
            result: str = "_"
            for page in token.pages:
                print(page)
                graph: nx.Graph = create_graph_for_entity(EntityId(page))

                if check_if_target_entity_is_in_graph(graph):
                    result = page
                    break
            token_results.append(result)

        full_result_pd = full_result_pd.append(
            sequence.create_result_table(chosen_tokens, token_results)
        )

        i = i + 1
        print(i)

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


if __name__ == "__main__":

    run_simple_graph_classifier_for_entities()
