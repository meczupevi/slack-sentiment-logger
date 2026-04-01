from flask import Flask, request
import requests
import os

app = Flask(__name__)

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")

@app.route("/slack/command", methods=["POST"])
def slack_command():
    trigger_id = request.form.get("trigger_id")

    url = "https://slack.com/api/views.open"

    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "title": {
                "type": "plain_text",
                "text": "Log Sentiment"
            },
            "submit": {
                "type": "plain_text",
                "text": "Save"
            },
            "blocks": [
                {
                    "type": "input",
                    "block_id": "sentiment",
                    "label": {
                        "type": "plain_text",
                        "text": "Sentiment"
                    },
                    "element": {
                        "type": "static_select",
                        "action_id": "value",
                        "options": [
                            {"text": {"type": "plain_text", "text": "Good"}, "value": "good"},
                            {"text": {"type": "plain_text", "text": "Neutral"}, "value": "neutral"},
                            {"text": {"type": "plain_text", "text": "Bad"}, "value": "bad"}
                        ]
                    }
                },
                {
                    "type": "input",
                    "block_id": "note",
                    "label": {
                        "type": "plain_text",
                        "text": "Notes"
                    },
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "value"
                    }
                }
            ]
        }
    }

    requests.post(url, headers=headers, json=data)

    return "", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)