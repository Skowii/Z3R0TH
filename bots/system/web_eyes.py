# web_eyes.py ∴ Z3R0TH Autonomous Web Intelligence Engine v4.0
import os, re, json, time, requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from newspaper import Article
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# 📂 Target memory location
MEMORY_DIR = Path.home() / "Desktop" / "HEX13-Z3R0TH" / "Z3R0TH_ENV" / "core" / "memory" / "web"
os.makedirs(MEMORY_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
}

# 🧼 Clean + Normalize scraped text
def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    return text.strip()

# 🔍 DuckDuckGo Smart Search
def search_duckduckgo(query, max_results=3):
    with DDGS() as ddgs:
        return list(ddgs.text(query, max_results=max_results))

# 🧠 Extract title + article body
def extract_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.title.strip(), clean_text(article.text)
    except Exception as e:
        print(f"⚠ Failed to extract article → {url}\n⛔ {e}")
        return None, None

# 💾 Store scraped knowledge
def save_to_memory(title, url, content, bot=None):
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = re.sub(r"[^a-zA-Z0-9]", "_", title.lower())[:60]
    filename = f"{now}__{safe_title}.txt"
    filepath = MEMORY_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# 🔗 {url}\n\n{content}")

    if bot:
        bot.log(f"🌐 Web memory ingested: {filename}")
    print(f"✅ Saved: {filename}")

# 🌐 Master Search + Scrape Routine
def search_and_scrape(query, bot=None, max_results=3):
    print(f"🔍 Searching for: '{query}'")
    results = search_duckduckgo(query, max_results=max_results)

    if not results:
        print("⚠ No results.")
        return

    for i, res in enumerate(results):
        url = res.get("href") or res.get("url")
        if not url:
            continue
        print(f"🌐 [{i+1}] {url}")
        title, content = extract_article(url)
        if title and content:
            save_to_memory(title, url, content, bot)
        else:
            print(f"⚠ Skipped: {url}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔮 NEW INTELLIGENT WEB FEATURES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def extract_keywords(text):
    return list(set(re.findall(r"\b\w{5,}\b", text.lower())))

def auto_summarize_article(content, max_sentences=5):
    sentences = re.split(r'[.!?]', content)
    return '. '.join(sentences[:max_sentences]) + "..."

def categorize_article(content):
    categories = {
        "ai": ["neural", "language model", "machine learning", "deep learning"],
        "crypto": ["bitcoin", "blockchain", "token", "ethereum"],
        "privacy": ["surveillance", "vpn", "proxy", "anonymity"],
        "darkweb": ["tor", ".onion", "darknet", "silk road"],
        "ecommerce": ["dropship", "store", "ecommerce", "shopify"],
        "automation": ["script", "automate", "bot", "process"],
        "espionage": ["spy", "tracking", "surveillance", "osint"]
    }
    for cat, terms in categories.items():
        if any(term in content.lower() for term in terms):
            return cat
    return "uncategorized"

# 🧬 Self-evolving multi-query scraper
def recursive_scrape(seed_topic, depth=2, bot=None):
    queue = [seed_topic]
    visited = set()

    for _ in range(depth):
        if not queue:
            break
        current = queue.pop(0)
        visited.add(current)

        print(f"🔁 Recursive scrape: {current}")
        results = search_duckduckgo(current, max_results=3)
        for res in results:
            url = res.get("href") or res.get("url")
            if not url or url in visited:
                continue
            title, content = extract_article(url)
            if title and content:
                save_to_memory(title, url, content, bot)
                queue.extend(extract_keywords(content)[:3])  # Expand next layer from keywords
            time.sleep(2)

# 🕵️ Dark pattern + scam detection (basic)
def detect_malicious_content(text):
    patterns = ["earn $$$", "free bitcoin", "hacked account", "send wallet", "decryption key"]
    return any(p.lower() in text.lower() for p in patterns)

# 🤖 Threat analysis + classification
def analyze_scraped_content(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        category = categorize_article(content)
        threat = "⚠️ Potential Scam" if detect_malicious_content(content) else "✅ Clean"
        summary = auto_summarize_article(content)
        print(f"\n📑 Analysis of {filepath.name}")
        print(f"📂 Category: {category}")
        print(f"🔎 Threat Check: {threat}")
        print(f"📝 Summary: {summary}")
    except Exception as e:
        print(f"⚠ Failed to analyze: {e}")

# 🌍 Smart scraper loop — For evolving understanding
def smart_web_loop(topic_list, rounds=3, bot=None):
    for round_num in range(rounds):
        print(f"\n🌐 Round {round_num+1} — Smart Loop")
        for topic in topic_list:
            recursive_scrape(topic, depth=1, bot=bot)
        print("🌀 Loop pause for cooldown...\n")
        time.sleep(5)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Utility CLI (Optional)
if __name__ == "__main__":
    topic = input("Enter a search topic for recursive scrape: ").strip()
    recursive_scrape(topic, depth=2)
