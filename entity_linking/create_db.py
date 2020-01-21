"""
Simple script to create database for application.
"""

import argparse
import sqlite3
import sys

from entity_linking.utils import parser_check_if_file_exists


def drop_and_create_database(database_name: str) -> None:
    """
    Create SQLite3 data base with two tables:
    entity: id text, sub text
    token: id text, pages text

    Entity describes subclasses of entity given by id.
    Token describes pages for given token from Wikidata.
    Token pages and entity sub are save in format:
    Q{NUM};...Q{NUM}.

    Args:
        database_name: Path to new database.
    """
    conn = sqlite3.connect(database_name)

    c = conn.cursor()

    # drop table entity
    c.execute("""DROP TABLE IF EXISTS entity""")

    # drop table token
    c.execute("""DROP TABLE IF EXISTS token""")

    # create table entity
    c.execute("""CREATE TABLE entity (id text, sub text)""")

    # create table token
    c.execute("""CREATE TABLE token (id text, pages text)""")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "db_name",
        help="path to database",
        type=lambda x: parser_check_if_file_exists(parser, x),
    )

    args = parser.parse_args(sys.argv[1:])

    drop_and_create_database(args.db_name)

    print(f"Data base created! Path: {args.db_name}")
