import pytest

from src.modules.profanity import profanity_rule
from src.spacy_nlp_matcher_making import nlp


@pytest.mark.parametrize(
    "submission_words, expected",
    [
        (
            [
                word.text
                for word in nlp(
                    """
                This is a good practice with attentive staff who always make me feel massively good
                """
                )
            ],
            (0, []),
        ),
        (
            [
                word.text
                for word in nlp(
                    """
                load of rubbish don't go there at the risk of getting cameltoe
                """
                )
            ],
            (1, ["cameltoe"]),
        ),
    ],
)
def test_profanity(submission_words, expected):
    assert profanity_rule(submission_words) == expected


def test_profanity_logging(caplog):
    input_for_error = 5
    with pytest.raises(Exception):
        profanity_rule(input_for_error)
    assert "profanity_rule" in caplog.text
