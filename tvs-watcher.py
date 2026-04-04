import requests
import time
from datetime import datetime

# ===== TELEGRAM CONFIG =====
BOT_TOKEN = "8620495010:AAE339ct3WAg62O6BjTfqjI1iU2SFPvB9R4"
CHAT_ID = "2059235733"

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

last_status = {}
last_summary_time = time.time()

night_changes = set()
night_summary_sent = False
last_update_id = None  # 👈 for telegram polling

# ===== UTILS =====
def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

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

def is_night():
    hour = datetime.now().hour
    return hour >= 23 or hour < 6

# ===== STOCK =====
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

# ===== TELEGRAM COMMAND LISTENER =====
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

            message = update.get("message", {})
            text = message.get("text", "").lower()

            if text == "logs":
                log("📩 'logs' command received")

                if night_changes:
                    msg = "🌙 CURRENT NIGHT LOGS\n\n"
                    for name in night_changes:
                        msg += f"✅ {name}\nhttps://shop.tvsmotor.com/products/{products[name]}\n\n"
                else:
                    msg = "🌙 No activity recorded tonight."

                send_telegram(msg)

    except Exception as e:
        log(f"Command ERROR: {e}")

# ===== MAIN =====
if __name__ == "__main__":
    log("🚀 Tracker Started\n")

    while True:
        current_status = {}

        # 👂 listen for commands
        check_commands()

        for name, handle in products.items():
            status = check_stock(name, handle)
            current_status[name] = status

            prev = last_status.get(name)

            if name in watch_for_alert:
                if prev is not None and prev != status:
                    send_telegram(
                        f"{name} {'IN STOCK 🚀' if status else 'OUT OF STOCK ❌'}\n"
                        f"https://shop.tvsmotor.com/products/{handle}"
                    )

                    if is_night() and status:
                        night_changes.add(name)

        last_status = current_status

        # 🌅 6 AM NIGHT SUMMARY
        if not is_night() and not night_summary_sent and night_changes:
            msg = "🌙 NIGHT SUMMARY\n\n"
            for name in night_changes:
                msg += f"✅ {name}\nhttps://shop.tvsmotor.com/products/{products[name]}\n\n"

            send_telegram(msg)
            night_changes.clear()
            night_summary_sent = True

        if is_night():
            night_summary_sent = False

        # ☀️ DAY SUMMARY
        if not is_night() and time.time() - last_summary_time >= 1800:
            msg = f"📊 STOCK SUMMARY ({datetime.now().strftime('%H:%M:%S')})\n\n"

            for name, handle in products.items():
                status = current_status.get(name, False)
                msg += f"{'✅' if status else '❌'} {name}\nhttps://shop.tvsmotor.com/products/{handle}\n\n"

            send_telegram(msg)
            last_summary_time = time.time()

        log("⏳ Waiting 2 minutes...\n")
        time.sleep(120)