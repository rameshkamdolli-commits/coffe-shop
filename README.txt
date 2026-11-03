CHAI & COFFEE SHOP - FLASK PROJECT

1. Install Python 3.10+.
2. Extract this ZIP.
3. Open the extracted folder in VS Code.
4. Open Terminal in this folder and run:
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
5. Open http://127.0.0.1:5000

ADMIN LOGIN (demo credentials):
Username: admin
Password: admin123

IMPORTANT:
- Change app.secret_key and admin credentials before deployment.
- This chatbot is a menu-aware rule-based assistant, not a hosted LLM/ChatGPT integration.
- Orders are stored in SQLite. This demo checkout does not collect or process real payments.
- Product photos use remote Unsplash URLs and need internet access to load.
