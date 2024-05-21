import json
import os
import urllib.request
from typing import List, Tuple

from config import descriptions_adj, descriptions_nouns
from helpers.common_functions import clean_api_key, correct_url_format, log_exceptions


@log_exceptions
def descriptor_rule(
    submission_words: str,
    desc_adjectives_to_use=descriptions_adj,
    descriptions_nouns=descriptions_nouns,
) -> Tuple[int, List[str]]:
    """Check string for descriptors in the form of Adjective -> Noun
    The function then checks if the Adjectives -> Nouns identified are in a list of preselected terms.
    Args:
        submission_words : string to check - it has more args than this, describe them all.
      Returns:
        Tuple[int, List[str]]: A tuple containing two elements:
            - An integer label (0 or 1) where 1 indicates that at least one valid descriptor was found.
            - A list of strings with each valid 'Adjective Noun' descriptor found in the input string.
    """

    if not isinstance(submission_words, str):
        raise ValueError("expected a string")

    data = {"data": str(submission_words)}

    body = str.encode(json.dumps(data))

    url = os.getenv("DescriptionsURL")
    url = correct_url_format(url)
    api_key = os.getenv("DescriptionsKey")
    api_key = clean_api_key(api_key)

    if not api_key:
        raise Exception("A key should be provided to invoke the endpoint")

    # The azureml-model-deployment header will force the request to go to a specific deployment.
    # Remove this header to have the request observe the endpoint traffic rules
    headers = {
        "Content-Type": "application/json",
        "Authorization": ("Bearer " + api_key),
    }

    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)
        result = response.read()
        result = json.loads(result)
        predicted_classes = json.loads(result)

    except urllib.error.HTTPError as error:
        print(f"failed with str {str(error.code)}")
        print(error.info())
        raise

    result_label = 0
    result = []

    for pair in predicted_classes.values():
        if pair[0] in desc_adjectives_to_use and pair[1] in descriptions_nouns:
            descriptor = f"{pair[0]} {pair[1]}"
            result.append(descriptor)

    if len(result) > 0:
        result_label = 1

    return result_label, result
