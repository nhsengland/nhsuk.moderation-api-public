import json
import logging
import os
import urllib
from typing import List, Tuple

from helpers.common_functions import clean_api_key, correct_url_format, log_exceptions

logger = logging.getLogger(__name__)


@log_exceptions
def safeguarding_rule(submission_words: str) -> Tuple[int, List[str], str]:
    """Checks a string for safeguarding indications such as selfharm

    Args:
        submission_words : a lowercase string to check for safeguarding concerns
    Returns:
        tuple of length 3: first value is the score,
        second value is the level of the risk ("No safeguarding"/"Possibly Concerning"/"Strongly Concerning"),
        third value is probability / confidence (str)
    """

    url = os.getenv("SafeguardingURL")
    url = correct_url_format(url)
    api_key = os.getenv("SafeguardingKey")
    api_key = clean_api_key(api_key)
    body = str.encode(json.dumps({"data": submission_words}))

    headers = {
        "Content-Type": "application/json",
        "Authorization": ("Bearer " + api_key),
        "azureml-model-deployment": "safeguarding",
    }

    req = urllib.request.Request(url, body, headers)
    response = urllib.request.urlopen(req)
    result = response.read()
    result = json.loads(result)
    predicted_classes = json.loads(result)

    score = 0

    if predicted_classes["0"] == "Possibly Concerning":
        score = 1
    elif predicted_classes["0"] == "Strongly Concerning":
        score = 2
    return score, [predicted_classes["0"]], predicted_classes["1"]
