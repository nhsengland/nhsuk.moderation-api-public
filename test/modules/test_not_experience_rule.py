import json

import pytest

from src.helpers import common_functions
from src.modules.not_experience_rule import not_experience_rule

common_functions.load_env_variables()

with open("test/test_data/test-comments.json") as f:
    test_comments = json.load(f)


@pytest.mark.parametrize(
    "body, expected",
    [
        (test_comments["not_an_experience"]["Comment"], (1, ["Not_an_experience"])),
        (test_comments["an_experience"]["Comment"], (0, ["Experience"])),
    ],
)
def test_not_experience_rule(body, expected):
    assert not_experience_rule(body) == expected


def test_nae_logging(caplog):
    input_for_error = 5
    with pytest.raises(Exception):
        not_experience_rule(input_for_error)
    assert "not_experience_rule" in caplog.text
