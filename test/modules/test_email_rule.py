import pytest

from src.modules.email_rule import check_email_rule


@pytest.mark.parametrize(
    "input, expected",
    [
        ("jason@hotmail.com", (1, ["jason@hotmail.com"])),
        (
            "I cannot express my gratitude enough for the staff at [Surgery Name]. Dr. Smith went above and beyond to ensure my concerns were addressed. If you ever need to contact me for further feedback, feel free to reach me at [johnDoe123@example.co.uk].",
            (1, ["johnDoe123@example.co.uk"]),
        ),
        (
            "I’m quite disappointed with the service at [Surgery Name]. My appointment was delayed, and nobody informed me about the wait time. The front desk could use some lessons in communication and empathy. For any clarifications or to discuss further, I’m available at angrypatient@mymail.com or mixedfeelings@gmail.com.",
            (1, ["angrypatient@mymail.com", "mixedfeelings@gmail.com"]),
        ),
        (
            "The staff at [Surgery Name] are pleasant, but I've experienced consistent issues with scheduling and billing. I appreciate Dr. Lees thorough care, but administrative improvements are needed. Please contact me at [mixedfeelings@gmail.com] if you'd like more details.",
            (1, ["mixedfeelings@gmail.com"]),
        ),
        (
            "I believe [Surgery Name] could greatly benefit from utilizing a more user-friendly online booking system. The current method is quite tedious and prone to errors. Feel free to get in touch with me to discuss this further at [techsavyPatient@reviews.com].",
            (1, ["techsavyPatient@reviews.com"]),
        ),
        (
            "A massive thank you to Nurse Jamie at [Surgery Name]! Her compassion and expertise did not go unnoticed during my visit last Tuesday. If you need more specific feedback, drop me an email at gratefulPatient@superdupermail.com.",
            (1, ["gratefulPatient@superdupermail.com"]),
        ),
        (
            "Five stars for the [Surgery Name] team! Every visit has been met with kindness, professionalism, and a genuinely caring attitude from all staff members. Dr. Harris, in particular, has been absolutely wonderful in addressing all my concerns thoroughly.",
            (0, []),
        ),
        (
            "Regrettably, my experience with [Surgery Name] was less than stellar. My appointment was rescheduled multiple times without prior notice, and when I finally got to see the doctor, the consultation felt rushed and my concerns were not fully addressed.",
            (0, []),
        ),
        (
            "My experiences at [Surgery Name] have been a mixed bag. While I appreciate the medical advice from the doctors, the waiting times, both in-person and on calls, have been consistently lengthy. I hope to see an improvement in these administrative aspects in the future.",
            (0, []),
        ),
        (
            "The medical team at [Surgery Name] is commendable for their expertise. However, I'd suggest a review and possible overhaul of the appointment booking system, which currently feels outdated and occasionally unreliable. It's an aspect that, if improved, would greatly enhance patient experience.",
            (0, []),
        ),
        (
            "A heartfelt thanks to the administrative team at [Surgery Name]. Despite the busy environment, they always manage to assist patients with a smile, ensuring a pleasant and smooth experience even before meeting the doctor. This positive attitude significantly enhances the overall atmosphere of the surgery.",
            (0, []),
        ),
    ],
)
def test_check_email_rule(input, expected):
    result = check_email_rule(input)

    assert result == expected


def test_email_logging(caplog):
    input_for_error = 5
    with pytest.raises(Exception):
        check_email_rule(input_for_error)
    assert "email_rule" in caplog.text
