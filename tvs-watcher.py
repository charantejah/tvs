import requests
import time
from datetime import datetime

products = {
    "Tank Guard": "tank-guard",
    "Aluminium Bash Plate": "aluminium-bash-plate",
    "Visor Extender": "tvs-apache-rtx-visor-extender-enhanced-wind-protection-stylish-upgrade",
    "Raised Fender": "raised-fender-1",
    "Rear Hugger Fender": "rear-hugger-fender"
}

LOG_FILE = "stock_log.txt"

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    final_msg = f"[{timestamp}] {message}"

    print(final_msg)

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(final_msg + "\n")
    except Exception as e:
        print(f"[LOG ERROR] {e}")


def check_stock(name, handle):
    try:
        url = f"https://shop.tvsmotor.com/products/{handle}.js"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            log(f"[⚠️] {name}: Failed (status {response.status_code})")
            return

        # 🔒 Safe JSON parsing
        try:
            data = response.json()
        except Exception:
            log(f"[⚠️] {name}: Invalid JSON response")
            return

        # 🔒 Safe key access
        variants = data.get("variants", [])
        if not variants:
            log(f"[⚠️] {name}: No variant data found")
            return

        available = any(v.get("available", False) for v in variants)

        if available:
            log(f"[✅] {name} is AVAILABLE")
        else:
            log(f"[❌] {name} is OUT OF STOCK")

    except requests.exceptions.RequestException as e:
        log(f"[🌐] Network issue for {name}: {e}")

    except Exception as e:
        log(f"[ERROR] {name}: {e}")


log("🚀 Starting TVS Stock Tracker...\n")

while True:
    for name, handle in products.items():
        check_stock(name, handle)

    log("⏳ Waiting 5 minutes...\n")
    time.sleep(300)