from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from entity_linking.maintenance.logger import get_logger
from entity_linking.wiki.data_processor import DataProcessor
from entity_linking.wiki.graph import GraphBuilder


def get_args_parser() -> ArgumentParser:
    parser = ArgumentParser(description='Entity Linking',
                            formatter_class=ArgumentDefaultsHelpFormatter)

    # parser.add_argument('mode',
    #                     type=int,
    #                     help="App mode:0(train), 1(test), 2(run)")
    #
    # parser.add_argument('-i', '--input', required=True, type=str,
    #                     help="Input file")
    #
    # parser.add_argument('-o', '--output', required=True, type=str,
    #                     help="Output file")

    parser.set_defaults(func=lambda x: parser.print_help())

    return parser


def main():
    logger = get_logger("app")
    parser = get_args_parser()
    args = parser.parse_args()
    # mode = args.mode
    # input_file = args.input
    # output_file = args.output
    # logger.info("Mode: {}, input file: {}, output file: {}".format(
    #     mode, input_file, output_file))

    data_processor = DataProcessor()
    data_processor.store_token("Krzysztof Krawczyk")
    entity = GraphBuilder._get_entity_node(entity_id="Q1380592")
    logger.info("Krzysztof Krawczyk (Q1380592) qualified: {}".format(entity.qualified))


if __name__ == "__main__":
    main()
