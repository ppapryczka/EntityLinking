"""
Module that contain classification report functions.
"""

import os
import random
import string
import time
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import confusion_matrix

from entity_linking.utils import (NOT_WIKIDATA_ENTITY_SIGN,
                                  ClassificationResult, TokensGroup,
                                  TokensSequence)

# length of random string added to report dir end
REPORT_RANDOM_NAME_LEN: int = 8
# report dir prefix
REPORT_FOLDER_PREFIX: str = "report"
# name of main report file
REPORT_MAIN_FILE: str = "report.txt"
# name for first confusion matrix
REPORT_CONFUSION_MATRIX_1: str = "confusion_matrix_1.png"
# name for second confusion matrix
REPORT_CONFUSION_MATRIX_2: str = "confusion_matrix_2.png"
# name for full result file
REPORT_FULL_RESULT: str = "result.csv"


def create_report_folder():
    """
    Search for not existing dir, create it using time and random string.

    Returns:
        Path to created report dir.
    """
    random_end_part = "".join(
        random.choice(string.ascii_lowercase) for _ in range(REPORT_RANDOM_NAME_LEN)
    )
    time_part = time.strftime("%Y_%m_%d_%H_%M_%S")

    while os.path.isdir(f"{REPORT_FOLDER_PREFIX}_{time_part}_{random_end_part}"):
        random_end_part = "".join(
            random.choice(string.ascii_lowercase) for _ in range(REPORT_RANDOM_NAME_LEN)
        )

    dir_name = f"{REPORT_FOLDER_PREFIX}_{time_part}_{random_end_part}"

    os.makedirs(dir_name)
    return dir_name


def create_result_data_frame(
    sequence: TokensSequence,
    tokens_groups: List[TokensGroup],
    token_groups_entity_results: List[ClassificationResult],
) -> pd.DataFrame:
    """
    Create classification result dataframe for given sequence.
    Created dataframe columns:
        test_entity - ground truth - entity ID
        result_entity - result - entity ID
        test_classified - ground truth - 0 or 1 if test_entity not empty
        result_classified - result - 0 or 1 if result_entity not empty
        correct_predict - true correct predict - test_entity == result_entity and result_classified

    Args:
        sequence:
        tokens_groups:
        token_groups_entity_results:

    Returns:
        Dataframe with columns mentioned above.
    """

    columns = [
        "test_entity",
        "result_entity",
        "test_classified",
        "result_classified",
        "correct_predict",
    ]

    result_df = pd.DataFrame(columns=columns)

    test_entity = []
    result_entity = []
    test_classified = []
    result_classified = []
    correct_predict = []

    for token in sequence.sequence:
        test_entity.append(token.entity_id)

        if token.entity_id != NOT_WIKIDATA_ENTITY_SIGN:
            test_classified.append(1)
            correct_predict.append(0)
        else:
            test_classified.append(0)
            correct_predict.append(0)

        # dummy append
        result_entity.append(NOT_WIKIDATA_ENTITY_SIGN)
        # dummy append
        result_classified.append(0)

    tokens_and_results = list(zip(tokens_groups, token_groups_entity_results))

    def sort_fun(token_and_result):
        return token_and_result[1].score

    tokens_and_results.sort(reverse=True, key=sort_fun)

    for token, result in tokens_and_results:
        if result.result_entity != NOT_WIKIDATA_ENTITY_SIGN:
            empty = True
            for x in range(token.start, token.end + 1):
                if result_entity[x] != NOT_WIKIDATA_ENTITY_SIGN:
                    empty = False
                    break

            if empty:
                for x in range(token.start, token.end + 1):
                    result_entity[x] = result.result_entity
                    result_classified[x] = 1
                    if result_entity[x] == test_entity[x]:
                        correct_predict[x] = 1
                    else:
                        correct_predict[x] = 0

    result_list = list(
        zip(
            test_entity,
            result_entity,
            test_classified,
            result_classified,
            correct_predict,
        )
    )
    result_df = result_df.append(pd.DataFrame(result_list, columns=columns))

    return result_df


def create_report_for_result(
    result_df: pd.DataFrame, seq_number: int, file_name: str
) -> None:
    """
    Create new report folder and save there following files:
    - main report file
    - two confusion matrixes
    - ``result_df`` dump to csv file

    Args:
        result_df: Result dataframe for sequences. Format described in ``create_result_data_frame`` function.
        seq_number: Number of sequences read from file.
        file_name: Source of sequences to classification.
    """

    dir_name = create_report_folder()

    result_df.to_csv(os.path.join(dir_name, REPORT_FULL_RESULT))

    c_m = confusion_matrix(
        result_df.loc[:, "test_classified"].tolist(),
        result_df.loc[:, "result_classified"].tolist(),
    )
    [[tn1, fp1], [fn1, tp1]] = c_m
    save_confusion_matrix_to_dir(
        c_m, "Classification in same positions", dir_name, REPORT_CONFUSION_MATRIX_1
    )

    c_m = confusion_matrix(
        result_df.loc[:, "test_classified"].tolist(),
        result_df.loc[:, "correct_predict"].tolist(),
    )
    [[tn2, fp2], [fn2, tp2]] = c_m
    save_confusion_matrix_to_dir(
        c_m, "Classification same entities", dir_name, REPORT_CONFUSION_MATRIX_2
    )


def save_confusion_matrix_to_dir(
    c_matrix: np.array, plot_title: str, dir: str, file_name: str
) -> None:
    """
    Create figure for confusion matrix ``c_matrix`` using matplotlib and save to ``dir`` as a ``file_name``.

    Args:
        c_matrix: Confusion matrix.
        plot_title: Name of plot.
        dir: Path to dir when will be save plot.
        file_name: Plot save file name.
    """

    fig_confusion_matrix, ax = plt.subplots()

    axis = sns.heatmap(
        c_matrix,
        annot=True,
        square=True,
        cmap=sns.color_palette("Blues"),
        xticklabels=["0", "1"],
        yticklabels=["0", "1"],
        ax=ax,
        fmt="d",
    )

    axis.set_ylabel("True label")
    axis.set_xlabel("Predicted label")
    axis.set_title(plot_title)
    # rotate class labels
    for tick in axis.get_xticklabels():
        tick.set_rotation(45)
    for tick in axis.get_yticklabels():
        tick.set_rotation(0)

    fig_confusion_matrix.savefig(os.path.join(dir, file_name), dpi=500)
