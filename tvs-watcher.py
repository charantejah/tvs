import requests
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

EMAIL = "backup1charanteja@gmail.com"
APP_PASSWORD = "dtegbahefstywige"
TO_EMAIL = "charanteja1290@gmail.com"

products = {
    "Tank Guard": "tank-guard",
    "Aluminium Bash Plate": "aluminium-bash-plate",
    "Knuckle Guard": "tvs-apache-rtx-knuckle-guard",
    "Speedometer Scratch Guard": "tvs-apache-rtx-speedometer-scratch-guard-protect-your-ride-preserve-your-style",
    "USB Charger": "usb",
    "Top Rack": "top-rack",
    "Visor Extender": "tvs-apache-rtx-visor-extender-enhanced-wind-protection-stylish-upgrade",
    "Raised Fender": "raised-fender-1",
    "Rear Hugger Fender": "rear-hugger-fender"
}

watch_for_alert = {
    "Tank Guard",
    "Aluminium Bash Plate",
    "Speedometer Scratch Guard"
}

last_status = {}

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def send_email(subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL
        msg["To"] = TO_EMAIL

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(EMAIL, APP_PASSWORD)
            server.send_message(msg)

        log("📧 Email SENT")

    except Exception as e:
        log(f"❌ EMAIL FAILED: {e}")

def check_stock(name, handle):
    try:
        url = f"https://shop.tvsmotor.com/products/{handle}.js"
        response = requests.get(url, timeout=10)

        data = response.json()
        available = any(v.get("available", False) for v in data.get("variants", []))

        prev = last_status.get(name)

        if prev != available:
            status = "AVAILABLE" if available else "OUT OF STOCK"
            log(f"{name} → {status}")
            last_status[name] = available

            # send email only when it becomes available
            if available and name in watch_for_alert:
                send_email(
                    f"{name} IN STOCK 🚀",
                    f"{name} is now available:\nhttps://shop.tvsmotor.com/products/{handle}"
                )

    except Exception as e:
        log(f"{name} ERROR: {e}")

# ===== MAIN LOOP =====
if __name__ == "__main__":
    log("🚀 Tracker Started")

    while True:
        for name, handle in products.items():
            check_stock(name, handle)

        log("⏳ Waiting 2 minutes...\n")
        time.sleep(120)