"""
Module contains function to deal with wikpedia pages using wikipediaapi library.
See: https://pypi.org/project/Wikipedia-API/
"""


import wikipediaapi
from wikidata.entity import EntityId

from entity_linking.utils import (MAX_WIKIPEDIA_PAGE_CONTENT_LEN, MORFEUSZ,
                                  TokensSequence)
from entity_linking.wikidata_web_api import (get_title_in_polish_wikipedia,
                                             get_url_to_polish_wikipedia)


def get_context_similarity_from_wikipedia(
    sequence: TokensSequence, entity: EntityId
) -> float:
    """
    Try to score ``entity`` using context given by ``sequence``. Take wikipedia page link to ``entity``, take
    wikipedia content and try to find similar words between wikipedia page and ``sequence``.

    Args:
        sequence: Sequence from which was taken ``entity``.
        entity: ID od entity given by Q{NUM}.

    Returns:
        Float that describe percent of similar important words between wikipedia page and ``sequence``.
    """

    page_title = get_title_in_polish_wikipedia(entity)

    if page_title is None:
        return 0.0

    page_content = get_site_wikipedia_site_content(page_title)

    m_result = MORFEUSZ.analyse(page_content)

    # simplify morfeusz result - take only first result for token, take only subst and adj tags
    cur_position = 0

    wikipedia_words = []
    for r in m_result:
        if r[1] > cur_position and r[2][2].split(":")[0] in ["subst", "adj"]:
            wikipedia_words.append(r[2][1].split(":")[0].lower())
            cur_position = r[1]

    # take only subst, adj from sequence
    sequence_words = []
    for t in sequence.sequence:
        if t.get_first_morph_tags_part() in ["subst", "adj"]:
            sequence_words.append(t.lemma.lower())

    common_words_num = 0
    for s_w in sequence_words:
        if s_w in wikipedia_words:
            common_words_num += 1

    if len(sequence_words) == 0:
        return 0.0

    return float(common_words_num) / len(sequence_words)


def get_wikipedia_site_title(entity: EntityId):
    """
    Get wikipedia site title which is last part of url of link given in site of ``entity``.

    Args:
        entity: ID of wikidata page which for take title of wikipedia page.

    Returns:
        Title of wikipedia page for ``entity``
    """

    return get_url_to_polish_wikipedia(entity).split("/")[-1]


def get_site_wikipedia_site_content(page_title: str) -> str:
    """
    Get content of wikipedia page using wikipediaapi. Cut result to MAX_WIKIPEDIA_PAGE_CONTENT_LEN, because it
    content can be too long to analyse in rational time.

    Args:
        page_title: Title of wikipedia page.

    Returns:
        Content of wikipedia page for ``page_title``.
    """

    # get all sections from page
    wiki_wiki = wikipediaapi.Wikipedia("pl")
    page = wiki_wiki.page(page_title)

    result = ""

    for x in page.sections:
        result += x.text

    return result[:MAX_WIKIPEDIA_PAGE_CONTENT_LEN]
