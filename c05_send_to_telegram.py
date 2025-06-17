import sqlite3
import requests
import os
#import requests

# --- Step 1: Set Telegram Bot credentials ---
# in .env file
from dotenv import load_dotenv
load_dotenv(override=True)
BOT_TOKEN = os.getenv('BOT_TOKEN_SAFE')
CHAT_ID = os.getenv('CHAT_ID_SAFE')

'''code to get chat_id
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
resp = requests.get(url)
print(resp.json())
'''

# --- Step 2: Connect to SQLite DB ---
db_path = "medium.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# --- Step 3: Fetch the latest article with a comment ---
cursor.execute("""
    SELECT article_url, article_comment
    FROM latest_articles
    WHERE article_comment IS NOT NULL
    ORDER BY rowid DESC
    LIMIT 1
""")
latest = cursor.fetchone()
conn.close()

# --- Step 4: Send to Telegram if article exists ---
if latest:
    article_url, article_comment = latest
    message = f"📰 *New Article to Comment On*\n\n🔗 {article_url}\n💬 _Suggested Comment:_\n{article_comment}"

    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    response = requests.post(telegram_url, data=payload)
    
    if response.status_code == 200:
        print("✅ Sent to Telegram!")
    else:
        print(f"❌ Failed to send: {response.text}")
else:
    print("⚠️ No article with a comment found.")