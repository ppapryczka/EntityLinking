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

from entity_linking.utils import (
    NOT_WIKIDATA_ENTITY_SIGN,
    ClassificationResult,
    TokensGroup,
    TokensSequence,
)

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
    Search for not existing dir, create it using time and random string as name.

    Returns:
        Path to created report dir.
    """
    # generate report random name
    random_end_part = "".join(
        random.choice(string.ascii_lowercase) for _ in range(REPORT_RANDOM_NAME_LEN)
    )
    # generate date and time file name part
    time_part = time.strftime("%Y_%m_%d_%H_%M_%S")

    # if file exist generate new random end
    while os.path.isdir(f"{REPORT_FOLDER_PREFIX}_{time_part}_{random_end_part}"):
        random_end_part = "".join(
            random.choice(string.ascii_lowercase) for _ in range(REPORT_RANDOM_NAME_LEN)
        )

    # create file
    dir_name = f"{REPORT_FOLDER_PREFIX}_{time_part}_{random_end_part}"
    os.makedirs(dir_name)

    return dir_name


def create_result_data_frame(
    sequence: TokensSequence,
    tokens_groups: List[TokensGroup],
    tokens_groups_entity_results: List[ClassificationResult],
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
        sequence: Sequence of tokens.
        tokens_groups: Chosen tokens groups.
        tokens_groups_entity_results: Result entities for token groups.

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

    tokens_and_results = list(zip(tokens_groups, tokens_groups_entity_results))

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
                    elif (
                        result_entity[x] != test_entity[x]
                        and test_entity[x] == NOT_WIKIDATA_ENTITY_SIGN
                    ):
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
    result_df: pd.DataFrame, seq_number: int, test_file_name: str, method_name: str
) -> None:
    """
    Create new report folder and save there following files:
    - main report file
    - two confusion matrixes
    - ``result_df`` dump to csv file

    Args:
        result_df: Result dataframe for sequences. Format described in ``create_result_data_frame`` function.
        seq_number: Number of sequences read from file.
        test_file_name: Source of sequences to classification.
        method_name: String that describe classification method.
    """

    dir_name = create_report_folder()

    result_df.to_csv(os.path.join(dir_name, REPORT_FULL_RESULT))

    main_report_file_name = os.path.join(dir_name, REPORT_MAIN_FILE)

    with open(main_report_file_name, "w") as main_report_file:
        c_m1 = confusion_matrix(
            result_df.loc[:, "test_classified"].tolist(),
            result_df.loc[:, "result_classified"].tolist(),
        )
        [[tn1, fp1], [fn1, tp1]] = c_m1

        c_m2 = confusion_matrix(
            result_df.loc[:, "test_classified"].tolist(),
            result_df.loc[:, "correct_predict"].tolist(),
        )
        [[tn2, fp2], [fn2, tp2]] = c_m2

        main_report_file.write(f"Classification result for file:\n{test_file_name}\n")
        main_report_file.write(f"Classification method:\n{method_name}\n")
        main_report_file.write(f"Classification sequences:\n{seq_number}\n")
        main_report_file.write("\n")
        main_report_file.write(f"Results for classification(correct position):\n")
        main_report_file.write(f"TN: {tn1}\nFP: {fp1}\nFN: {fn1}\nTP: {tp1}\n")
        main_report_file.write(
            f"Accuracy: {round(float(tn1+tp1)/float(tn1+fp1+fn1+tp1)*100.0, 2)}%\n"
        )
        main_report_file.write(
            f"Precision: {round(float(tp1) / float(tp1+fp1) * 100.0, 2)}%\n"
        )
        main_report_file.write("\n")
        main_report_file.write(
            f"Results for classification(correct position and entity):\n"
        )
        main_report_file.write(f"TN: {tn2}\nFP: {fp2}\nFN: {fn2}\nTP: {tp2}\n")
        main_report_file.write(
            f"Accuracy: {round(float(tn2 + tp2) / float(tn2 + fp2 + fn2 + tp2) * 100.0, 2)}%\n"
        )
        main_report_file.write(
            f"Precision: {round(float(tp2) / float(tp2 + fp2) * 100.0, 2)}%\n"
        )

    save_confusion_matrix_to_dir(
        c_m1, "Classification in same positions", dir_name, REPORT_CONFUSION_MATRIX_1
    )

    save_confusion_matrix_to_dir(
        c_m2, "Classification same entities", dir_name, REPORT_CONFUSION_MATRIX_2
    )


def save_confusion_matrix_to_dir(
    c_matrix: np.array, plot_title: str, dir_name: str, file_name: str
) -> None:
    """
    Create figure for confusion matrix ``c_matrix`` using matplotlib and save to ``dir`` as a ``file_name``.

    Args:
        c_matrix: Confusion matrix.
        plot_title: Name of plot.
        dir_name: Path to dir when will be save plot.
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

    fig_confusion_matrix.savefig(os.path.join(dir_name, file_name), dpi=500)
