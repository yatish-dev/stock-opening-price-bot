import os
import requests
import yfinance as yf
from datetime import datetime, timedelta, timezone

# -------------------------------
# Telegram Secrets (ENV Variables)
# -------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# -------------------------------
# Your 4 Stocks (Base Symbols)
# -------------------------------
SYMBOLS = ["POLYSIL", "MVKAGRO", "ARUNIS", "SHISHIND"]


# -------------------------------
# Fetch Open & Close (Auto NSE/BSE)
# -------------------------------
def get_open_close(symbol_base: str):
    """Try NSE (.NS) first, then BSE (.BO)."""

    possible_symbols = [
        f"{symbol_base}.NS",
        f"{symbol_base}.BO"
    ]

    for ticker in possible_symbols:
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="2d", interval="1d")

            if hist is not None and len(hist) > 0:
                today = hist.iloc[-1]
                open_price = float(today["Open"])
                close_price = float(today["Close"])

                if open_price == 0:
                    return None, None

                return open_price, close_price

        except Exception:
            continue

    return None, None


# -------------------------------
# Format Price
# -------------------------------
def format_price(v: float) -> str:
    return f"₹{round(v, 2)}"


# -------------------------------
# Build Telegram Message
# -------------------------------
def build_message() -> str:
    today = datetime.now(timezone.utc) + timedelta(hours=5.5)
    date_str = today.strftime("%Y-%m-%d")

    msg = f"📊 *Daily Open & Close Update* — {date_str}\n\n"

    for name in SYMBOLS:
        op, cl = get_open_close(name)

        if op is None or cl is None:
            msg += f"{name} — Data not available\n\n"
        else:
            pct_change = ((cl - op) / op) * 100

            if pct_change > 0:
                change_line = f"   Change: 🟢 +{round(pct_change,2)}%"
            elif pct_change < 0:
                change_line = f"   Change: 🔴 {round(pct_change,2)}%"
            else:
                change_line = f"   Change: ⚪ 0%"

            msg += (
                f"🔹 *{name}*\n"
                f"   Open:  {format_price(op)}\n"
                f"   Close: {format_price(cl)}\n"
                f"{change_line}\n\n"
            )

    return msg


# -------------------------------
# Send Telegram Message
# -------------------------------
def send_message(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("Missing BOT_TOKEN or CHAT_ID environment variables")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }

    requests.post(url, json=payload, timeout=30)


# -------------------------------
# Main Execution
# -------------------------------
if __name__ == "__main__":
    try:
        message = build_message()
        send_message(message)
    except Exception as e:
        print("Error:", e)
