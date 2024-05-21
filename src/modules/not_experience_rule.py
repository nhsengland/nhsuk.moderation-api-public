import json
import os
import urllib
from typing import List, Tuple

from config import MAX_TITLE_CHARS
from helpers.common_functions import clean_api_key, correct_url_format, log_exceptions


@log_exceptions
def not_experience_rule(submission_words: str) -> Tuple[int, List[str]]:
    """Function to check comment and title for content that does not describe an experience.

    Args:
        submission_words : a lowercase string to check for not an experience
    Returns:
        a tuple of length 2: first value is the score (0 if an experience 1 if not),
        second value is the prediction ("Experience" or "Not_an_experience")
    """
    score = 0
    prediction = "Experience"
    # If submission is a title then skip model and mark as 'Experience'
    if len(submission_words) <= MAX_TITLE_CHARS:
        return (score, [prediction])

    # This is extracting the text from the submitted json
    data = {"data": [submission_words]}

    body = str.encode(json.dumps(data))

    url = os.getenv("NotAnExperienceURL")
    url = correct_url_format(url)
    api_key = os.getenv("NotAnExperienceKey")
    api_key = clean_api_key(api_key)

    if not api_key:
        raise Exception("A key should be provided to invoke the endpoint")

    headers = {
        "Content-Type": "application/json",
        "Authorization": ("Bearer " + api_key),
    }

    req = urllib.request.Request(url, body, headers)

    response = urllib.request.urlopen(req)

    result = response.read()
    result = result.decode()
    result = json.loads(
        json.loads(result)
    )  # We have to do this because the returned result is double-serialised.
    result_final = int(result["0"])

    if result_final == 1:
        score = 1
        prediction = "Not_an_experience"

    return score, [prediction]
