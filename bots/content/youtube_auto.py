# youtube_auto.py ∴ Z3R0TH YouTube Automation Bot v4.4

import os, sys, json, time, argparse
from datetime import datetime

# 🔧 Core brain import path (absolute to Z3R0TH_ENV)
sys.path.append(os.path.expanduser("~/Desktop/HEX13-Z3R0TH/Z3R0TH_ENV"))
from core.z3r0th_bot import Z3R0THBot

# 📁 Directories
OUTPUT_DIR = os.path.expanduser("~/Desktop/HEX13-Z3R0TH/Z3R0TH_ENV/output/youtube")
MEMORY_DIR = os.path.expanduser("~/Desktop/HEX13-Z3R0TH/Z3R0TH_ENV/core/memory/youtube")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MEMORY_DIR, exist_ok=True)

class YouTubeBot(Z3R0THBot):
    def __init__(self):
        super().__init__(name="YouTubeBot")
        self.log("🎬 YouTubeBot initialized.")

    def run_cycle(self, reuse=False):
        try:
            self.log("⚙ Starting new script cycle...")
            t0 = time.time()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # 🧠 Idea Generation or Recall
            topic = None
            if reuse:
                topic = self.recall("last_idea", category="youtube")
                if not topic:
                    self.log("⚠ No idea in memory. Generating fresh...")
            if not topic:
                topic = self.ask("Give me a unique viral YouTube Shorts idea about making money online.") or "[Fallback Topic]"
            self.remember("last_idea", topic, category="youtube")

            # 🛠 Script Building
            script = self.ask(f"Write a short, punchy 30-45 second YouTube script for this topic: {topic}") or "[No Script Generated]"
            title_raw = self.ask(f"Generate a catchy title for this YouTube Shorts script:\n{script}") or "[Untitled]"
            title = self.ask(f"Optimize this YouTube title for virality: {title_raw}") or title_raw
            tags_raw = self.ask(f"Generate 8 SEO-boosted hashtags for the YouTube video titled:\n{title}") or "#shorts #viral"
            tags = self.ask(f"Refine this hashtag list to make it cleaner:\n{tags_raw}") or tags_raw
            thumbnail_prompt = self.ask(f"Give me a thumbnail idea prompt based on this title: {title}") or "📸 Thumbnail idea not generated."

            # 💾 Save TXT
            txt_filename = f"{timestamp}_short_script.txt"
            txt_path = os.path.join(OUTPUT_DIR, txt_filename)
            with open(txt_path, "w") as f:
                f.write(f"🎬 TITLE:\n{title}\n\n")
                f.write(f"📜 SCRIPT:\n{script}\n\n")
                f.write(f"🏷 TAGS:\n{tags}\n\n")
                f.write(f"🖼 THUMBNAIL:\n{thumbnail_prompt}\n")

            # 💾 Save JSON
            metadata = {
                "timestamp": timestamp,
                "idea": topic,
                "title": title,
                "script": script,
                "tags": tags.split(),
                "thumbnail_prompt": thumbnail_prompt,
                "duration": round(time.time() - t0, 2)
            }
            json_path = os.path.join(OUTPUT_DIR, f"{timestamp}_data.json")
            with open(json_path, "w") as f:
                json.dump(metadata, f, indent=2)

            # 📊 Output Summary
            print(f"\n\033[1;36m🎬 TITLE:\033[0m {title}")
            print(f"\n\033[1;33m📜 SCRIPT:\033[0m\n{script}")
            print(f"\n\033[1;35m🏷 TAGS:\033[0m {tags}")
            print(f"\n\033[1;34m🖼 THUMBNAIL PROMPT:\033[0m {thumbnail_prompt}")
            print(f"\n\033[1;32m💾 Saved:\033[0m {txt_filename}, {os.path.basename(json_path)}")
            print(f"\033[1;90m⏱ Time taken: {metadata['duration']}s\033[0m")

            self.log("✅ Script + metadata successfully saved.")

        except Exception as e:
            error_path = os.path.join(OUTPUT_DIR, "errors.log")
            self.log(f"❌ ERROR: {e}")
            with open(error_path, "a") as errf:
                errf.write(f"[{datetime.now()}] {str(e)}\n")
            print(f"\n\033[1;31m❌ Exception logged to {error_path}\033[0m")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Z3R0TH YouTube Automation Bot")
    parser.add_argument("--reuse", action="store_true", help="♻ Reuse last idea from memory")
    parser.add_argument("--cycles", type=int, default=3, help="🔁 Number of scripts to generate")
    args = parser.parse_args()

    bot = YouTubeBot()
    for i in range(args.cycles):
        print(f"\n\033[1;96m🌐 GENERATION {i+1}/{args.cycles}\033[0m")
        bot.run_cycle(reuse=args.reuse)
