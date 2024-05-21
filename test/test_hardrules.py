from src.hardrules import HardRules
from src.helpers import common_functions

common_functions.load_env_variables()


def test_HardRules(
    comment="This is a test comment to test the hard rules object setup. It instantiates a HardRules object and runs the apply function, which should in turn run each module and return a dict",
    org="dummyorganisation",
):
    obj = HardRules(body=comment, org_name=org)
    assert isinstance(obj.apply(), dict)
