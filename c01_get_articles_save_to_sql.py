import feedparser
import sqlite3

# --- Step 1: Define list of feed URLs ---
feed_urls = [
    "https://generativeai.pub/feed",
    "https://medium.com/feed/illumination"
]

# --- Step 2: Set up SQLite DB ---
db_path = "medium.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# --- Step 3: Create the table if it doesn't exist ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS latest_articles (
    article_name TEXT,
    article_url TEXT UNIQUE,
    article_update_time TEXT,
    feed_url TEXT
)
""")

# --- Step 4: Loop through feeds and insert articles ---
for feed_url in feed_urls:
    feed = feedparser.parse(feed_url)
    print(f"🔍 Checking feed: {feed_url} — Found {len(feed.entries)} entries")

    for entry in feed.entries:
        title = entry.title
        link = entry.link
        update_time = getattr(entry, 'published', getattr(entry, 'updated', 'N/A'))

        # Check if this article already exists
        cursor.execute("SELECT * FROM latest_articles WHERE article_url = ?", (link,))
        exists = cursor.fetchone()

        if not exists:
            cursor.execute("""
                INSERT INTO latest_articles (article_name, article_url, article_update_time, feed_url)
                VALUES (?, ?, ?, ?)
            """, (title, link, update_time, feed_url))
            print(f"✅ Added: {title}")
        else:
            print(f"⏩ Skipped (already exists): {title}")

# --- Step 5: Commit & close ---
conn.commit()
conn.close()

print("🎉 Done updating articles from all feeds.")