# This module contains a set of functions that work together to detect URLs in text using
# both spaCy's built-in URL matching functionality and regular expressions. The module
# also provides functionality to verify if the detected URLs are not in a list of
# URL exceptions.
import logging
from typing import List, Tuple

import regex as re

from helpers.common_functions import log_exceptions

logger = logging.getLogger(__name__)

url_exceptions = ["...", "...?"]


@log_exceptions
def find_match_for_url_rule(text: str) -> Tuple[int, List[str]]:
    """
    Checks if a given text contains a URL using regex matching.

    Args:
        text (str): The input text to be analysed for URL matches.

    Returns:
        a tuple of length 2: first value is the score (1 if a non-exception URL is found, otherwise 0),
        second value is a list of matched URLs found in the document
    """
    score = 0
    matched_urls = []

    if isinstance(text, str):
        # Search for text matching an URL regex
        urls_found = re.findall(
            r"(?i)\b((?:ftp|ftps|http|https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))",
            text,
        )

        if urls_found:
            score = 1
            matched_urls.extend(urls_found)

    return score, matched_urls


def verify_url_rule(nlp, doc, matcher) -> Tuple[int, List[str]]:
    """
    Determines whether a given document contains a URL that is not in the list of URL exceptions.

    Args:
        nlp (spacy.Language): A spaCy language model instance.
        doc (spacy.tokens.Doc): A document to be analysed for URL matches.
        matcher (spacy.matcher.Matcher): A spaCy Matcher object configured to find URL patterns.

    Returns:
        a tuple of length 2: first value is the score (1 if a non-exception URL is found, otherwise 0),
        second value is a list of matched URLs found in the document
    """
    score = 0
    matched_urls = []

    matches = matcher(doc)

    if matches:
        for match_id, start, end in matches:
            string_id = nlp.vocab.strings[match_id]
            if string_id == "URL" and doc[start:end].text not in url_exceptions:
                score = 1
                matched_urls.append(doc[start:end].text)

    return score, matched_urls


@log_exceptions
def check_url_rule(nlp, doc, matcher) -> Tuple[int, List[str]]:
    """
    Checks a given document for URL matches using both spaCy's built-in URL matching and
    regular expressions.

    Args:
        nlp (spacy.Language): A spaCy language model instance.
        doc (spacy.tokens.Doc): A document to be analysed for URL matches.
        matcher (spacy.matcher.Matcher): A spaCy Matcher object configured to find URL patterns.

    Returns:
        a tuple of length 2: first value is the score (1 if a non-exception URL is found, otherwise 0),
        second value is a list of matched URLs found in the document
    """
    result = verify_url_rule(nlp, doc, matcher)

    if result[0] == 0:
        result = find_match_for_url_rule(doc.text)

    return result[0], result[1]
