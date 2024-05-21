import pytest

import src.modules.url_rule as url_rule
from src.spacy_nlp_matcher_making import matcher, nlp


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            "You should really go to this address:http://www.foufos.gr",
            (1, ["http://www.foufos.gr"]),
        ),
        (
            "There's a better Dr here: https://www.fouFos.gr",
            (1, ["https://www.fouFos.gr"]),
        ),
        (
            "And a better Dr here http://foufos.gr or here tbh http://betterdr.it",
            (1, ["http://foufos.gr", "http://betterdr.it"]),
        ),
        (
            "http://www.foufos.gr/kino is where I had better luck",
            (1, ["http://www.foufos.gr/kino"]),
        ),
        ("Please buy my products. http://werer.gr", (1, ["http://werer.gr"])),
        ("www.mp3.com", (1, ["www.mp3.com"])),
        ("www.t.co", (1, ["www.t.co"])),
        ("www.bookthebestholiday.travel", (1, ["www.bookthebestholiday.travel"])),
        ("http://t.co", (1, ["http://t.co"])),
        ("http://www.t.co", (1, ["http://www.t.co"])),
        ("https://www.t.co", (1, ["https://www.t.co"])),
        ("www.aa.com", (1, ["www.aa.com"])),
        ("http://aa.com", (1, ["http://aa.com"])),
        ("http://www.aa.com", (1, ["http://www.aa.com"])),
        ("https://www.aa.com", (1, ["https://www.aa.com"])),
        ("www.foufos", (1, ["www.foufos"])),
        ("www.foufos-.gr", (1, ["www.foufos-.gr"])),
        ("www.-foufos.gr", (1, ["www.-foufos.gr"])),
        ("foufos.gr", (1, ["foufos.gr"])),
        ("http://www.foufos", (1, ["http://www.foufos"])),
        ("http://foufos", (1, ["http://foufos"])),
        ("www.mp3#.com", (1, ["www.mp3#.com"])),
        ("mailto:name@example.com", (0, [])),
        ("rdar://1234", (0, [])),
        ("This is  a normal text", (0, [])),
        ("///:ss", (0, [])),
        ("...", (0, [])),
    ],
)
def test_check_url_rule(input, expected):
    doc = nlp(input)
    result = url_rule.check_url_rule(nlp, doc, matcher)

    assert result == expected


def test_url_rule_logging(caplog):
    input_for_error = 5
    with pytest.raises(Exception):
        url_rule.check_url_rule(input_for_error)
    assert "url_rule" in caplog.text
