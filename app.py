from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

# run test
from entity_linking.classification_report import create_report_for_result
from entity_linking.wikidata_api import WikidataAPI, WikidataWebAPI, WikidataDBAPI
from entity_linking.entity_classifier import WikipediaContextGraphEntityClassifier
from entity_linking.tokenizer import WikidataMorphTagsTokenizer


import sys


def run_test_command(input_file: str, seq_number: int, database_name: str):
    api: WikidataAPI

    if database_name != "":
        api = WikidataDBAPI(database_name)
    else:
        api = WikidataWebAPI()

    tokenizer = WikidataMorphTagsTokenizer(api, 2)
    graph_classifier = WikipediaContextGraphEntityClassifier(tokenizer, api, 5, 8)

    result = graph_classifier.classify_sequences_from_file(
        input_file, seq_number
    )

    create_report_for_result(result,
        seq_number,
        input_file,
        f"classifier:{WikidataMorphTagsTokenizer.__name__}, "
        f"tokenizer: {WikipediaContextGraphEntityClassifier.__name__}")


def get_args_parser() -> ArgumentParser:

    parser = ArgumentParser(description='Entity Linking',
                            formatter_class=ArgumentDefaultsHelpFormatter)

    subparsers = parser.add_subparsers()

    test_parser = subparsers.add_parser("test")

    test_parser.add_argument(
        '-i', '--input', required=True, type=str, help="Input file"
    )
    test_parser.add_argument(
        '-N', '--num', required=True, type=int, help="Sequences number"
    )
    test_parser.add_argument(
        '-db', type=str, required=False, default="", help="Path to database",
    )

    '''
    run_parser = subparsers.add_parser("run")

    run_parser.add_argument('-i', '--input', required=True, type=str,
                        help="Input file")

    run_parser.add_argument('-o', '--output', required=True, type=str,
                        help="Output file")
    '''

    parser.set_defaults(func=lambda x: parser.print_help())

    return parser


def main():
    parser = get_args_parser()
    print(sys.argv[1:])
    args = parser.parse_args(sys.argv[1:])

    run_test_command(args.input, args.num, args.db)


if __name__ == "__main__":
    main()
