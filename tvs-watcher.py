import requests
import time
import os
from datetime import datetime
import zoneinfo

# ===== ENV =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("Missing BOT_TOKEN or CHAT_ID")

# ===== TIME =====
IST = zoneinfo.ZoneInfo("Asia/Kolkata")

def now_ist():
    return datetime.now(IST)

def is_night():
    h = now_ist().hour
    return h >= 23 or h < 6

# ===== CONFIG =====
IMPORTANT_INTERVAL = 30
NORMAL_INTERVAL = 120

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
    "Top Rack",
    "Visor Extender",
    "Rear Hugger Fender",
    "Aluminium Bash Plate",
    "Speedometer Scratch Guard"
}

# ===== STATE =====
last_status = {}
last_summary_time = time.time()
last_update_id = None

runtime_logs = []
night_logs = []
night_changes = set()
night_summary_sent = False

last_important_check = 0
last_normal_check = 0

# ===== LOGGER =====
def log(msg):
    t = now_ist().strftime('%H:%M:%S')
    line = f"[{t}] {msg}"
    print(line)

    runtime_logs.append(line)
    if len(runtime_logs) > 50:
        runtime_logs.pop(0)

    if is_night():
        night_logs.append(line)
        if len(night_logs) > 100:
            night_logs.pop(0)

# ===== TELEGRAM =====
def send(msg, no_preview=False):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": msg,
                "parse_mode": "Markdown",
                "disable_web_page_preview": no_preview
            },
            timeout=10
        )
        log("📲 Sent")
    except Exception as e:
        log(f"❌ Telegram error: {e}")

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

# ===== COMMANDS =====
def check_commands():
    global last_update_id
    try:
        params = {"timeout": 1}
        if last_update_id:
            params["offset"] = last_update_id + 1

        res = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
            params=params,
            timeout=5
        ).json()

        for upd in res.get("result", []):
            last_update_id = upd["update_id"]
            text = upd.get("message", {}).get("text", "").lower()

            if text == "logs":
                send("🧾 *Recent Logs*\n\n" + "\n".join(runtime_logs[-10:]))

            elif text == "nlogs":
                if night_logs:
                    send("🌙 *Night Logs*\n\n" + "\n".join(night_logs[-20:]))
                else:
                    send("🌙 No activity recorded tonight.")

    except Exception as e:
        log(f"Cmd error: {e}")

# ===== MAIN =====
if __name__ == "__main__":
    log("🚀 Tracker Started")

    while True:
        now = time.time()
        check_commands()

        # ⚡ FAST CHECK
        if now - last_important_check >= IMPORTANT_INTERVAL:
            log("⚡ Fast check")

            for name in watch_for_alert:
                handle = products[name]
                status = check_stock(name, handle)

                prev = last_status.get(name)

                if prev is not None and prev != status:
                    msg = (
                        f"🚨 *{name}*\n\n"
                        f"{'🟢 *IN STOCK*' if status else '🔴 OUT OF STOCK'}\n"
                        f"[Buy Now](https://shop.tvsmotor.com/products/{handle})"
                    )
                    send(msg)

                    if is_night() and status:
                        night_changes.add(name)

                last_status[name] = status

            last_important_check = now

        # 🔄 FULL CHECK
        if now - last_normal_check >= NORMAL_INTERVAL:
            log("🔄 Full check")

            current_status = {}

            for name, handle in products.items():
                status = check_stock(name, handle)
                current_status[name] = status
                last_status[name] = status

            # 🌅 NIGHT SUMMARY
            if not is_night() and not night_summary_sent and night_changes:
                msg = "🌙 *Night Summary*\n\n"
                for n in night_changes:
                    msg += f"🟢 *{n}*\n[Open](https://shop.tvsmotor.com/products/{products[n]})\n\n"

                send(msg)
                night_changes.clear()
                night_logs.clear()
                night_summary_sent = True

            if is_night():
                night_summary_sent = False

            # 📊 SUMMARY WITH SMART PREVIEW
            if not is_night() and now - last_summary_time >= 1800:

                available = []
                unavailable = []

                for n, h in products.items():
                    if current_status.get(n, False):
                        available.append((n, h))
                    else:
                        unavailable.append((n, h))

                msg = f"📊 *RTX STOCK SUMMARY ({now_ist().strftime('%H:%M')})*\n\n"

                if available:
                    # 👇 FIRST LINK AT TOP (FOR PREVIEW)
                    first_name, first_handle = available[0]
                    msg = f"https://shop.tvsmotor.com/products/{first_handle}\n\n" + msg

                    msg += "*🟢 Available:*\n"
                    for n, h in available:
                        msg += f"• *{n}*\n👉 [View](https://shop.tvsmotor.com/products/{h})\n\n"

                    msg += "*🔴 Out of Stock:*\n"
                    for n, _ in unavailable:
                        msg += f"• {n}\n"

                    send(msg, no_preview=False)

                else:
                    msg += "*🔴 All items out of stock*\n\n"
                    for n, _ in products.items():
                        msg += f"• {n}\n"

                    send(msg, no_preview=True)

                last_summary_time = now

            last_normal_check = now

        time.sleep(5)
