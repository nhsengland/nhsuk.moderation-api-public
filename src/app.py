import json

import dotenv
from flask import Flask, Response, request

from hardrules import HardRules
from helpers import common_functions
from helpers.logging_config import configure_logging

app = Flask(__name__, static_folder="./static")

configure_logging()
common_functions.load_env_variables()


# Route used by the auto moderation tool
@app.route("/automoderator", methods=["POST"])
def automoderator():

    if request.method != "POST":
        return False

    data = request.get_json()
    request_id_key = next(iter(data))
    request_id = data[request_id_key]

    title = data["request"][0]["text"]
    comment = data["request"][1]["text"]
    org = data["organisation-name"]
    # call HardRules on the title:
    title = HardRules(body=title, org_name=org).apply()
    title["id"] = "title"
    # call HardRules on the comment:
    comment = HardRules(body=comment, org_name=org).apply()
    comment["id"] = "comment"

    Automoderator = {
        "{}".format(request_id_key): "{}".format(request_id),
        "response": [title, comment],
    }

    return Response(response=json.dumps(Automoderator), content_type="application/json")


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)
