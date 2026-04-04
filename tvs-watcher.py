import requests
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

# ===== EMAIL CONFIG =====
EMAIL = "backup1charanteja@gmail.com"
APP_PASSWORD = "dtegbahefstywige"
TO_EMAIL = "charanteja1290@gmail.com"

def send_email(subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL
        msg["To"] = TO_EMAIL

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL, APP_PASSWORD)
            server.send_message(msg)

        log("📧 Email sent successfully")

    except Exception as e:
        log(f"[EMAIL ERROR] {e}")


# ===== PRODUCTS =====
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

# Only alert for these
watch_for_alert = {"Tank Guard", "Aluminium Bash Plate","Speedometer Scratch Guard"}

LOG_FILE = "stock_log.txt"
last_status = {}

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    final_msg = f"[{timestamp}] {message}"
    print(final_msg)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(final_msg + "\n")


def check_stock(name, handle):
    try:
        url = f"https://shop.tvsmotor.com/products/{handle}.js"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            log(f"[⚠️] {name}: Failed ({response.status_code})")
            return

        data = response.json()
        available = any(v.get("available", False) for v in data.get("variants", []))

        # Only log when status changes
        if last_status.get(name) != available:
            status_text = "AVAILABLE" if available else "OUT OF STOCK"
            log(f"[🔄] {name} changed → {status_text}")
            last_status[name] = available

            # 🔔 Send email only for important items
            if available and name in watch_for_alert:
                send_email(
                    subject=f"{name} is IN STOCK!",
                    body=f"{name} is now available!\nhttps://shop.tvsmotor.com/products/{handle}"
                )

    except Exception as e:
        log(f"[ERROR] {name}: {e}")


log("🚀 Starting TVS Stock Tracker...\n")

while True:
    for name, handle in products.items():
        check_stock(name, handle)

    log("⏳ Waiting 5 minutes...\n")
    time.sleep(300)