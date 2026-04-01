from flask import Flask, request

app = Flask(__name__)

@app.route("/slack/command", methods=["POST"])
def slack_command():
    print(request.form)
    return "Slack command received ✅"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)