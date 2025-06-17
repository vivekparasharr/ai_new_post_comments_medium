import sqlite3
import requests
from bs4 import BeautifulSoup

# --- Step 1: Connect to DB and add article_text column if not exists ---
db_path = "medium.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Add new column for article text if it doesn't exist
cursor.execute("PRAGMA table_info(latest_articles)")
columns = [col[1] for col in cursor.fetchall()]
if "article_text" not in columns:
    cursor.execute("ALTER TABLE latest_articles ADD COLUMN article_text TEXT")

# --- Step 2: Get all articles that don't have text yet ---
cursor.execute("SELECT rowid, article_url FROM latest_articles WHERE article_text IS NULL")
articles = cursor.fetchall()

print(f"🔍 Found {len(articles)} article(s) without extracted text.\n")

# --- Step 3: Scrape article text and update DB ---
def extract_text_from_medium(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        # Medium content is inside <article> tags
        article_tag = soup.find("article")
        if not article_tag:
            return None

        # Collect all <p> tags from article body
        paragraphs = article_tag.find_all("p")
        content = "\n\n".join(p.get_text(strip=True) for p in paragraphs)
        return content if content.strip() else None

    except Exception as e:
        print(f"⚠️ Error fetching {url}: {e}")
        return None

updated = 0

for rowid, url in articles:
    text = extract_text_from_medium(url)
    if text:
        cursor.execute("UPDATE latest_articles SET article_text = ? WHERE rowid = ?", (text, rowid))
        updated += 1
        print(f"✅ Saved text for: {url}")
    else:
        print(f"❌ No text found for: {url}")

conn.commit()
conn.close()

print(f"\n🏁 Done. Updated {updated} article(s) with extracted text.")