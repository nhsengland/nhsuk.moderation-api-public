import pytest

from src.modules.profanity_soft import profanity_rule_soft


@pytest.mark.parametrize(
    "submission_words, expected",
    [
        (
            "this is a good practice with attentive staff who always make me feel massively good",
            (0, []),
        ),
        (
            "load of rubbish don't go there the doctor is a prick",
            (1, ["prick"]),
        ),
    ],
)
def test_profanity_soft(submission_words, expected):
    assert profanity_rule_soft(submission_words) == expected


def test_profanity_soft_logging(caplog):
    input_for_error = 5
    with pytest.raises(Exception):
        profanity_rule_soft(input_for_error)
    assert "profanity_rule_soft" in caplog.text
