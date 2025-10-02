import os

import requests
from flask import Flask, request

app = Flask(__name__)

GITHUB_TOKEN = os.getenv("LEXCODE_GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPO")


@app.route("/alert", methods=["POST"])
def alert():
    data = request.json
    summary = data["alerts"][0]["annotations"]["summary"]
    desc = data["alerts"][0]["annotations"]["description"]

    response = requests.post(
        f"https://api.github.com/repos/{REPO}/dispatches",
        headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
        json={
            "event_type": "runner_alert",
            "client_payload": {"summary": summary, "desc": desc},
        },
        timeout=10,
    )
    return {"github_status": response.status_code, "summary": summary}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
