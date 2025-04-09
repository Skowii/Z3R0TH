# plugin_updater.py ∴ Z3R0TH Auto-Updater v7.7 — Smart Updates, Backups, Changelogs, GUI Integration

import os, shutil, requests, json, hashlib, traceback
from pathlib import Path
from datetime import datetime

# ━━━━━━━━━━━ Directories
ROOT          = Path.home() / "Desktop" / "HEX13-Z3R0TH" / "Z3R0TH_ENV"
UPDATES_DIR   = ROOT / "core" / "updates"
BACKUP_DIR    = ROOT / "core" / "backup"
LOG_DIR       = ROOT / "core" / "logs"
REFLECT_DIR   = ROOT / "core" / "memory" / "reflections"

LOG_FILE      = LOG_DIR / "updater.log"
SUMMARY_FILE  = REFLECT_DIR / "last_update_summary.txt"
REMOTE_INDEX  = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/update_index.json"  # ← UPDATE THIS!

# ━━━━━━━━━━━ Init
for d in [UPDATES_DIR, BACKUP_DIR, LOG_DIR, REFLECT_DIR]:
    os.makedirs(d, exist_ok=True)

# ━━━━━━━━━━━ Logging
def log(msg, console=True):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")
    if console:
        print(f"📝 {msg}")

# ━━━━━━━━━━━ Hash Check
def hash_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

# ━━━━━━━━━━━ Fetch Remote Manifest
def fetch_remote_index():
    try:
        res = requests.get(REMOTE_INDEX, timeout=10)
        return res.json()
    except Exception as e:
        log(f"❌ Failed to fetch index: {e}")
        return {}

# ━━━━━━━━━━━ Update Check
def check_for_updates(index):
    updates = []
    for file_rel, meta in index.items():
        local_path = ROOT / file_rel
        if not local_path.exists() or hash_file(local_path) != meta.get("sha256", ""):
            updates.append((file_rel, meta))
    return updates

# ━━━━━━━━━━━ Apply One Update
def apply_update(file_rel, meta):
    dest = ROOT / file_rel
    url = meta.get("url")
    changelog = meta.get("changelog", "No changelog provided.")
    version = meta.get("version", "unknown")

    try:
        # Backup
        if dest.exists():
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{file_rel.replace('/', '__')}__{timestamp}"
            backup_path = BACKUP_DIR / backup_name
            shutil.copy(dest, backup_path)
            log(f"📦 Backed up {file_rel} → {backup_path}")

        # Download update
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f:
            f.write(response.content)

        # Confirm hash
        new_hash = hash_file(dest)
        if new_hash != meta["sha256"]:
            log(f"⚠ Hash mismatch for {file_rel}. Skipping.")
            return

        log(f"✅ Updated {file_rel} → v{version}")
        with open(SUMMARY_FILE, "a") as f:
            f.write(f"\n• {file_rel} → v{version}\n{changelog}\n")
    except Exception as e:
        log(f"❌ Failed to update {file_rel}: {e}")
        traceback.print_exc()

# ━━━━━━━━━━━ Updater Core
def run_updater():
    log("🚀 Z3R0TH Auto-Updater started.")
    try:
        summary = [f"🧬 Z3R0TH Update Summary — {datetime.now().isoformat()}\n"]
        index = fetch_remote_index()
        if not index:
            log("⚠ No updates index found.")
            return

        updates = check_for_updates(index)
        if not updates:
            log("🟢 All systems up to date.")
            return

        log(f"🔄 Updates available: {len(updates)}")
        for file_rel, meta in updates:
            apply_update(file_rel, meta)

        # Reflection
        summary.append(f"\n🔁 Updated {len(updates)} files.\nLogged in: {SUMMARY_FILE.name}")
        SUMMARY_FILE.write_text("\n".join(summary))
        log("📜 Update summary saved to memory.")
    except Exception as err:
        log(f"🚨 Updater crashed: {err}")
        traceback.print_exc()

# ━━━━━━━━━━━ Entry
if __name__ == "__main__":
    run_updater()
