import sqlite3
from ollama import Client

# --- Step 1: Set up DB and check column ---
db_path = "medium.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Add new column for article summary if not exists
cursor.execute("PRAGMA table_info(latest_articles)")
columns = [col[1] for col in cursor.fetchall()]
if "article_summary" not in columns:
    cursor.execute("ALTER TABLE latest_articles ADD COLUMN article_summary TEXT")

# --- Step 2: Fetch articles that need summarizing ---
cursor.execute("""
    SELECT rowid, article_text 
    FROM latest_articles 
    WHERE article_summary IS NULL AND article_text IS NOT NULL
""")
articles = cursor.fetchall()

print(f"📝 Found {len(articles)} article(s) that need summaries.\n")

# --- Step 3: Setup Ollama client ---
client = Client(host='http://localhost:11434')  # default Ollama endpoint
model_name = "llama3.2:latest"  # 🔁 Use llama3.2 or whichever tag you've pulled

# --- Step 4: Generate summaries and update DB ---
for rowid, text in articles:
    try:
        prompt = f"Summarize the following Medium article in 3-5 sentences:\n\n{text[:6000]}"
        response = client.chat(model=model_name, messages=[{"role": "user", "content": prompt}])
        summary = response['message']['content'].strip()

        cursor.execute(
            "UPDATE latest_articles SET article_summary = ? WHERE rowid = ?",
            (summary, rowid)
        )
        print(f"✅ Summary added for article #{rowid}")

    except Exception as e:
        print(f"⚠️ Error summarizing article #{rowid}: {e}")

conn.commit()
conn.close()
print("\n🏁 Done updating summaries.")