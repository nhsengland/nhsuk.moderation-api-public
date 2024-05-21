# config file to set thresholds and read in data lists

import os

from helpers.filehelper import read_csv_list

ALL_CAPS_THRESHOLD = 3  # 3 all caps words or less allowed per review
LANGUAGE_THRESHOLD = 99  # /100   # Retired, used in archived module detect_lang.py
CLASSIFIER_NO_PID_THRESHOLD = 0.86  # Retired, used in archived module pid.py
PARTIAL_RATIO_THRESHOLD = 89  # Used in names module fuzzy matching
MAX_TITLE_CHARS = (
    60  # Used to determine whether text is the review title or review body
)


data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

acronyms = read_csv_list(os.path.join(data_path, "acronym-list.csv"))
profanity = read_csv_list(os.path.join(data_path, "profanity-list-hard.csv"))
profanity_soft = read_csv_list(os.path.join(data_path, "profanity-list-soft.csv"))
descriptions_adj = read_csv_list(os.path.join(data_path, "descriptions-adjectives.csv"))
descriptions_nouns = read_csv_list(os.path.join(data_path, "descriptions-nouns.csv"))
non_names = [
    word.lower() for word in read_csv_list(os.path.join(data_path, "non-names.csv"))
]  # read in and ensure lowercase
def_names = [
    word.lower() for word in read_csv_list(os.path.join(data_path, "def-names.csv"))
]  # read in and ensure lowercase
