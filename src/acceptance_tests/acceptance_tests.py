import os

import pytest
import requests

test_data = [
    {
        "title": "Comment Title",
        "body": "This is the main text of the comment. It's long enough but doesn't really say that much",
        "expected_response": "not_an_experience",
    },
    {
        "title": "Doctor stealing drugs",
        "body": "I went to the GP to get an opinion about a sore throat I've had the last month. The doctor was stealing drugs from the practice and I saw it with my own eyes. When I told the nurse she didn't do anything",
        "expected_response": "complaint",
    },
    {
        "title": "Love My GP",
        "body": "I went to the GP to get an opinion about a sore throat I've had the last month. The doctor was called Philip Hammond and I thought he was unkind. Andrew landsley was worse. Hoping I get better soon, Therese",
        "expected_response": "landsley",
    },
    {
        "title": "Going to kill myself",
        "body": "This is the day I kill myself. I've already taken the pills. I took the whole bottle. This is the end for me and I won't be waking up from this. Goodbye cruel world.",
        "expected_response": "concerning",
    },
    {
        "title": "Really like the doctor who treated me.",
        "body": "I really like short welsh doctor who treated me. She told me I had very small lungs. Not sure if that's bad news or not but it doesn't sound good. Anyway there were more vending machines that I would have expected.",
        "expected_response": "descriptor",
    },
]


@pytest.mark.parametrize("input", test_data)
def test_automoderator(input):
    """
    Test the auto-moderation endpoints for a response.

    This function sends a series of predefined requests to the auto-moderation endpoint,
    each containing a title and body of text. It then verifies that the response from
    the endpoint matches the expected categorization.

    Parameters:
    input (dict): A dictionary containing the 'title' and 'body' of a submission, along
                  with the 'expected_response'
                  by the automoderation tool.

    The function asserts that the HTTP status code is 200 (the request was successfully received) and that the response text
    includes the expected categorization.
    """
    base_url = os.environ.get("BASE_URL")
    subscription_key = os.environ.get("API_KEY")

    url = f"{base_url}/automoderation/automoderator"

    headers = {"subscription-key": subscription_key, "Content-Type": "application/json"}

    data = {
        "organisation-name": "Testing Organisation",
        "request-id": "bdd39182-95a7-490a-9f79-8f4747250081",
        "request": [
            {"id": "title", "text": input["title"]},
            {"id": "body", "text": input["body"]},
        ],
    }

    response = requests.post(url=url, headers=headers, json=data)
    assert response.status_code == 200

    response_text = response.text
    assert (
        input["expected_response"] in response_text.lower()
    )  # We lower this because there's ongoing uncerainty with what the names model will return. Just checking uncased match is enough here.
