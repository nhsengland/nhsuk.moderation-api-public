import json

import pytest

from src.helpers import common_functions
from src.modules.descriptor_rule import descriptor_rule

common_functions.load_env_variables()

with open("test/test_data/test-comments.json") as f:
    test_comments = json.load(f)


@pytest.mark.parametrize(
    "body, expected",
    [
        (test_comments["ethnic"]["Comment"], (1, ["welsh woman"])),
        (test_comments["hair_colour"]["Comment"], (1, ["blonde doctor"])),
        (test_comments["height"]["Comment"], (1, ["tall pharmacist"])),
        (test_comments["wonderful"]["Comment"], (0, [])),
        (test_comments["awful"]["Comment"], (0, [])),
    ],
)
def test_descriptor_rule(body, expected):
    """
    This tests the descriptor rule; it pulls in some comments specified above
    from the test_comments json, and passes them to the descriptor rule
    function. This calls the descriptor API specified in your .env file. These
    tests check that that endpoint, and the rest of the descriptor function, are
    working as expected.
    """

    assert descriptor_rule(body) == expected


def test_descriptor_logging(caplog):
    input_for_error = 5
    with pytest.raises(Exception):
        descriptor_rule(input_for_error)
    assert "descriptor_rule" in caplog.text
