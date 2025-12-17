from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib
from datetime import datetime
import traceback
import re

app = Flask(__name__)

# Enable CORS for frontend communication
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:*", "http://127.0.0.1:*", "file://*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# 🔑 EMAIL CONFIGURATION
# IMPORTANT: Change these values to your own!
OFFICIAL_EMAIL = "secretsanta1.noreply@gmail.com"  # ⚠️ CHANGE THIS
GMAIL_APP_PASSWORD = "xkkajzxtyyueztxz"      # ⚠️ CHANGE THIS

# Email validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def validate_email(email):
    """Validate email format"""
    if not email or not isinstance(email, str):
        return False
    return EMAIL_REGEX.match(email.strip()) is not None

def sanitize_input(text):
    """Sanitize user input to prevent injection"""
    if not text:
        return ""
    return str(text).strip()[:2000]  # Limit to 2000 characters

@app.route('/', methods=['GET'])
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'service': 'Secret Santa Anonymous Email Server',
        'version': '1.0.0',
        'anonymous': True,
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Detailed health check"""
    try:
        # Check if email is configured
        is_configured = (
            OFFICIAL_EMAIL != "your-secret-santa@gmail.com" and
            GMAIL_APP_PASSWORD != "xxxx xxxx xxxx xxxx"
        )
        
        return jsonify({
            'status': 'healthy' if is_configured else 'needs_configuration',
            'service': 'Secret Santa Email Server',
            'configured': is_configured,
            'message': 'Ready to send anonymous emails!' if is_configured else 'Please configure email credentials',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/send-anonymous-email', methods=['POST', 'OPTIONS'])
def send_anonymous_email():
    """Send anonymous Secret Santa email"""
    
    # Handle preflight CORS request
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Check if email is configured
        if OFFICIAL_EMAIL == "your-secret-santa@gmail.com":
            return jsonify({
                'success': False,
                'error': 'Email not configured. Please update OFFICIAL_EMAIL in backend.py'
            }), 500
        
        if GMAIL_APP_PASSWORD == "xxxx xxxx xxxx xxxx":
            return jsonify({
                'success': False,
                'error': 'Gmail App Password not configured. Please update GMAIL_APP_PASSWORD in backend.py'
            }), 500
        
        # Get and validate request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Extract and sanitize data
        sender_email = sanitize_input(data.get('senderEmail', ''))
        recipient_email = sanitize_input(data.get('recipientEmail', ''))
        message_text = sanitize_input(data.get('message', ''))
        sender_name = sanitize_input(data.get('senderName', 'Anonymous'))
        
        # Validate required fields
        if not sender_email or not recipient_email or not message_text:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: senderEmail, recipientEmail, and message are required'
            }), 400
        
        # Validate email formats
        if not validate_email(sender_email):
            return jsonify({
                'success': False,
                'error': f'Invalid sender email format: {sender_email}'
            }), 400
        
        if not validate_email(recipient_email):
            return jsonify({
                'success': False,
                'error': f'Invalid recipient email format: {recipient_email}'
            }), 400
        
        # Check message length
        if len(message_text) < 10:
            return jsonify({
                'success': False,
                'error': 'Message too short. Please write at least 10 characters.'
            }), 400
        
        # Create anonymous tracking ID (for logging only)
        tracking_id = hashlib.md5(
            f"{sender_email}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:8]
        
        # Log the request (privately - for your records only)
        print("="*60)
        print(f"📧 ANONYMOUS MESSAGE REQUEST")
        print(f"   Tracking ID: {tracking_id}")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   To: {recipient_email}")
        print(f"   From (Private): {sender_email}")
        print(f"   Sender Name (Private): {sender_name}")
        print(f"   Message Length: {len(message_text)} characters")
        print("="*60)
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"Secret Santa 🎅 <{OFFICIAL_EMAIL}>"
        msg['To'] = recipient_email
        msg['Subject'] = "🎅 You've Got a Secret Santa Message! 🎄"
        # NOTE: No Reply-To header = recipient cannot reply to sender
        
        # HTML email body (beautiful and festive)
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; background-color: #fef2f2;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #fef2f2; padding: 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: white; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: 3px solid #c41e3a;">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 40px 30px 40px; text-align: center;">
                            <h1 style="color: #c41e3a; font-size: 42px; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.1);">
                                🎅 Secret Santa 🎁
                            </h1>
                            <p style="color: #666; font-size: 18px; margin-top: 10px; margin-bottom: 0;">
                                Someone special has a message for you!
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Message Content -->
                    <tr>
                        <td style="padding: 0 40px 30px 40px;">
                            <div style="background: linear-gradient(135deg, #fef2f2 0%, #f0fdf4 100%); padding: 30px; border-radius: 15px; border-left: 5px solid #c41e3a; box-shadow: inset 0 2px 10px rgba(0,0,0,0.05);">
                                <p style="color: #333; font-size: 18px; line-height: 1.8; white-space: pre-wrap; margin: 0;">
{message_text}
                                </p>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Anonymous Notice -->
                    <tr>
                        <td style="padding: 0 40px 30px 40px;">
                            <div style="background: linear-gradient(135deg, #e0e7ff 0%, #fce7f3 100%); padding: 20px; border-radius: 10px; border: 2px dashed #9333ea; text-align: center;">
                                <p style="color: #7e22ce; font-size: 16px; font-weight: bold; margin: 0 0 10px 0;">
                                    🔒 This message was sent anonymously
                                </p>
                                <p style="color: #6b21a8; font-size: 14px; margin: 0;">
                                    The sender's identity is protected by our Secret Santa system.<br>
                                    Enjoy the mystery! 🎄✨
                                </p>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 0 40px 40px 40px; border-top: 2px dashed #e5e7eb; text-align: center;">
                            <p style="color: #999; font-size: 13px; margin: 20px 0 0 0;">
                                🎄 Powered by Secret Santa Anonymous Messaging System 🎄<br>
                                <em>Spreading holiday cheer, one anonymous message at a time!</em>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """
        
        # Plain text version (for email clients that don't support HTML)
        text_body = f"""
🎅 SECRET SANTA MESSAGE 🎁

{message_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔒 This message was sent anonymously.
The sender's identity is protected by our Secret Santa system.
Enjoy the mystery! 🎄✨

🎄 Powered by Secret Santa Anonymous Messaging System 🎄
Spreading holiday cheer, one anonymous message at a time!
        """
        
        # Attach both versions
        msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        
        # Send email via Gmail SMTP
        try:
            # Remove spaces from app password if any
            clean_password = GMAIL_APP_PASSWORD.replace(' ', '')
            
            print(f"📤 Attempting to send email...")
            print(f"   SMTP Server: smtp.gmail.com:587")
            print(f"   From: {OFFICIAL_EMAIL}")
            print(f"   To: {recipient_email}")
            
            with smtplib.SMTP('smtp.gmail.com', 587, timeout=30) as server:
                server.set_debuglevel(0)  # Set to 1 for debug info
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(OFFICIAL_EMAIL, clean_password)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully!")
            print(f"   Tracking ID: {tracking_id}")
            print("="*60 + "\n")
            
            return jsonify({
                'success': True,
                'message': 'Anonymous Secret Santa message sent successfully!',
                'tracking_id': tracking_id,
                'anonymous': True,
                'recipient': recipient_email,
                'timestamp': datetime.now().isoformat()
            }), 200
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ SMTP Authentication Error: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Email authentication failed. Please check your Gmail App Password.',
                'details': 'Make sure you enabled 2-Step Verification and generated an App Password in your Google Account settings.'
            }), 500
            
        except smtplib.SMTPException as e:
            print(f"❌ SMTP Error: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Failed to send email: {str(e)}',
                'details': 'There was a problem with the email server.'
            }), 500
    
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR:")
        print(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}',
            'details': 'An unexpected error occurred. Check server logs.'
        }), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            'GET /',
            'GET /health',
            'POST /send-anonymous-email'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        'error': 'Internal server error',
        'message': str(e)
    }), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎅 SECRET SANTA ANONYMOUS EMAIL SERVER")
    print("="*60)
    print(f"🔒 Anonymity Protection: ACTIVE")
    print(f"📧 Official Email: {OFFICIAL_EMAIL}")
    print(f"🌐 Server starting on: http://localhost:5000")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Check configuration
    if OFFICIAL_EMAIL == "your-secret-santa@gmail.com":
        print("⚠️  WARNING: Email not configured!")
        print("   Please update OFFICIAL_EMAIL in backend.py")
    
    if GMAIL_APP_PASSWORD == "xxxx xxxx xxxx xxxx":
        print("⚠️  WARNING: Gmail App Password not configured!")
        print("   Please update GMAIL_APP_PASSWORD in backend.py")
    
    if OFFICIAL_EMAIL != "your-secret-santa@gmail.com" and GMAIL_APP_PASSWORD != "xxxx xxxx xxxx xxxx":
        print("✅ Configuration looks good!")
        print("   Ready to send anonymous emails!")
    
    print("="*60 + "\n")
    print("📝 Available Endpoints:")
    print("   GET  /              - Server info")
    print("   GET  /health        - Health check")
    print("   POST /send-anonymous-email - Send email")
    print("\n" + "="*60 + "\n")
    
    # Run the server
    app.run(
        host='0.0.0.0',  # Allow external connections
        port=5000,
        debug=True,
        threaded=True
    )