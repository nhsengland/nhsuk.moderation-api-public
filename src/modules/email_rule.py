from typing import List, Tuple

import regex as re

from helpers.common_functions import log_exceptions


@log_exceptions
def check_email_rule(submission_words: str) -> Tuple[int, List[str]]:
    """
    Checks if a given submission contains an email address using regex matching.

    Args:
        submission_words (str): The input text to be analyzed for email address matches.

    Returns:
        tuple of length 2: first value being the score (1 if an email address is found, otherwise 0),
        second value is a list of email addresses found in the submission.
    """
    assert isinstance(submission_words, str)

    score = 0
    matches = []
    email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    matched_emails = re.findall(email_regex, submission_words)
    if matched_emails:
        score = 1
        matches = matched_emails

    return score, matches
