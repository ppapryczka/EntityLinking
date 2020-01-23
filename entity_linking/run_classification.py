from typing import Union

from entity_linking.classification_report import create_report_for_result
from entity_linking.entity_classifier import (
    NoContextGraphEntityClassifier, WikipediaContextGraphEntityClassifier)
from entity_linking.tokenizer import (WikidataLengthTokenizer,
                                      WikidataMorphTagsTokenizer)
from entity_linking.wikidata_api import (WikidataAPI, WikidataDBAPI,
                                         WikidataWebAPI)


def run_classification(
    tokenizer_init,
    token_length: int,
    classifier_init,
    graph_levels: int,
    processes_number: int,
    seq_number: int,
    test_file: str,
    data_base_name: Union[str, None],
) -> None:
    api: WikidataAPI
    if data_base_name:
        api = WikidataDBAPI(data_base_name)
    else:
        api = WikidataWebAPI(False)

    tokenizer = tokenizer_init(api, token_length)
    classifier = classifier_init(tokenizer, api, graph_levels, processes_number)

    result = classifier.classify_sequences_from_file(test_file, seq_number)

    create_report_for_result(
        result,
        seq_number,
        test_file,
        f"classifier:{classifier_init.__name__}, tokenizer: {tokenizer_init.__name__}",
    )


if __name__ == "__main__":
    test_file_name: str = "../tokens-with-entities-and-tags.tsv"

    data_base_name: str = "./entity_linking.db"

    run_classification(
        WikidataLengthTokenizer,
        2,
        WikipediaContextGraphEntityClassifier,
        5,
        10,
        1000,
        test_file_name,
        data_base_name,
    )
