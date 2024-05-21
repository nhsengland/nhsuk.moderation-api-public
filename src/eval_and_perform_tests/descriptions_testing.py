# This is a script to test the performance of the descriptions rule. The script reads in data from a csv,
# and runs this data through the descriptions rule and records the results.
# The time taken, precision, recall and f1 score are/can be printed to the terminal.
# To aid model evaluation, the false negatives and false positives can be logged in a csv by
# uncommenting the logging functions at the bottom of the script. Remember to change the file names
# if you do not want to overwite the existing csvs
# Before running the test suite on a large volume of data, check which endpoint is being queried in
# the descriptions function - only sumbit large volumes of data to non-production endpoints or add a
# sleep to the for loop to avoid affecting live traffic
import timeit
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from helpers.common_functions import load_env_variables
from modules.descriptor_rule import descriptor_rule

published_data = pd.read_csv("./src/data/testing_data/some_publishable_data.csv")
rejected_data = pd.read_csv("./src/data/testing_data/some_unpublishable_data.csv")
load_env_variables()


def get_descriptions_results(data: pd.DataFrame):
    """This function takes a pandas dataframe which must have these required columns:
    Comment ID, Comment Title, Comment Text. The function passes this information to the
    names rule and records the results
    Arguments:
        data: a pandas dataframe of reviews with the required columns
    Returns:
        results: a list of 1 or 0 to indicate whether the rule was triggered
        descriptors: a list of lists of descriptors returned by the model
        times: a list of processing times for each review
        review_ids: a list of ids of the reviews which were run through the descriptor rule
    """
    results = []
    times = []
    review_ids = []
    descriptors = []
    for i, row in data.iterrows():
        title = row["Comment Title"]
        title = title.replace("’", "'")
        comment = row["Comment Text"]
        comment = comment.replace("’", "'")

        t1 = timeit.default_timer()
        title_result = descriptor_rule(title.lower())
        comment_result = descriptor_rule(comment.lower())
        t2 = timeit.default_timer()
        time_taken = t2 - t1

        combined_result = max(title_result[0], comment_result[0])
        times.append(time_taken)
        results.append(combined_result)
        descriptors.append(title_result[1] + comment_result[1])
        review_ids.append(row["Comment ID"])

    return results, descriptors, times, review_ids


(publishable_results, pub_descriptors, pub_times, pub_ids) = get_descriptions_results(
    published_data
)
(rejectable_results, rej_descriptors, rej_times, rej_ids) = get_descriptions_results(
    rejected_data
)

expected_publishable_output = [0] * len(publishable_results)
expected_rejectable_output = [1] * len(rejectable_results)

fp_descriptors = sum(
    [abs(x - y) for x, y in zip(publishable_results, expected_publishable_output)]
)
fn_descriptors = sum(
    [abs(x - y) for x, y in zip(rejectable_results, expected_rejectable_output)]
)

print("Publishable results: ", publishable_results)
print("Rejectable results: ", rejectable_results)
print("TP descriptors: ", sum(rejectable_results))
print(
    "TN descriptors: ", sum([x == 0 for x in publishable_results])
)  # counts the number of 0s
print("FP descriptors: ", fp_descriptors)
print("FN descriptors: ", fn_descriptors)

my_results = publishable_results + rejectable_results
true_data = expected_publishable_output + expected_rejectable_output

print(f"Precision: {precision_score(true_data, my_results)}")
print(f"Recall: {recall_score(true_data, my_results)}")
print(f"F1 score: {f1_score(true_data, my_results)}")

cm = confusion_matrix(true_data, my_results)
disp = ConfusionMatrixDisplay(confusion_matrix=cm)
disp.plot()
plt.show()


def log_false_negs(results: List[int], review_ids: List[str], path_to_save: str):
    fn = []
    for result, comment_id in zip(results, review_ids):
        if result == 0:
            fn.append(comment_id)
    fn_reviews = rejected_data[rejected_data["Comment ID"].isin(fn)]
    fn_reviews.to_csv(path_to_save)


def log_false_pos(
    results: List[str], desc: List[List[str]], review_ids: List[str], path_to_save: str
):
    fp = []
    fp_desc = []
    for result, description, comment_id in zip(results, desc, review_ids):
        if result == 1:
            fp.append(comment_id)
            fp_desc.append(description)
    fp_reviews = published_data[published_data["Comment ID"].isin(fp)]
    fp_reviews = fp_reviews.assign(descriptor=fp_desc)
    fp_reviews.to_csv(path_to_save)


# CSV IS OVERWRITTEN ON EACH RUN OF THE TEST SUITE
# Specify a new path to avoid this
log_false_negs(
    rejectable_results, rej_ids, "./src/data/testing_data/false_neg_desc_reviews.csv"
)

# CSV IS OVERWRITTEN ON EACH RUN OF THE TEST SUITE
# Specify a new path to avoid this
log_false_pos(
    publishable_results,
    pub_descriptors,
    pub_ids,
    "./src/data/testing_data/false_pos_desc_reviews.csv",
)
