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
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# ✅ FIXED SMTP (PORT 587)
def send_email(subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL
        msg["To"] = TO_EMAIL

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
            server.starttls()
            server.login(EMAIL, APP_PASSWORD)
            server.send_message(msg)

        log("📧 EMAIL SENT")

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

                # send email only when becomes available
                if status and pname in watch_for_alert:
                    send_email(
                        f"{pname} IN STOCK 🚀",
                        f"{pname} is now available:\nhttps://shop.tvsmotor.com/products/{handle}"
                    )

        # ✅ CLEAN LOG OUTPUT
        if cycle_changes:
            log("🔄 Changes detected:")
            for n, s in cycle_changes:
                log(f"   {n} → {'AVAILABLE' if s else 'OUT OF STOCK'}")
        else:
            log("✔ No changes")

        log("⏳ Waiting 2 minutes...\n")
        time.sleep(120)