import re
from typing import List, Tuple

from config import profanity_soft
from helpers.common_functions import log_exceptions


@log_exceptions
def profanity_rule_soft(
    submission_words: str, profanity_list=profanity_soft
) -> Tuple[int, List[str]]:
    """Checks a string for soft profanity

    Args:
        submission_words (list) : a string to check for profanity
        profanity (list) : list of strings of profane words to check for in submission

    Returns:
        tuple of length 2: first value is the score (0 for no soft profanity, 1 otherwise),
        second value is a list of soft profanity words included in the submission
    """
    assert isinstance(submission_words, str)

    result = []
    for profane_word in profanity_list:
        pattern = r"\b" + profane_word.lower().strip() + r"\b"
        if re.search(pattern, submission_words):
            result.append(profane_word.lower())

    result = list(set(result))

    profane_count = len(result)
    if profane_count > 0:
        return 1, result

    if profane_count == 0:
        return 0, result
