import json

import pytest

from src.helpers import common_functions
from src.modules.complaint_rule import complaint_rule

common_functions.load_env_variables()

with open("test/test_data/test-comments.json") as f:
    test_comments = json.load(f)


@pytest.mark.parametrize(
    "body, expected",
    [
        (test_comments["suing"]["Comment"], (1, ["Complaint"])),
        (test_comments["tribunal"]["Comment"], (1, ["Complaint"])),
        (test_comments["sexual harassment"]["Comment"], (1, ["Complaint"])),
        (test_comments["complaint A"]["Comment"], (1, ["Complaint"])),
        (test_comments["great practice"]["Comment"], (0, ["No_Complaint"])),
        (test_comments["terrible"]["Comment"], (0, ["No_Complaint"])),
        (test_comments["negligence"]["Comment"], (1, ["Complaint"])),
    ],
)
def test_complaint_rule(body, expected):
    """
    This tests the complaint rule; it pulls in some comments specified above
    from the test_comments json, and passes them to the complaints rule
    function. This calls the complaints API specified in your .env file. These
    tests check that that endpoint, and the rest of the complaints function, are
    working as expected.

    For example, the 'terrible' comment from the list above pulls in a comment
    which is negative, but does not qualify for raising a formal complaint.
    """
    assert complaint_rule(body) == expected


def test_complaints_rule_logging(caplog):
    """
    Checks that any triggering of the complaints rule is properly recorded to the log.
    """
    input_for_error = 5
    with pytest.raises(Exception):
        complaint_rule(input_for_error)
    assert "complaint_rule" in caplog.text
