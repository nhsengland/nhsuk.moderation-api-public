# This is a script to test the performance of automod rules. The script reads in data from a csv,
# and runs this through each rule
# The mean, median and stdev of time taken is printed to the terminal.
# Before running the test suite on a large volume of data, check which endpoint is being queried in
# each rule - only sumbit large volumes of data to non-production endpoints and/or add a
# sleep to the for loop to avoid affecting live traffic
import os
from statistics import mean, median, stdev
from time import sleep
from timeit import default_timer

import matplotlib.pyplot as plt
import pandas as pd
import requests

from hardrules import HardRules
from helpers.common_functions import clean_api_key, correct_url_format
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

test_data = pd.read_csv("./src/data/testing_data/some_publishable_data.csv")


# Check there is a good distribution of lengths:
def check_len_distribution():
    """Produces a visual to understand distribution of comment lengths.
    Exits the script once called"""
    comment_lengths = []
    for i, row in test_data.iterrows():
        comment = row["Comment Text"]
        comment = comment.replace("’", "'")
        comment_lengths.append(len(comment))
    plt.hist(
        comment_lengths,
        color="lightgreen",
        ec="black",
        bins=[
            100,
            200,
            300,
            400,
            500,
            600,
            700,
            800,
            900,
            1000,
            1250,
            1500,
            1750,
            2000,
            3000,
        ],
    )
    plt.show()
    exit(0)


# check_len_distribution()

# Test models:
names_times = []
descriptor_times = []
nae_times = []
complaint_times = []
safeguarding_times = []


def models_performance():
    """Function for testing rules that use an endpoint"""
    for i, row in test_data.iterrows():
        title = row["Comment Title"]
        title = title.replace("’", "'")
        comment = row["Comment Text"]
        comment = comment.replace("’", "'")
        org_name = row["Org Name"]
        org_name = org_name.replace("’", "'")

        t1 = default_timer()
        title_result = names_rule(nlp(title).text, org_name)
        comment_result = names_rule(nlp(comment).text, org_name)
        t2 = default_timer()
        names_times.append(t2 - t1)

        t1 = default_timer()
        title_result = descriptor_rule(nlp(title).text.lower())
        comment_result = descriptor_rule(nlp(comment).text.lower())
        t2 = default_timer()
        descriptor_times.append(t2 - t1)

        t1 = default_timer()
        title_result = not_experience_rule(nlp(title).text.lower())
        comment_result = not_experience_rule(nlp(comment).text.lower())
        t2 = default_timer()
        nae_times.append(t2 - t1)

        t1 = default_timer()
        title_result = complaint_rule(nlp(title).text.lower())
        comment_result = complaint_rule(nlp(comment).text.lower())
        t2 = default_timer()
        complaint_times.append(t2 - t1)

        t1 = default_timer()
        title_result = safeguarding_rule(nlp(title).text.lower())
        comment_result = safeguarding_rule(nlp(comment).text.lower())
        t2 = default_timer()
        safeguarding_times.append(t2 - t1)
        # sleep for 10 seconds
        sleep(10)
    print(
        f"Names rule:\nMean: {round(mean(names_times),2)}, Median: {round(median(names_times),2)}, Stdev: {round(stdev(names_times),2)}\n"
    )
    print(
        f"Descriptor rule:\nMean: {round(mean(descriptor_times),2)}, Median: {round(median(descriptor_times),2)}, Stdev: {round(stdev(descriptor_times),2)}\n"
    )
    print(
        f"NAE rule:\nMean: {round(mean(nae_times),2)}, Median: {round(median(nae_times),2)}, Stdev: {round(stdev(nae_times),2)}\n"
    )
    print(
        f"Complaint rule:\nMean: {round(mean(complaint_times),2)}, Median: {round(median(complaint_times),2)}, Stdev: {round(stdev(complaint_times),2)}\n"
    )
    print(
        f"Safeguarding rule:\nMean: {round(mean(safeguarding_times),2)}, Median: {round(median(safeguarding_times),2)}, Stdev: {round(stdev(safeguarding_times),2)}"
    )


# Test local rules:
# These can be tested together as they are likely to be very quick and negligable
local_times = []


def local_performance():
    """Function for testing rules that are run in Flask only"""
    for i, row in test_data.iterrows():
        title = row["Comment Title"]
        title = title.replace("’", "'")
        comment = row["Comment Text"]
        comment = comment.replace("’", "'")
        org_name = row["Org Name"]
        org_name = org_name.replace("’", "'")

        t1 = default_timer()
        title_result = all_caps_rule(nlp(title))
        comment_result = all_caps_rule(nlp(comment))
        title_result = check_email_rule(nlp, nlp(title), matcher)
        comment_result = check_email_rule(nlp, nlp(comment), matcher)
        title_result = profanity_rule_soft(nlp(title).text.lower())
        comment_result = profanity_rule_soft(nlp(comment).text.lower())
        title_result = profanity_rule([word.text.lower() for word in nlp(title)])
        comment_result = profanity_rule([word.text.lower() for word in nlp(comment)])
        title_result = check_url_rule(nlp, nlp(title), matcher)
        comment_result = check_url_rule(nlp, nlp(comment), matcher)
        t2 = default_timer()
        local_times.append(t2 - t1)
    print(
        f"Local rules:\nMean: {round(mean(local_times),2)}, Median: {round(median(local_times),2)}, Stdev: {round(stdev(local_times),2)}\n"
    )


# Test hard_rules:
hr_times = []


def hr_performance():
    """Function for testing rules called by HardRules"""
    for i, row in test_data.iterrows():
        title = row["Comment Title"]
        title = title.replace("’", "'")
        comment = row["Comment Text"]
        comment = comment.replace("’", "'")
        org_name = row["Org Name"]
        org_name = org_name.replace("’", "'")

        t1 = default_timer()
        HardRules(body=title, org_name=org_name).apply()
        HardRules(body=comment, org_name=org_name).apply()
        t2 = default_timer()
        hr_times.append(t2 - t1)
        # sleep for 10 seconds
        sleep(10)
    print(
        f"HardRules:\nMean: {round(mean(hr_times),2)}, Median: {round(median(hr_times),2)}, Stdev: {round(stdev(hr_times),2)}\n"
    )


# Test full app DEV/INT environment:
# IMPORTANT: This tests the verison of the flask app deployed to dev or int,
# NOT your local version
app_times = []


def app_performance(env: str):
    """Function for testing the full app on the specified environment"""
    env_dict = {
        "INT": [
            correct_url_format(os.getenv("INTURL")),
            clean_api_key(os.getenv("INTKey")),
        ],
        "DEV": [
            correct_url_format(os.getenv("DEVURL")),
            clean_api_key(os.getenv("DEVKey")),
        ],
    }
    for i, row in test_data.iterrows():
        title = row["Comment Title"]
        title = title.replace("’", "'")
        comment = row["Comment Text"]
        comment = comment.replace("’", "'")
        org_name = row["Org Name"]
        org_name = org_name.replace("’", "'")
        data = {
            "organisation-name": org_name,
            "request-id": "abc",
            "request": [{"text": title}, {"text": comment}],
        }
        headers = {
            "Content-Type": "application/json",
            "subscription-key": env_dict[env][1],
        }
        t1 = default_timer()
        response = requests.post(
            f"{env_dict[env][0]}/automoderation/automoderator",
            json=data,
            headers=headers,
        )
        t2 = default_timer()
        if response.status_code != 200:
            print(f"Recieved a {response.status_code} response code")
            continue
        app_times.append(t2 - t1)
        # sleep for 10 seconds
        sleep(10)
    print(
        f"App:\nMean: {round(mean(app_times),2)}, Median: {round(median(app_times),2)}, Stdev: {round(stdev(app_times),2)}\n"
    )
