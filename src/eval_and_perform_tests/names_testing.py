# This is a script to test the performance of the names rule. The script reads in data from a csv,
# takes a random sample and runs this data through the names rule and records the results.
# The time taken, precision, recall and f1 score is printed to the terminal.
# To aid model evaluation, the false negatives and false positives can be logged in a csv by
# uncommenting the logging functions at the bottom of the script. Remember to change the file names
# if you do not want to overwite the existing csvs
# Before running the test suite on a large volume of data, check which endpoint is being queried in
# the names_rule function - only sumbit large volumes of data to non-production endpoints or add a
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

from modules.names_rule import names_rule

published_data = pd.read_csv("./src/data/testing_data/some_publishable_data.csv")
rejected_data = pd.read_csv("./src/data/testing_data/some_unpublishable_data.csv")

RANDOMSEED = 12
rejected_data = rejected_data.sample(n=1, random_state=RANDOMSEED)
published_data = published_data.sample(n=1, random_state=RANDOMSEED)


def get_names_results(data: pd.DataFrame):
    """This function takes a pandas dataframe which must have these required columns:
    Comment ID, Comment Title, Comment Text, Org Name. The function passes this information to the
    names rule and records the results
    Arguments:
        data: a pandas dataframe of reviews with the required columns
    Returns:
        results: a list of 1 or 0 to indicate whether the rule was triggered
        names: a list of lists of names returned by the model
        review_ids: a list of ids of the reviews which were run through the names rule
    """
    results = []
    times = []
    review_ids = []
    names = []
    for i, row in data.iterrows():
        title = row["Comment Title"]
        title = title.replace("’", "'")
        comment = row["Comment Text"]
        comment = comment.replace("’", "'")
        org_name = row["Org Name"]
        org_name = org_name.replace("’", "'")

        t1 = timeit.default_timer()
        title_result = names_rule(title, org_name)
        comment_result = names_rule(comment, org_name)
        t2 = timeit.default_timer()
        time_taken = t2 - t1

        combined_result = max(title_result[0], comment_result[0])
        times.append(time_taken)
        results.append(combined_result)
        names.append(title_result[1] + comment_result[1])
        review_ids.append(row["Comment ID"])

    return results, names, times, review_ids


(positive_results, pos_names, pos_times, positive_review_ids) = get_names_results(
    rejected_data
)
(negative_results, neg_names, neg_times, negative_review_ids) = get_names_results(
    published_data
)

# Print timings:
print(
    "Mean avg time taken for results:",
    sum(pos_times + neg_times) / (len(pos_times) + len(neg_times)),
)
print("Total time taken: ", sum(pos_times + neg_times))

# Print metrics:
true_data = [1] * len(positive_results) + [0] * len(negative_results)
print(f"Precision: {precision_score(true_data, positive_results+negative_results)}")
print(f"Recall: {recall_score(true_data, positive_results+negative_results)}")
print(f"F1 score: {f1_score(true_data, positive_results+negative_results)}")

# PLot confusion matrix:
cm = confusion_matrix(true_data, positive_results + negative_results)
disp = ConfusionMatrixDisplay(confusion_matrix=cm)
disp.plot()
plt.show()


def log_false_negatives(results: List[int], review_ids: List[str], path_to_save: str):
    """Creates a csv of false negatives to aid model evaluation. This function should
    be given results obtained from 'positive' data i.e. reviews that should trigger the names rule
    Arguments:
        results: a list of 1 or 0 (int) returned from the model
        review_ids: a list of the review ids of the checked reviews
    """
    fn = []
    for result, comment_id in zip(results, review_ids):
        if result == 0:
            fn.append(comment_id)
    fn_reviews = rejected_data[rejected_data["Comment ID"].isin(fn)]
    fn_reviews.to_csv(path_to_save)


def log_false_positives(
    results: List[int], names: List[List[str]], review_ids: List[str], path_to_save: str
):
    """Creates a csv of false positives to aid model evaluation. This function should be given results obtained
    from 'negative' data i.e. reviews that should not trigger the names rule
    Arguments:
        results: a list of 1 or 0 (int) returned from the model
        names: a list of lists of names
        review_ids: a list of the review ids of the checked reviews
    """
    fp = []
    fp_names = []
    for result, name, comment_id in zip(results, names, review_ids):
        if result == 1:
            fp.append(comment_id)
            fp_names.append(name)
    fp_reviews = published_data[published_data["Comment ID"].isin(fp)]
    fp_reviews = fp_reviews.assign(names=fp_names)
    fp_reviews.to_csv(path_to_save)


# CSV IS OVERWRITTEN ON EACH RUN OF THE TEST SUITE
# Specify a new path to avoid this
log_false_negatives(
    positive_results,
    positive_review_ids,
    "./src/data/testing_data/false_negative_reviews.csv",
)

# CSV IS OVERWRITTEN ON EACH RUN OF THE TEST SUITE
# Specify a new path to avoid this
log_false_positives(
    negative_results,
    neg_names,
    negative_review_ids,
    "./src/data/testing_data/false_positive_reviews.csv",
)
