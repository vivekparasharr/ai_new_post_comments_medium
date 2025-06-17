import sqlite3
from ollama import Client

# --- Step 1: Set up DB and column ---
db_path = "medium.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Add 'article_comment' column if it doesn't exist
cursor.execute("PRAGMA table_info(latest_articles)")
columns = [col[1] for col in cursor.fetchall()]
if "article_comment" not in columns:
    cursor.execute("ALTER TABLE latest_articles ADD COLUMN article_comment TEXT")

# --- Step 2: Fetch articles that need commenting ---
cursor.execute("""
    SELECT rowid, article_summary 
    FROM latest_articles 
    WHERE article_summary IS NOT NULL AND article_comment IS NULL
""")
articles = cursor.fetchall()

print(f"💬 Found {len(articles)} article(s) that need comments.\n")

# --- Step 3: Set up Ollama client ---
client = Client(host='http://localhost:11434')
model_name = "llama3.2:latest"

# --- Step 4: Generate comments and update DB ---
for rowid, summary in articles:
    try:
        prompt = (
            f"You are Vivek, a data-driven professional with a deep interest in AI, "
            f"generative tech, and analytics. Based on this article summary, write a thoughtful "
            f"and conversational comment that Vivek could realistically post on Medium to contribute to the discussion. "
            f"The tone should be authentic and mildly curious, maybe asking a question or reflecting on the insight.\n\n"
            f"Article Summary:\n{summary}"
        )

        response = client.chat(model=model_name, messages=[{"role": "user", "content": prompt}])
        comment = response['message']['content'].strip()

        cursor.execute(
            "UPDATE latest_articles SET article_comment = ? WHERE rowid = ?",
            (comment, rowid)
        )
        print(f"✅ Comment generated for article #{rowid}")

    except Exception as e:
        print(f"⚠️ Error generating comment for article #{rowid}: {e}")

conn.commit()
conn.close()
print("\n🏁 Done generating comments.")
