from flask import Flask, request, jsonify
from flask_cors import CORS
import os, re
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

OFFICIAL_EMAIL = os.environ.get("OFFICIAL_EMAIL")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")


@app.route("/health", methods=["GET"])
def health():
    configured = bool(OFFICIAL_EMAIL and GMAIL_APP_PASSWORD)
    return jsonify({
        "status": "healthy" if configured else "needs_configuration",
        "configured": configured
    })
  
def send_email(to_email, message):
    msg = EmailMessage()
    msg["Subject"] = "🎁 You got a Secret Santa message!"
    msg["From"] = OFFICIAL_EMAIL
    msg["To"] = to_email
    msg.set_content(message)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(OFFICIAL_EMAIL, GMAIL_APP_PASSWORD)
        server.send_message(msg)


@app.route("/send-anonymous-email", methods=["POST"])
def send_anonymous_email():
    data = request.get_json()
    to_email = data.get("email")
    message = data.get("message")

    if not to_email or not message:
        return jsonify({"error": "Missing email or message"}), 400


    try:
        send_email(to_email, message)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
