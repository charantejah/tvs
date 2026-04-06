available_items = []
unavailable_items = []

for name, handle in products.items():
    status = current_status.get(name, False)

    if status:
        available_items.append((name, handle))
    else:
        unavailable_items.append((name, handle))


# ===== BUILD MESSAGE =====
msg = f"📊 *RTX STOCK SUMMARY ({now_ist().strftime('%H:%M')})*\n\n"

# 🔥 CASE 1: IF ANY STOCK AVAILABLE
if available_items:
    # 👉 Put FIRST available item link at TOP (for preview)
    first_name, first_handle = available_items[0]

    msg = (
        f"https://shop.tvsmotor.com/products/{first_handle}\n\n"
        + msg
    )

    # Available items (TOP)
    msg += "*🟢 Available:*\n"
    for name, handle in available_items:
        msg += f"• *{name}*\n👉 [View](https://shop.tvsmotor.com/products/{handle})\n\n"

    # Unavailable items (below)
    msg += "*🔴 Out of Stock:*\n"
    for name, handle in unavailable_items:
        msg += f"• {name}\n"

    # 👉 ENABLE preview
    preview = False  # FALSE = show preview


# ❌ CASE 2: NOTHING AVAILABLE
else:
    msg += "*🔴 All items are currently out of stock*\n\n"

    for name, handle in products.items():
        msg += f"• {name}\n"

    # 👉 DISABLE preview
    preview = True  # TRUE = no preview
