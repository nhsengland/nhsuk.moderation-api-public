from typing import List, Tuple

from config import ALL_CAPS_THRESHOLD, acronyms
from helpers.common_functions import log_exceptions


@log_exceptions
def all_caps_rule(body) -> Tuple[int, int, List[str]]:
    """Comments must not be in caps lock. Caps lock is defined as more than three words in all caps,
    excluding uppercase words in an acronyms list.
    This function is to check if the review contains any allcaps words.

    Args:
        body (spaCy Doc) : spacy doc object for the comment

    Returns:
        0/1/2 (int) : for pass/fail/human moderation
        number_of_all_caps (int) : number of all caps words
        all_caps_words (List[str]) : a list of the all caps words
    """

    # Uppercase words longer than 1 character and not in acronyms list are counted as all caps.
    words = [word.text for word in body]

    allcaps_words = []
    for word in words:
        if word.isupper() and len(word) > 1 and word not in acronyms:
            allcaps_words.append(word)

    number_of_all_caps = len(allcaps_words)

    if number_of_all_caps >= ALL_CAPS_THRESHOLD:
        return 1, number_of_all_caps, allcaps_words
    elif number_of_all_caps > 0:
        return 2, number_of_all_caps, allcaps_words
    else:
        return 0, number_of_all_caps, allcaps_words
