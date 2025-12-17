# 🎅 Secret Santa Anonymous Email Sender

AI-Powered anonymous Secret Santa message delivery system built with Flask (Python) and React.

## Features
- 🔒 100% Anonymous messaging
- 📧 Real email delivery via SMTP
- 🎨 Beautiful festive UI
- ✨ AI-powered message suggestions
- 🛡️ Complete sender identity protection

## Setup Instructions

### Prerequisites
- Python 3.8+
- Gmail account

### Backend Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your email in `backend.py`:
   - Change `OFFICIAL_EMAIL` to your Gmail
   - Get Gmail App Password from https://myaccount.google.com/security
   - Update `GMAIL_APP_PASSWORD`

3. Run the backend:
```bash
python backend.py
```

### Frontend Setup

1. Open `index.html` in a web browser
2. Make sure backend is running on port 5000

## Usage

1. Enter your email (kept private)
2. Enter recipient's email
3. Write your anonymous message
4. Send! Recipient only sees "Secret Santa 🎅"

## Technology Stack
- Backend: Python Flask
- Frontend: React, TailwindCSS
- Email: SMTP (Gmail)

## Project Structure
```
secret-santa/
├── backend.py          # Python Flask server
├── requirements.txt    # Python dependencies
├── index.html         # Frontend website
└── README.md          # This file
```

## License
MIT License - Free to use for personal and educational purposes
```

---

### **File 5: `.gitignore`** (Files NOT to upload to GitHub)
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Sensitive files
*.env
config.py
secrets.txt

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db