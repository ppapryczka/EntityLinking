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
    parser.add_argument('-r', '--host', required=False, type=str,
                        help="Database & Redis host", default="localhost")

    parser.add_argument('-i', '--input', required=True, type=str,
                        help="Input file")

    # parser.add_argument('-o', '--output', required=True, type=str,
    #                     help="Output file")

    parser.set_defaults(func=lambda x: parser.print_help())

    return parser


def main():
    parser = get_args_parser()
    args = parser.parse_args()
    # mode = args.mode
    host = args.host
    input_file = args.input
    # output_file = args.output
    # logger.info("Mode: {}, input file: {}, output file: {}".format(
    #     mode, input_file, output_file))

    data_processor = DataProcessor(host=host)
    data_processor.process_file(filename=input_file)


if __name__ == "__main__":
    main()
