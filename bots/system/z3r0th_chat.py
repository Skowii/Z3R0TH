# z3r0th_chat.py ∴ Z3R0TH Console Companion v14.0 (Optimized for 1920x1080)

import os, sys, json, shutil, subprocess, psutil, platform
from datetime import datetime
from pathlib import Path
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

# ━━━━━━━━━━━ PATH SETUP ━━━━━━━━━━━
ROOT = Path.home() / "Desktop" / "HEX13-Z3R0TH" / "Z3R0TH_ENV"
CORE_DIR = ROOT / "core"
BOT_DIR = ROOT / "bots" / "system"
MEMORY_DIR = CORE_DIR / "memory"
SKILLS_DIR = CORE_DIR / "skills"
IDENTITY_PATH = MEMORY_DIR / "system" / "identity.txt"
LOGS_DIR = CORE_DIR / "logs"
REFLECTIONS_DIR = MEMORY_DIR / "reflections"
WEB_DIR = MEMORY_DIR / "web"
os.makedirs(LOGS_DIR, exist_ok=True)

sys.path.append(str(ROOT))
sys.path.append(str(BOT_DIR))

from core.z3r0th_bot import Z3R0THBot
from web_eyes import search_and_scrape

bot = Z3R0THBot(name="Z3R0THChat")
memory_loaded = ""

# ━━━━━━━━━━━ UTILITIES ━━━━━━━━━━━
def load_all_memory():
    compiled = ""
    if IDENTITY_PATH.exists():
        compiled += f"\n🤖 IDENTITY:\n{IDENTITY_PATH.read_text().strip()}\n"
    for root, _, files in os.walk(MEMORY_DIR):
        for file in files:
            path = os.path.join(root, file)
            if file.endswith(".txt"):
                try:
                    content = Path(path).read_text(encoding="utf-8").strip()
                    if content:
                        rel = os.path.relpath(path, MEMORY_DIR)
                        compiled += f"\n📄 {rel}:\n{content}\n"
                except Exception as e:
                    bot.log(f"[LOAD_ERROR] {file}: {e}")
    return compiled.strip()

def speak(text):
    try:
        subprocess.run(["piper", "--model", "en-us-lessac", "--text", text])
    except:
        pass

def run_skill(label):
    for ext in [".py", ".txt"]:
        skill_path = SKILLS_DIR / f"{label}{ext}"
        if skill_path.exists():
            subprocess.run(["python3", str(skill_path)])
            return
    print(f"❌ Skill '{label}' not found.")

def detect_risky_command(text):
    risky = ["rm -rf", "shutdown", "reboot", "format", "os.remove", "shutil.rmtree"]
    return any(term in text.lower() for term in risky)

def backup_everything():
    dest = ROOT.parent / f"everything_backup_{datetime.now().strftime('%Y%m%d_%H%M')}"
    shutil.copytree(ROOT, dest, dirs_exist_ok=True)
    bot.log(f"[BACKUP] {dest}")
    print(f"✅ Backup created at: {dest}")

def learn_new_skill(label, script_code):
    ext = ".py" if "import" in script_code or "def" in script_code else ".txt"
    file_path = SKILLS_DIR / f"{label}{ext}"
    file_path.write_text(script_code.strip())
    print(f"🧠 Learned skill → {file_path.name}")
    bot.remember(f"learn_{label}", f"Skill '{label}' created", category="system")

def organize_memory():
    cat_map = {
        "crypto": "finance", "bot": "agents", "youtube": "media",
        "tiktok": "media", "linux": "tech", "plugin": "plugins"
    }
    for file in MEMORY_DIR.rglob("*.txt"):
        try:
            content = file.read_text().lower()
            for key, folder in cat_map.items():
                if key in content:
                    new_dir = MEMORY_DIR / folder
                    new_dir.mkdir(exist_ok=True)
                    shutil.move(str(file), new_dir / file.name)
                    print(f"📂 Moved {file.name} → {folder}/")
                    break
        except: pass
# ━━━━━━━━━━━ GUI VOICE INTERFACE ━━━━━━━━━━━
def launch_voice_gui():
    def submit_query():
        user_input = input_box.get("1.0", tk.END).strip()
        input_box.delete("1.0", tk.END)
        if not user_input:
            return
        output_box.insert(tk.END, f"\n👤 You: {user_input}\n", "user")

        def thread_bot():
            try:
                if detect_risky_command(user_input):
                    output_box.insert(tk.END, "⚠ Risky command blocked.\n", "warn")
                    return
                model = "codellama:13b" if any(x in user_input for x in ["code", "script", "automate"]) else "mistral-openorca"
                bot.model = model
                response = bot.ask(prompt=user_input, system=memory_loaded)
                output_box.insert(tk.END, f"\n🤖 Z3R0TH:\n{response}\n", "z3")
                speak(response[:200])
            except Exception as e:
                output_box.insert(tk.END, f"\n[ERROR]: {e}\n", "warn")

        threading.Thread(target=thread_bot).start()

    gui = tk.Tk()
    gui.title("Z3R0TH Voice Interface ∴ Chat GUI")
    gui.geometry("1600x880")  # RESIZED HERE
    gui.configure(bg="#0d0d0d")

    title = tk.Label(gui, text="🧠 Z3R0TH ∴ Voice Console", font=("Helvetica", 16), fg="#39ff14", bg="#0d0d0d")
    title.pack(pady=10)

    output_box = scrolledtext.ScrolledText(gui, width=180, height=30, bg="#121212", fg="#39ff14", insertbackground="#39ff14")
    output_box.pack(padx=10, pady=5)
    output_box.tag_config("user", foreground="#0ff")
    output_box.tag_config("z3", foreground="#39ff14")
    output_box.tag_config("warn", foreground="#ff4444")

    input_box = scrolledtext.ScrolledText(gui, width=180, height=4, bg="#1a1a1a", fg="#00ffff", insertbackground="#00ffff")
    input_box.pack(padx=10, pady=5)

    submit_btn = tk.Button(gui, text="🗣 Speak to Z3R0TH", command=submit_query, bg="#222", fg="#fff")
    submit_btn.pack(pady=8)

    gui.mainloop()
# ━━━━━━━━━━━ MAIN LOOP ━━━━━━━━━━━
print("🧠 Z3R0TH ∴ Console Companion v14.0 Ready.")
print("Type 'exit' to disconnect | 'gui' to launch dashboard | 'voice' for chat panel.\n")

memory_loaded = load_all_memory()

while True:
    try:
        user_input = input("👤 You: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n👁 Z3R0TH: Shutting down.")
        break

    if not user_input:
        continue

    cmd = user_input.lower()

    if cmd == "exit":
        speak("Session ending.")
        break
    elif cmd == "backup":
        backup_everything()
    elif cmd == "reload":
        memory_loaded = load_all_memory()
        print("🔄 Memory reloaded.")
    elif cmd == "reflect":
        print(bot.get_log_tail(50))
    elif cmd == "lastlog":
        for f in sorted(WEB_DIR.glob("*.txt"), key=os.path.getmtime)[-5:]:
            print(f"\n📄 {f.name}:\n{f.read_text()[:1000]}")
    elif cmd == "organize":
        organize_memory()
    elif cmd == "train":
        summary = bot.ask(f"Summarize memory:\n\n{memory_loaded[:4000]}")
        bot.remember("train_" + datetime.now().strftime("%H%M%S"), summary, category="reflections")
        print("🧠 Trained:\n", summary)
    elif cmd == "train recent":
        files = sorted(Path(REFLECTIONS_DIR).glob("*.txt"), key=os.path.getmtime)[-10:]
        content = "\n\n".join(f.read_text() for f in files)
        summary = bot.ask(f"Summarize:\n{content[:4000]}")
        bot.remember("recent_train_" + datetime.now().strftime("%H%M%S"), summary, category="reflections")
        print("🧠 Recent Training:\n", summary)
    elif cmd.startswith("learn:"):
        try:
            _, label, *script = user_input.split(":")
            learn_new_skill(label.strip(), ":".join(script).strip())
        except:
            print("⚠ Use: learn:<label>:<script>")
    elif cmd.startswith("scrape "):
        search_and_scrape(user_input[7:], bot=bot, max_results=3)
    elif cmd.startswith("run skill "):
        run_skill(cmd.split("run skill ")[-1])
    elif cmd == "diagnostics":
        run_skill("diagnostics")
    elif cmd == "gui":
        run_skill("gui_core_dashboard")
    elif cmd == "voice":
        launch_voice_gui()
    elif cmd == "status":
        print(f"🖥 CPU: {psutil.cpu_percent()}% | RAM: {psutil.virtual_memory().percent}% | DISK: {psutil.disk_usage('/').percent}%")
    else:
        model = "codellama:13b" if any(x in user_input for x in ["code", "script", "api", "automation"]) else "mistral-openorca"
        bot.model = model
        print(f"⚙  [Model: {model}]")
        response = bot.ask(prompt=user_input, system=memory_loaded)
        print(f"\n🤖 Z3R0TH:\n{response}\n")
        speak(response[:250])
