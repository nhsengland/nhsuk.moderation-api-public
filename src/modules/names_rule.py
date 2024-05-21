import json
import logging
import os
import urllib
from typing import List, Tuple

import requests

from config import MAX_TITLE_CHARS
from helpers.common_functions import clean_api_key, correct_url_format, log_exceptions
from modules.names_helpers import (
    allow_name_signoff,
    allow_org_name,
    definite_names,
    remove_non_names,
)


@log_exceptions
def names_rule(submission_words: str, org_name: str) -> Tuple[int, List[str]]:
    """Check a string for names

    Args:
        submission_words : a string to check for names
        org_name: the organisation being reviewed
    Returns:
        tuple of length 2: first value is the score,
        second  value is a list of names
    """

    url = os.getenv("NamesURL")
    url = correct_url_format(url)
    api_key = os.getenv("NamesKey")
    api_key = clean_api_key(api_key)

    body = str.encode(json.dumps({"data": submission_words}))

    headers = {
        "Content-Type": "application/json",
        "Authorization": ("Bearer " + api_key),
        "azureml-model-deployment": "names-module",
    }

    req = urllib.request.Request(url, body, headers)
    response = urllib.request.urlopen(req)
    result = response.read()
    result = json.loads(result)
    predicted_classes = json.loads(result)

    # get lowercase list of names (need lowercase for comparison with non-names list)
    result = [
        x["word"].lower()
        for x in predicted_classes.values()
        if x["entity_group"] == "PER"
    ]

    # Remove names from the result that are in non_names
    filtered_names = remove_non_names(result)

    # Add any names from submission_words that are in def_names
    def_names_result = definite_names(submission_words)
    full_result = list(set(def_names_result + filtered_names))

    # remove org names
    full_result = allow_org_name(org_name, full_result)

    # allow name signoff only if submission words are from comment text
    if len(submission_words) > MAX_TITLE_CHARS:
        full_result = allow_name_signoff(submission_words, full_result)

    # Sort the names
    full_result.sort()

    if full_result:
        return 1, full_result
    else:
        return 0, []
