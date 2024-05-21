import logging
import os
import sys
from typing import List, Tuple

sys.path.append(os.path.abspath("nhsuk.moderation-api\src"))
from config import profanity
from helpers.common_functions import log_exceptions

logger = logging.getLogger(__name__)


@log_exceptions
def profanity_rule(
    submission_words: List[str], profanity_list=profanity
) -> Tuple[int, List[str]]:
    """Checks words for profanity

    Args:
        submission_words (list) : list of strings (words) to check for profanity
        profanity (list) : list of strings of profane words to check for in submission

    Returns:
        a tuple of length 2: first value is the score (0 for no profanity, 1 otherwise),
        second value is a list of profanity words included in submission
    """
    result = list(
        set(
            [
                profane_word.lower()
                for profane_word in profanity_list
                if profane_word.lower() in submission_words
            ]
        )
    )

    profane_count = len(result)

    if profane_count > 0:
        return 1, result

    if profane_count == 0:
        return 0, result
