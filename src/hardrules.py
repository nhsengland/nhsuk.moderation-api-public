import logging
from typing import Callable, Dict, Union

from joblib import Parallel, delayed, parallel_backend

from helpers import common_functions
from helpers.common_functions import exec_in_parallel, log_exceptions
from modules.allcaps import all_caps_rule
from modules.complaint_rule import complaint_rule
from modules.descriptor_rule import descriptor_rule
from modules.email_rule import check_email_rule
from modules.names_rule import names_rule
from modules.not_experience_rule import not_experience_rule
from modules.profanity import profanity_rule
from modules.profanity_soft import profanity_rule_soft
from modules.safeguarding_rule import safeguarding_rule
from modules.url_rule import check_url_rule
from src.spacy_nlp_matcher_making import matcher, nlp

common_functions.load_env_variables()


class HardRules:
    """Defines a class for enforcing moderation rules on user-generated comments.

    The HardRules class encapsulates a set of moderation rules applied to the text of user-generated comments to ensure they adhere to specific standards. It preprocesses the text for rule application and provides a method to validate the text against all moderation rules, returning a structured report on rule violations.

    Attributes:
    body (Doc): The processed text of the user comment, prepared for NLP operations.
    org_name (str): The name of the organisation associated with the comment.
    words (List[str]): A list of words in the comment, used for rule validation.

    Methods:
    apply() -> Dict[int, Dict[str, Union[int, str, Dict[str, str]]]]: Applies all hard moderation rules to the comment text and returns a dictionary of results indicating rule passes, failures, and flags for review.
    """

    def __init__(self, body: str, org_name: str):
        """Instantiate HardRules object (now includes all moderation rules).

        Args:
          body (str): The text to be validated
          org_name (str): The organisation being reviewed

        Returns:
          HardRules object
        """

        self.body = nlp(body)
        self.org_name = org_name
        self.words = [word.text.lower() for word in self.body]

    def apply(self) -> Dict[int, Dict[str, Union[int, str, Dict[str, str]]]]:
        """Validate all of the hard rules

        Returns:
          results (dict): results for each rule applied to the body. 0 for pass, 1 for
                          fail, 2 for flag for review
        """

        self.results = exec_in_parallel(
            [
                (all_caps_rule, [], dict(body=self.body)),
                (check_url_rule, [], dict(nlp=nlp, doc=self.body, matcher=matcher)),
                (
                    names_rule,
                    [],
                    dict(submission_words=self.body.text, org_name=self.org_name),
                ),
                (descriptor_rule, [], dict(submission_words=self.body.text.lower())),
                (safeguarding_rule, [], dict(submission_words=self.body.text.lower())),
                (complaint_rule, [], dict(submission_words=self.body.text.lower())),
                (
                    profanity_rule_soft,
                    [],
                    dict(submission_words=self.body.text.lower()),
                ),
                (check_email_rule, [], dict(submission_words=self.body.text)),
                (
                    not_experience_rule,
                    [],
                    dict(submission_words=self.body.text.lower()),
                ),
            ],
            n_jobs=4,
        )

        self.profanity_rule_results = profanity_rule(self.words)

        self.all_caps_results = self.results[0]
        self.url_rule_results = self.results[1]
        self.names_rule_results = self.results[2]
        self.descriptor_rule_results = self.results[3]
        self.safeguarding_rule_results = self.results[4]
        self.complaint_rule_results = self.results[5]
        self.profanity_rule_soft_results = self.results[6]
        self.email_rule_results = self.results[7]
        self.not_experience_rule_results = self.results[8]

        self.results = {
            "id": "ids",
            "results": [
                {
                    "rule": "allCaps",
                    "code": self.all_caps_results[0],
                    "values": self.all_caps_results[2],
                },
                {
                    "rule": "emailRule",
                    "code": self.email_rule_results[0],
                    "values": self.email_rule_results[1],
                },
                {
                    "rule": "urlRule",
                    "code": self.url_rule_results[0],
                    "values": self.url_rule_results[1],
                },
                {
                    "rule": "profanityDetectionHard",
                    "code": self.profanity_rule_results[0],
                    "values": self.profanity_rule_results[1],
                },
                {
                    "rule": "profanityDetectionSoft",
                    "code": self.profanity_rule_soft_results[0],
                    "values": self.profanity_rule_soft_results[1],
                },
                {
                    "rule": "namesRule",
                    "code": self.names_rule_results[0],
                    "values": self.names_rule_results[1],
                },
                {
                    "rule": "descriptorRuleHard",
                    "code": self.descriptor_rule_results[0],
                    "values": self.descriptor_rule_results[1],
                },
                {
                    "rule": "safeguardingRule",
                    "code": self.safeguarding_rule_results[0],
                    "values": self.safeguarding_rule_results[1],
                    "probability": self.safeguarding_rule_results[2],
                },
                {
                    "rule": "complaintRule",
                    "code": self.complaint_rule_results[0],
                    "values": self.complaint_rule_results[1],
                },
                {
                    "rule": "notAnExperienceRule",
                    "code": self.not_experience_rule_results[0],
                    "values": self.not_experience_rule_results[1],
                },
            ],
        }

        self.results["results"] = [x for x in self.results["results"] if x["code"] >= 1]
        return self.results
