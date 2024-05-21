import re
import string
from typing import List

from fuzzywuzzy import fuzz

from config import PARTIAL_RATIO_THRESHOLD, def_names, non_names


def remove_punctuation(input_string: str) -> str:

    return re.sub(r"[^\w\s]", "", input_string)


def remove_non_names(result: List[str]) -> List[str]:
    """
    Removes common false positives from a list of names identified by NLP model.
    For example, our model will flag 'lord' in 'thank the lord I'm OK'; but
    actually this isn't a name in the sense we're interested in.

    Args:
        result: a lowercase list of suspected names.
    Returns:
         a list: a list of names with non-names removed
    """
    filtered_names = [name for name in result if name not in non_names]

    return filtered_names


def definite_names(submission_words: str) -> List[str]:
    """
    Add names to the result that are listed as definite names

    Args:
        submission_words : a string to check for names
    Returns:
        a list: a list of names found
    """
    # remove all punctuation and make lowercase
    submission_no_punc = remove_punctuation(submission_words).lower()

    def_names_result = [n for n in submission_no_punc.split(" ") if n in def_names]

    return def_names_result


def allow_org_name(org_name: str, full_result: List[str]) -> List[str]:
    """
    Filters out names from a list that closely match a given organization name using fuzzy matching.

    Args:
        org_name (str): The organization name to compare against.
        full_result (List[str]): List of names to be filtered.

    Returns:
        List[str]: Filtered list of names with similar entries to `org_name` removed based on a similarity threshold.
    """

    org_name = remove_punctuation(org_name).lower()
    new_result = []
    for name in full_result:
        ratio = fuzz.partial_ratio(name, org_name)
        if ratio < PARTIAL_RATIO_THRESHOLD:  # Keep only results above the threshold.
            new_result.append(name)

    return new_result


def allow_name_signoff(submission_words: str, full_result: List[str]) -> List[str]:
    """Check if the last few words in the review submission contains names returned by bert
    Args:
        submission_words : a string to check for names
        full_result : the result so far returned by bert (lowercase)
    Returns:
        a list: result with any signoff names removed
    """
    # remove any commas and fullstops
    sign_off_punctuation = "[,.]"
    submission_no_punc = re.sub(sign_off_punctuation, "", submission_words)
    submission_split = submission_no_punc.split()

    end_words = [
        submission_split[-1].lower(),
        " ".join(submission_split[-2:]).lower(),
        " ".join(submission_split[-3:]).lower(),
    ]
    for word_combo in end_words:
        if word_combo in full_result:
            full_result.remove(word_combo)

    return full_result
