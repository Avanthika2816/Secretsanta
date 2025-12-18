from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import smtplib, os, re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

OFFICIAL_EMAIL = os.environ.get("OFFICIAL_EMAIL")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
RESEND_API_KEY= os.environ.get("RESEND_API_KEY")

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

@app.route("/health", methods=["GET"])
def health():
    configured = bool(OFFICIAL_EMAIL and GMAIL_APP_PASSWORD)
    return jsonify({
        "status": "healthy" if configured else "needs_configuration",
        "configured": configured
    })
def send_email_resend(to_email, message):
    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "from": "Secret Santa <no-reply@resend.dev>",
            "to": [to_email],
            "subject": "🎁 You got a Secret Santa message!",
            "text": message
        }
    )

    if response.status_code not in [200, 201]:
        raise Exception(response.text)

@app.route("/send-anonymous-email", methods=["POST", "OPTIONS"])
def send_email():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json()
    recipient = data.get("recipientEmail")
    message = data.get("message")

    if not recipient or not EMAIL_REGEX.match(recipient):
        return jsonify({"error": "Invalid recipient email"}), 400

    if not message or len(message.strip()) == 0:
        return jsonify({"error": "Message cannot be empty"}), 400

    try:
        send_email_resend(recipient, message)
        return jsonify({"success": True}), 200

    except Exception as e:
        print("EMAIL ERROR:", e)
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
