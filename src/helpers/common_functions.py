import functools
import logging
import os
import re
from typing import Any, Callable, List, Tuple

import dotenv
import emoji
from joblib import Parallel, delayed, parallel_backend


def clean_api_key(api_key: str):
    """Removes leading and trailing whitespace, and strips single quotes, backticks, and double quotes from a given API key string.

    Parameters:
    api_key (str): The API key string to clean.

    Returns:
    str: The cleaned API key string.
    """
    api_key = api_key.strip()
    api_key = api_key.replace("'", "")
    api_key = api_key.replace("`", "")
    api_key = api_key.replace('"', "")
    return api_key


def correct_url_format(url):
    """
    Corrects common formatting issues in URLs including removing leading apostrophes.

    Args:
    url (str): The URL string to be corrected.

    Returns:
    str: The corrected URL.
    """
    # Trim leading/trailing whitespaces and non-standard characters
    url = url.strip().lstrip("'\"")

    # Check for missing 'http://' or 'https://' prefix
    if not url.startswith(("http://", "https://")):
        # Attempt to find the start of the URL
        http_match = re.search(r"http://|https://", url)
        if http_match:
            # Slice the URL from the match
            url = url[http_match.start() :]
        else:
            # Default to adding 'http://' if no match found
            url = "http://" + url

    url = url.replace("'", "")
    url = url.replace("`", "")
    url = url.replace('"', "")
    return url


def log_exceptions(func: Callable):
    """A decorator that wraps the passed in function and logs
    exceptions should one occur"""
    logger = logging.getLogger(__name__)

    @functools.wraps(func)  # Preserve the metadata of the decorated function
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)  # Call the wrapped function
        except Exception as e:
            logger.error(
                f"Exception occurred in {func.__name__}: {str(e)}", exc_info=True
            )
            raise

    return wrapper


def load_env_variables():
    """Loads environment variables from local .env file"""
    if os.getenv("environmentShort") not in {"PROD", "INT", "DEV", "STAG"}:
        dotenv.load_dotenv()


def give_emoji_free_text(text):
    """Strips all emojis from the input text, leaving only emoji-free text.

    This function iterates through each character of the input text, identifying characters that are recognized as emojis based on the emoji.UNICODE_EMOJI list. It then reconstructs the text without these emoji characters, ensuring that the resulting text is free from any emoji.
    Parameters:
    text (str): The text from which emojis will be removed.

    Returns:
    str: The text stripped of all emojis.
    """
    allchars = [string for string in text]
    emoji_list = [c for c in allchars if c in emoji.UNICODE_EMOJI]
    clean_text = " ".join(
        [
            string.strip()
            for string in text.split()
            if not any(i in string for i in emoji_list)
        ]
    )

    return clean_text


def isEnglish(s):
    """
    To check for commonly occuring non ascii characters
    Parameters:
    s (str): The string to check.

    Returns:
    bool: True if the string can be considered as English after removing specific non-ASCII characters, otherwise False.
    """

    s = s.replace("\ufe0f", "")  # special space
    s = s.replace("\xbd", "")  # 1/2
    s = s.replace("\xe2", "")  # â
    s = s.replace("\xba", "")  # º
    s = s.replace("\xe0", "")  # à
    s = s.replace("\xe7", "")  # ç
    s = s.replace("\u015f", "")  # Ş
    s = s.replace("\xe9", "")  # é
    s = s.replace("\xe8", "")  # è
    s = s.replace("\u013a", "")  # i
    s = s.replace("\u0155", "")  # r
    s = s.replace("\u0131", "")  # ı
    s = s.replace("\xf6", "")  # ö

    ascii_only = s.encode("ascii", "ignore").decode()
    return s == ascii_only


def result_code_mappers(val):
    """Map result codes 0/1/2 to string explanations
    Parameters:
    val (int): The result code to map. Expected values are 0, 1, or 2.

    Returns:
    str: The explanation for the provided result code. Possible returns are "passed", "failed", or "human moderation required".
    """
    m = {0: "passed", 1: "failed", 2: "human moderation required"}
    return m[val]


def format_output_text(stringval):
    """Removes the unwanted characters in output text  and provides clean readable output .
    Parameters:
    stringval (str): The string to be cleaned and formatted.

    Returns:
    str: The cleaned and formatted string, with specific characters removed and certain sequences replaced for improved readability.
    """

    stringval = stringval.replace("},", "<br>")
    for ch in [
        "{",
        "}",
        "[",
        "]",
    ]:
        if ch in stringval:
            stringval = stringval.replace(ch, "")
    return stringval


def colouring(html_table):
    """The function highlights detected tags with individual colours in the html code.

    Args:
        html_table (str) : original html code

    Returns:
        html_table (str): modified html in which all detected tags are highlighted with individual colour
    """

    pos = {
        "Title matched": "green",
        "Token in names list": "aqua",
        "PERSON": "yellow",
        "NORP": "fuchsia",
        "Email": "wood",
        "Personal Description": "cyan",
        "Telephone number": "blue",
        "UK Postcode": "white",
        "Social Media": "orange",
    }

    for key, value in pos.items():
        html_table = html_table.replace(
            key, "<span class='{}'>{}</span>".format(value, key)
        )
        print(key, value)

    return html_table


def exec_in_parallel(
    callables: List[Tuple[Callable, List, dict]], n_jobs: int = 1
) -> List[Any]:
    """Use joblib to execute the callables via c() for c in callables

    Args:
    - callables: A list of tuples, each containing:
        - c (Callable): The callable function to be executed.
        - args (List): The positional arguments to be passed to the callable.
        - kwargs (dict): The keyword arguments to be passed to the callable.

    - n_jobs (int, optional): Number of parallel jobs to run. Default is 1.

    Returns:
    - List[Any]: A list containing the results of the parallel executions.
    """

    with parallel_backend("threading", n_jobs=n_jobs):
        ans = Parallel(verbose=True)(
            delayed(c)(*args, **kwargs) for c, args, kwargs in callables
        )

    return ans
