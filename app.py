from flask import Flask, request
import requests
import os
import threading
import json

app = Flask(__name__)

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")


# -----------------------------
# SLASH COMMAND → OPEN MODAL
# -----------------------------
@app.route("/slack/command", methods=["POST"])
def slack_command():
    trigger_id = request.form.get("trigger_id")

    def open_modal():
        url = "https://slack.com/api/views.open"

        headers = {
            "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
            "Content-Type": "application/json"
        }

        data = {
            "trigger_id": trigger_id,
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Log Sentiment"},
                "submit": {"type": "plain_text", "text": "Save"},
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "customer",
                        "label": {"type": "plain_text", "text": "Customer"},
                        "element": {
                            "type": "external_select",
                            "action_id": "value",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Search customer"
                            },
                            "min_query_length": 0
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "sentiment",
                        "label": {"type": "plain_text", "text": "Sentiment"},
                        "element": {
                            "type": "static_select",
                            "action_id": "value",
                            "options": [
                                {"text": {"type": "plain_text", "text": "Positive"}, "value": "positive"},
                                {"text": {"type": "plain_text", "text": "Neutral"}, "value": "neutral"},
                                {"text": {"type": "plain_text", "text": "Negative"}, "value": "negative"}
                            ]
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "topic",
                        "label": {"type": "plain_text", "text": "Topic"},
                        "element": {
                            "type": "static_select",
                            "action_id": "value",
                            "placeholder": {"type": "plain_text", "text": "Select topic"},
                            "options": [
                                {"text": {"type": "plain_text", "text": "Product / Issues"}, "value": "product_issues"},
                                {"text": {"type": "plain_text", "text": "Usage / Testing"}, "value": "usage_testing"},
                                {"text": {"type": "plain_text", "text": "Commercial / Contract"}, "value": "commercial_contract"},
                                {"text": {"type": "plain_text", "text": "Stakeholder / Organization"}, "value": "stakeholder_org"},
                                {"text": {"type": "plain_text", "text": "Other"}, "value": "other"}
                            ]
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "note",
                        "optional": True,
                        "label": {"type": "plain_text", "text": "Note"},
                        "element": {
                            "type": "plain_text_input",
                            "multiline": True,
                            "action_id": "value"
                        }
                    }
                ]
            }
        }

        requests.post(url, headers=headers, json=data)

    threading.Thread(target=open_modal).start()

    return "", 200


# -----------------------------
# DYNAMIC CUSTOMER OPTIONS
# -----------------------------
@app.route("/slack/options", methods=["POST"])
def slack_options():
    query = request.form.get("value", "").lower()

    customers_str = os.environ.get("CUSTOMERS", "")
    customers = [c.strip() for c in customers_str.split(",") if c.strip()]

    options = []

    for customer in customers:
        if query in customer.lower():
            options.append({
                "text": {"type": "plain_text", "text": customer},
                "value": customer
            })

        if len(options) >= 50:
            break

    return {"options": options}


# -----------------------------
# FORM SUBMISSION HANDLER
# -----------------------------
@app.route("/slack/interactions", methods=["POST"])
def interactions():
    payload = request.form.get("payload")
    data = json.loads(payload)

    values = data["view"]["state"]["values"]

    customer = values["customer"]["value"]["selected_option"]["value"]
    sentiment = values["sentiment"]["value"]["selected_option"]["value"]
    topic = values["topic"]["value"]["selected_option"]["value"]

    note_block = values["note"]["value"]
    note = note_block.get("value", "")

    user_id = data["user"]["id"]
    username = data["user"]["username"]

    print("NEW ENTRY:")
    print("Customer:", customer)
    print("Sentiment:", sentiment)
    print("Topic:", topic)
    print("Note:", note)
    print("Logged by:", username, "|", user_id)

    sheet_url = os.environ.get("GOOGLE_SHEETS_WEBHOOK")

    print("NEW ENTRY:")
    print("Customer:", customer)
    print("Sentiment:", sentiment)
    print("Topic:", topic)
    print("Note:", note)
    print("CSM:", username, "|", user_id)

    # 👇 prepare payload
    sheet_payload = {
        "customer": customer,
        "sentiment": sentiment,
        "topic": topic,
        "note": note,
        "user": username,
        "secret": os.environ.get("SHEET_SECRET")
    }

    # 👇 async send (CRITICAL)
    threading.Thread(target=send_to_sheets, args=(sheet_payload,)).start()

    return "", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)