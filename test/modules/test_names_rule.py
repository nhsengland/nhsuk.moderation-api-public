import json

import pytest

from src.helpers import common_functions
from src.modules.names_helpers import (
    allow_name_signoff,
    allow_org_name,
    definite_names,
    remove_non_names,
)
from src.modules.names_rule import names_rule

common_functions.load_env_variables()

with open("test/test_data/test-comments-names.json") as f:
    test_comments = json.load(f)


# Checks functionality of the remove non-name post-processing step
@pytest.mark.parametrize(
    "result, expected",
    [
        (test_comments["one_non_name"], ["alan", "brian", "david"]),
        (test_comments["all_non_names"], []),
        (test_comments["no_non_names"], ["alan", "brian", "david"]),
    ],
)
def test_remove_non_names(result, expected):
    """
    We have a function which removes common false positives from a list of names
    identified by NLP model. For example, our model will flag 'lord' in 'thank
    the lord I'm OK'; but actually this isn't a name in the sense we're
    interested in. This tests that that function is working as expected.
    """
    assert remove_non_names(result) == expected


# Checks functionality of the include definite-name post-processing step
@pytest.mark.parametrize(
    "body, expected",
    [
        (test_comments["definite_name"]["Comment"], ["mustafa"]),
        (test_comments["definite_name_with_punc"]["Comment"], ["mustafa"]),
        (test_comments["no_definite_name"]["Comment"], []),
    ],
)
def test_definite_names(body, expected):
    assert definite_names(body) == expected


# Checks functionality of allowing org names
@pytest.mark.parametrize(
    "org_name, full_result, expected",
    [
        (
            test_comments["org_name_flagged"]["org_name"],
            test_comments["org_name_flagged"]["full_result"],
            ["matt", "alice"],
        ),
        (
            test_comments["org_name_flagged_x2"]["org_name"],
            test_comments["org_name_flagged_x2"]["full_result"],
            ["matt", "alice"],
        ),
    ],
)
def test_allow_org_name(org_name, full_result, expected):
    """
    If you go to St. Thomas hospital, you should be able to say so in your
    review without it violating our no-names rule. We have a way of including
    such exceptions - this test checks that that's working as expected.
    """
    assert allow_org_name(org_name, full_result) == expected


# Checks functionality of allowing sign off - consider the comment i made in the names_rule about them having the same name as a nurse and test what that situation would do
@pytest.mark.parametrize(
    "body, full_result, expected",
    [
        (
            test_comments["signoff_with_name"]["Comment"],
            test_comments["signoff_with_name"]["full_result"],
            ["sarah"],
        ),
        (
            test_comments["signoff_with_name_with_punc"]["Comment"],
            test_comments["signoff_with_name_with_punc"]["full_result"],
            [],
        ),
        (
            test_comments["name_no_signoff"]["Comment"],
            test_comments["name_no_signoff"]["full_result"],
            ["sarah"],
        ),
    ],
)
def test_allow_name_signoff(body, full_result, expected):
    """
    You're allowed to include your own name at the end of a review, which is
    common. I.e. "... Thanks very much! -Mary"

    This tests that the function we've built to *exclude sign-offs* from our
    names checking, is working as expected.
    """
    assert allow_name_signoff(body, full_result) == expected


# Checks functionality of combined steps
@pytest.mark.parametrize(
    "body, org_name, expected",
    [
        (
            test_comments["one_name"]["Comment"],
            test_comments["one_name"]["Organisation"],
            (1, ["mustafa"]),
        ),
        (
            test_comments["one_sentance"]["Comment"],
            test_comments["one_sentance"]["Organisation"],
            (1, ["anthony"]),
        ),
        (
            test_comments["two_sentences"]["Comment"],
            test_comments["two_sentences"]["Organisation"],
            (1, ["joy", "laila"]),
        ),
        (
            test_comments["lower_case"]["Comment"],
            test_comments["lower_case"]["Organisation"],
            (1, ["beckham"]),
        ),
        (
            test_comments["upper_case"]["Comment"],
            test_comments["upper_case"]["Organisation"],
            (1, ["sarah"]),
        ),
        (
            test_comments["multiple_names"]["Comment"],
            test_comments["multiple_names"]["Organisation"],
            (1, ["dan", "mustafa", "sandra"]),
        ),
        (
            test_comments["multiple_names_with_signoff"]["Comment"],
            test_comments["multiple_names_with_signoff"]["Organisation"],
            (1, ["simon", "steven"]),
        ),
        (
            test_comments["org_name"]["Comment"],
            test_comments["org_name"]["Organisation"],
            (1, ["alice"]),
        ),
        (
            test_comments["org_name_real1"]["Comment"],
            test_comments["org_name_real1"]["Organisation"],
            (0, []),
        ),
        (
            test_comments["org_name_real2"]["Comment"],
            test_comments["org_name_real2"]["Organisation"],
            (0, []),
        ),
    ],
)
def test_full_names_rule(body, org_name, expected):
    """
    This tests the names rule; it pulls in some comments specified above from
    the test_comments json, and passes them to the names rule function. This
    calls the names API specified in your .env file. These tests check that that
    endpoint, and the rest of the names function, are working as expected.

    This test is distinct from the others in that it's testing the full,
    combined rule. This is comprised of some simple 'helper' functions, and the
    main NLP component which lives on an endpoint specified in your .env.
    """

    assert names_rule(body, org_name) == expected


def test_names_rule_logging(caplog):
    """
    Because the names rule turns it's input into a string: str(input), it's kind
    of hard to make it throw an error; because anything can be turned into a
    string - and then the rule works fine. Here we've made a class which will
    allow us to give an error. When str(submission_words) is called, it will
    produce a string that looks like a dictionary containing itself as a value
    (due to str(self)). This will lead to a json.dumps() failure since the
    resulting string is not a valid format for JSON serialization.
    """

    class ProblematicString:
        def __str__(self):
            return "{unserializable: " + str(self) + "}"

    input_for_error = ProblematicString()

    with pytest.raises(Exception):
        names_rule(input_for_error)
    assert "names" in caplog.text
