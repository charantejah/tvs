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
    "Rear Hugger Fender": "rear-hugger-fender"
}

# ===== ALERT PRODUCTS =====
watch_for_alert = {
    "Tank Guard",
    "Aluminium Bash Plate",
    "Speedometer Scratch Guard",
    "Visor Extender"
}

last_status = {}

# ===== LOGGER =====
def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# ===== TELEGRAM FUNCTION =====
def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": message
        }
        requests.post(url, data=data, timeout=10)
        log("📲 TELEGRAM SENT")
    except Exception as e:
        log(f"❌ TELEGRAM ERROR: {e}")

# ===== STOCK CHECK =====
def check_stock(name, handle):
    try:
        url = f"https://shop.tvsmotor.com/products/{handle}.js"
        response = requests.get(url, timeout=10)

        data = response.json()
        available = any(v.get("available", False) for v in data.get("variants", []))

        prev = last_status.get(name)

        if prev != available:
            last_status[name] = available
            return name, available

    except Exception as e:
        log(f"{name} ERROR: {e}")

    return None, None

# ===== MAIN LOOP =====
if __name__ == "__main__":
    log("🚀 Tracker Started\n")

    while True:
        cycle_changes = []

        for name, handle in products.items():
            pname, status = check_stock(name, handle)

            if pname is not None:
                cycle_changes.append((pname, status))

                # 🔔 ALERT
                if status and pname in watch_for_alert:
                    log(f"🚨 ALERT TRIGGERED for {pname}")

                    send_telegram(
                        f"{pname} IN STOCK 🚀\nhttps://shop.tvsmotor.com/products/{products[pname]}"
                    )

        # ===== CLEAN LOGS =====
        if cycle_changes:
            log("🔄 Changes detected:")
            for n, s in cycle_changes:
                log(f"   {n} → {'AVAILABLE' if s else 'OUT OF STOCK'}")
        else:
            log("✔ No changes")

        log("⏳ Waiting 2 minutes...\n")
        time.sleep(120)