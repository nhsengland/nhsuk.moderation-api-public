import json

import pytest

from src.modules.allcaps import all_caps_rule
from src.spacy_nlp_matcher_making import nlp

with open("test/test_data/test-comments.json") as f:
    test_comments = json.load(f)

list_of_caps_rule_violations = [
    "WHAT",
    "LOAD",
    "OF",
    "RUBBISH",
    "THE",
    "DOCTOR",
    "WAS",
    "VERY",
    "RUDE",
    "TO",
    "AND",
    "SAID",
    "HAD",
    "TO",
    "COME",
    "BACK",
    "ANOTHER",
    "TIME",
    "WITH",
    "AN",
    "APPOINTMENT",
]


@pytest.mark.parametrize(
    "body, expected",
    [
        (test_comments["ground"]["Comment"], (0, 0, [])),
        (test_comments["acronym"]["Comment"], (0, 0, [])),
        (test_comments["one_caps"]["Comment"], (2, 1, ["VERY"])),
        (test_comments["three_caps"]["Comment"], (2, 2, ["SHAMBLES", "MILD"])),
        (
            test_comments["all_caps"]["Comment"],
            (1, 21, list_of_caps_rule_violations),
        ),
    ],
)
def test_hard_all_caps_rule(body, expected):
    assert all_caps_rule(body=nlp(body)) == expected


def test_allcaps_logging(caplog):
    input_for_error = 5
    with pytest.raises(Exception):
        all_caps_rule(input_for_error)
    assert "all_caps" in caplog.text
