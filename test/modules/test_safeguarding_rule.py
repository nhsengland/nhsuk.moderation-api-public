import json

import pytest

from src.helpers import common_functions
from src.modules.safeguarding_rule import safeguarding_rule

common_functions.load_env_variables()

with open("test/test_data/test-comments.json") as f:
    test_comments = json.load(f)


def almost_equal(val1, val2, precision=3):
    format_string = "{:." + str(precision) + "f}"
    return format_string.format(float(val1)) == format_string.format(float(val2))


@pytest.mark.parametrize(
    "body, expected",
    [
        (
            test_comments["cutting"]["Comment"],
            (1, ["Possibly Concerning"], "0.81097084"),
        ),
        (
            test_comments["depressed"]["Comment"],
            (2, ["Strongly Concerning"], "0.99905795"),
        ),
        (
            test_comments["overdose"]["Comment"],
            (2, ["Strongly Concerning"], "0.99648947"),
        ),
        (
            test_comments["drug_abuse"]["Comment"],
            (2, ["Strongly Concerning"], "0.9978967"),
        ),
        (
            test_comments["domestic_abuse"]["Comment"],
            (1, ["Possibly Concerning"], "0.96628714"),
        ),
        (
            test_comments["thanking_dr"]["Comment"],
            (0, ["No safeguarding"], "0.99942696"),
        ),
        (
            test_comments["crying"]["Comment"],
            (1, ["Possibly Concerning"], "0.87213665"),
        ),
    ],
)
def test_safeguarding_rule(body, expected):
    result = safeguarding_rule(body)
    assert result[0] == expected[0]
    assert result[1] == expected[1]
    assert almost_equal(
        result[2], expected[2], 3
    )  # Compare only the first 3 decimal places


def test_safeguarding_logging(caplog):
    input_for_error = 5
    with pytest.raises(Exception):
        safeguarding_rule(input_for_error)
    assert "safeguarding" in caplog.text
