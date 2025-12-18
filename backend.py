from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib, os, re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app)

OFFICIAL_EMAIL = os.environ.get("OFFICIAL_EMAIL")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

@app.route("/health", methods=["GET"])
def health():
    configured = bool(OFFICIAL_EMAIL and GMAIL_APP_PASSWORD)
    return jsonify({
        "status": "healthy" if configured else "needs_configuration",
        "configured": configured
    })

@app.route("/send-anonymous-email", methods=["POST"])
def send_email():
    data = request.get_json()

    recipient = data.get("recipientEmail")
    message = data.get("message")

    if not recipient or not EMAIL_REGEX.match(recipient):
        return jsonify({"error": "Invalid recipient email"}), 400

    if not message or len(message.strip()) == 0:
        return jsonify({"error": "Message cannot be empty"}), 400

    try:
        msg = MIMEMultipart()
        msg["From"] = f"Secret Santa 🎅 <{OFFICIAL_EMAIL}>"
        msg["To"] = recipient
        msg["Subject"] = "🎁 You got a Secret Santa message!"

        msg.attach(MIMEText(message, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(OFFICIAL_EMAIL, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
