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
    "Rear Hugger Fender": "rear-hugger-fender"
}

watch_for_alert = {
    "Tank Guard",
    "Aluminium Bash Plate",
    "Speedometer Scratch Guard",
    "Visor Extender"
}

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

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

def check_stock(name, handle):
    try:
        url = f"https://shop.tvsmotor.com/products/{handle}.js"
        response = requests.get(url, timeout=10)

        data = response.json()
        available = any(v.get("available", False) for v in data.get("variants", []))

        return available

    except Exception as e:
        log(f"{name} ERROR: {e}")
        return False

# ===== MAIN LOOP =====
if __name__ == "__main__":
    log("🚀 Tracker Started\n")

    while True:
        available_items = []

        for name, handle in products.items():
            status = check_stock(name, handle)

            if status:
                available_items.append(name)

                # 🚨 SPAM ALERT
                if name in watch_for_alert:
                    log(f"🚨 SPAM ALERT for {name}")

                    send_telegram(
                        f"{name} STILL IN STOCK 🚀\nhttps://shop.tvsmotor.com/products/{handle}"
                    )

        # ===== CLEAN LOGS =====
        if available_items:
            log("✅ Currently Available:")
            for item in available_items:
                log(f"   {item}")
        else:
            log("❌ Nothing in stock")

        log("⏳ Waiting 2 minutes...\n")
        time.sleep(120)