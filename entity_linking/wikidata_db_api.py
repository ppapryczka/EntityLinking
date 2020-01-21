"""
Module that contains wikidata API build around sqlite3 database. It is use to make Wikidata requests more efficient by
saving results to future use.
"""

import sqlite3
from typing import List

from wikidata.entity import EntityId

from entity_linking.wikidata_web_api import (
    get_pages_for_token_wikidata,
    get_subclasses_for_entity_wikidata,
)


def add_entity_subclasses_to_data_base(
    database_name: str, entity: str, subclasses: List[str]
) -> None:
    """
    Insert into entity table new record for ``entity``, save in sub field ``subclasses``.

    Args:
        database_name: Path to database.
        entity: Name of entity to add, Q{NUM} format.
        subclasses: Subclasses of ``entity``.
    """

    conn = sqlite3.connect(database_name)
    c = conn.cursor()

    subclasses_str = ""
    for sub in subclasses:
        subclasses_str += f"{sub};"

    c.execute(f"""INSERT INTO entity(id, sub) VALUES('{entity}', '{subclasses_str}')""")

    conn.commit()
    conn.close()


def get_subclasses_for_entity_db(database_name: str, entity: str) -> List[str]:
    """
    Check if database is entry for given entity. If so take subclasses from database, if not
    take subclasses from Wikidata additionally adding new entry to database.

    Args:
        database_name: Path to database.
        entity: Name of entity, Q{NUM} format.

    Returns:
        List of subclasses for ``entity``.
    """

    conn = sqlite3.connect(database_name)
    c = conn.cursor()

    c.execute(f"SELECT sub FROM entity WHERE id = '{entity}'")

    result = c.fetchone()
    conn.close()

    # no such entity in db
    if result is None:
        sub = get_subclasses_for_entity_wikidata(EntityId(entity))
        add_entity_subclasses_to_data_base(database_name, entity, sub)
        return sub
    # such entity already in db
    else:
        return result[0].split(";")[:-1]


def add_token_pages_to_data_base(
    database_name: str, token: str, pages: List[str]
) -> None:
    """
    Insert into token table new record for ``token``, save in pages field ``pages``.

    Args:
        database_name: Path to database.
        token: Token to add - plain str.
        pages: Pages for ``token``.
    """

    conn = sqlite3.connect(database_name)
    c = conn.cursor()

    pages_str = ""
    for page in pages:
        pages_str += f"{page};"

    c.execute(f"""INSERT INTO token(id, pages) VALUES('{token}', '{pages_str}')""")

    conn.commit()
    conn.close()


def get_pages_for_token_db(database_name: str, token: str) -> List[str]:
    """
    Check if database is entry for given token. If so take pages from database, if not
    take search for pages in Wikidata additionally adding new entry to database.

    Args:
        database_name: Path to database.
        token: Token to search in Wikidata, plain text.

    Returns:
        List of pages for ``token``.
    """
    # this two sign cause db errors!
    if "'" in token or "\\" in token:
        pages = get_pages_for_token_wikidata(token)
        return pages

    conn = sqlite3.connect(database_name)
    c = conn.cursor()

    c.execute(f"SELECT pages FROM token WHERE id = '{token}'")

    result = c.fetchone()
    conn.close()

    # no such token in db
    if result is None:
        pages = get_pages_for_token_wikidata(token)
        add_token_pages_to_data_base(database_name, token, pages)
        return pages
    # such token already in db
    else:
        return result[0].split(";")[:-1]
