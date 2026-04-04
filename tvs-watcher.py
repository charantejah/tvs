import requests
import time
from datetime import datetime

# ===== TELEGRAM CONFIG =====
BOT_TOKEN = "YOUR_NEW_TOKEN"
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

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

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

def check_stock(name, handle):
    try:
        url = f"https://shop.tvsmotor.com/products/{handle}.js"
        response = requests.get(url, timeout=10)

        data = response.json()
        return any(v.get("available", False) for v in data.get("variants", []))

    except Exception as e:
        log(f"{name} ERROR: {e}")
        return False

# ===== MAIN LOOP =====
if __name__ == "__main__":
    log("🚀 Tracker Started\n")

    while True:
        available_items = []
        message = "🔥 RTX 300 ACCESSORIES IN STOCK 🔥\n\n"

        for name, handle in products.items():
            status = check_stock(name, handle)

            if status:
                available_items.append(name)

                # add to message
                message += f"• {name}\n"
                message += f"https://shop.tvsmotor.com/products/{handle}\n\n"

                # 🚨 spam alert for priority items
                if name in watch_for_alert:
                    log(f"🚨 SPAM ALERT for {name}")

                    send_telegram(
                        f"{name} STILL IN STOCK 🚀\nhttps://shop.tvsmotor.com/products/{handle}"
                    )

        # ===== SUMMARY MESSAGE =====
        if available_items:
            log("✅ Currently Available:")
            for item in available_items:
                log(f"   {item}")

            # send full list once per cycle
            send_telegram(message)

        else:
            log("❌ Nothing in stock")

        log("⏳ Waiting 1 hour\n")
        time.sleep(3600)