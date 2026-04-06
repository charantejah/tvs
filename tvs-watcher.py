import requests
import time
import os
from datetime import datetime
import zoneinfo

# ===== ENV VARIABLES =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("Missing BOT_TOKEN or CHAT_ID in environment variables")

# ===== TIMEZONE =====
IST = zoneinfo.ZoneInfo("Asia/Kolkata")

def get_ist_time():
    return datetime.now(IST)

def is_night():
    hour = get_ist_time().hour
    return hour >= 23 or hour < 6

# ===== PRODUCTS =====
products = {
    "Tank Guard": "tank-guard",
    "Aluminium Bash Plate": "aluminium-bash-plate",
    "Knuckle Guard": "tvs-apache-rtx-knuckle-guard",
    "Speedometer Scratch Guard": "tvs-apache-rtx-speedometer-scratch-guard-protect-your-ride-preserve-your-style",
    "USB Charger": "usb",
    "Visor Extender": "tvs-apache-rtx-visor-extender-enhanced-wind-protection-stylish-upgrade",
    "Raised Fender": "raised-fender-1",
    "Rear Hugger Fender": "rear-hugger-fender",
    "Top Rack": "top-rack"
}

watch_for_alert = {
    "Tank Guard",
    "Aluminium Bash Plate",
    "Rear Hugger Fender",
    "Top Rack"
}

# ===== STATE =====
last_status = {}
last_summary_time = time.time()
last_update_id = None

runtime_logs = []
night_logs = []
night_changes = set()
night_summary_sent = False

# ===== LOGGER =====
def log(msg):
    timestamp = get_ist_time().strftime('%H:%M:%S')
    full = f"[{timestamp}] {msg}"
    print(full)

    runtime_logs.append(full)
    if len(runtime_logs) > 50:
        runtime_logs.pop(0)

    if is_night():
        night_logs.append(full)
        if len(night_logs) > 100:
            night_logs.pop(0)

# ===== TELEGRAM =====
def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": message,
            "disable_web_page_preview": True
        }, timeout=10)
        log("📲 TELEGRAM SENT")
    except Exception as e:
        log(f"❌ TELEGRAM ERROR: {e}")

# ===== STOCK CHECK =====
def check_stock(name, handle):
    url = f"https://shop.tvsmotor.com/products/{handle}.js"
    headers = {"User-Agent": "Mozilla/5.0"}

    for _ in range(2):
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code != 200 or not r.text.strip():
                continue
            data = r.json()
            return any(v.get("available", False) for v in data.get("variants", []))
        except:
            continue
    return False

# ===== COMMAND HANDLER =====
def check_commands():
    global last_update_id

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        params = {"timeout": 1}

        if last_update_id:
            params["offset"] = last_update_id + 1

        res = requests.get(url, params=params, timeout=5).json()

        for update in res.get("result", []):
            last_update_id = update["update_id"]

            text = update.get("message", {}).get("text", "").lower()

            if text == "logs":
                log("📩 logs requested")
                if runtime_logs:
                    send_telegram("\n".join(runtime_logs[-10:]))
                else:
                    send_telegram("No logs yet.")

            elif text == "nlogs":
                log("📩 nlogs requested")
                if night_logs:
                    send_telegram("🌙 NIGHT LOGS\n\n" + "\n".join(night_logs[-20:]))
                else:
                    send_telegram("🌙 No night logs yet.")

    except Exception as e:
        log(f"Command ERROR: {e}")

# ===== MAIN LOOP =====
if __name__ == "__main__":
    log("🚀 Tracker Started\n")

    while True:
        check_commands()

        current_status = {}

        for name, handle in products.items():
            status = check_stock(name, handle)
            current_status[name] = status

            prev = last_status.get(name)

            # 🔔 ALERTS
            if name in watch_for_alert:
                if prev is not None and prev != status:
                    send_telegram(
                        f"{name} {'IN STOCK 🚀' if status else 'OUT OF STOCK ❌'}\n"
                        f"https://shop.tvsmotor.com/products/{handle}"
                    )

                    if is_night() and status:
                        night_changes.add(name)

        last_status = current_status

        # 🌅 NIGHT SUMMARY AT 6 AM
        if not is_night() and not night_summary_sent and night_changes:
            msg = "🌙 NIGHT SUMMARY\n\n"
            for name in night_changes:
                msg += f"✅ {name}\nhttps://shop.tvsmotor.com/products/{products[name]}\n\n"

            send_telegram(msg)

            night_changes.clear()
            night_logs.clear()
            night_summary_sent = True

        if is_night():
            night_summary_sent = False

        # ☀️ DAY SUMMARY (30 MIN)
        if not is_night() and time.time() - last_summary_time >= 1800:
            msg = f"📊 SUMMARY ({get_ist_time().strftime('%H:%M:%S')})\n\n"

            for name, handle in products.items():
                status = current_status.get(name, False)
                msg += f"{'✅' if status else '❌'} {name}\n\n"

            send_telegram(msg)
            last_summary_time = time.time()

        log("⏳ Waiting 2 minutes...\n")
        time.sleep(120)
