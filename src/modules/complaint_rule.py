import json
import os
import ssl
import urllib.request
from typing import List, Tuple

from helpers.common_functions import clean_api_key, correct_url_format, log_exceptions


def allow_self_signed_https(allowed):
    """
    Configures the SSL context to allow or disallow self-signed HTTPS certificates based on the provided argument.

    Parameters:
    allowed (bool): If True, bypasses SSL certificate verification.
    """
    if (
        allowed
        and not os.environ.get("PYTHONHTTPSVERIFY", "")
        and getattr(ssl, "_create_unverified_context", None)
    ):
        ssl._create_default_https_context = ssl._create_unverified_context


@log_exceptions
def complaint_rule(submission_words: str) -> Tuple[int, List[str]]:
    """
    Determines if the provided text is a complaint or not.
    This function prepares the data to be sent in the request,
    sets the API key and headers, makes an HTTP request with the prepared data,
    and deciphers the result upon receiving a response.

    Args:
        submission_words (str) : lowercase text to be analyzed.

    Returns:
        tuple of length 2: first value is the score (0 or 1),
        second value is the prediction ("No_Complaint" or "Complaint").
    """
    allow_self_signed_https(
        True
    )  # this line is needed if you use self-signed certificate in your scoring service.

    assert isinstance(submission_words, str)

    data = {"data": [submission_words]}

    body = str.encode(json.dumps(data))

    url = os.getenv("ComplaintsURL")
    url = correct_url_format(url)
    api_key = os.getenv("ComplaintsKey")
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
    interim_result = result.decode()
    result_final = int(interim_result[1])
    score = 0
    prediction = "No_Complaint"

    if result_final == 1:
        score = 1
        prediction = "Complaint"

    return score, [prediction]
