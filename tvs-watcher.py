import requests
import time
from datetime import datetime

# ===== TELEGRAM CONFIG =====
BOT_TOKEN = "8620495010:AAE339ct3WAg62O6BjTfqjI1iU2SFPvB9R4"
CHAT_ID = "2059235733"

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

# ===== IMPORTANT ITEMS =====
watch_for_alert = {
    "Tank Guard",
    "Aluminium Bash Plate",
    "Rear Hugger Fender",
    "Top Rack"
}

last_status = {}
last_summary_time = time.time()

# ===== LOGGER =====
def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# ===== TELEGRAM =====
def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": message,
            "disable_web_page_preview": True
        }
        requests.post(url, data=data, timeout=10)
        log("📲 TELEGRAM SENT")
    except Exception as e:
        log(f"❌ TELEGRAM ERROR: {e}")

# ===== STOCK CHECK (FIXED) =====
def check_stock(name, handle):
    url = f"https://shop.tvsmotor.com/products/{handle}.js"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for attempt in range(2):  # retry once
        try:
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                continue

            if not response.text.strip():
                continue

            data = response.json()
            return any(v.get("available", False) for v in data.get("variants", []))

        except Exception:
            if attempt == 1:
                log(f"{name} ERROR: Failed after retry")
                return False

    return False

# ===== MAIN LOOP =====
if __name__ == "__main__":
    log("🚀 Tracker Started\n")

    while True:
        current_status = {}

        # 🔁 CHECK EVERY 2 MIN
        for name, handle in products.items():
            status = check_stock(name, handle)
            current_status[name] = status

            prev = last_status.get(name)

            # 🔔 ALERT ON CHANGE (important items only)
            if name in watch_for_alert:
                if prev is not None and prev != status:
                    log(f"🚨 CHANGE DETECTED: {name}")

                    send_telegram(
                        f"{name} {'IN STOCK 🚀' if status else 'OUT OF STOCK ❌'}\n"
                        f"https://shop.tvsmotor.com/products/{handle}"
                    )

        last_status = current_status

        # ⏰ SUMMARY EVERY 30 MIN
        if time.time() - last_summary_time >= 1800:
            log("📊 Sending 30-min summary")

            msg = f"📊 RTX STOCK SUMMARY ({datetime.now().strftime('%H:%M:%S')})\n\n"

            for name, handle in products.items():
                status = current_status.get(name, False)

                msg += f"{'✅' if status else '❌'} {name}\n"
                msg += f"https://shop.tvsmotor.com/products/{handle}\n\n"

            send_telegram(msg)
            last_summary_time = time.time()

        log("⏳ Waiting 2 minutes...\n")
        time.sleep(120)