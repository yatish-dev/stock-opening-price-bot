import os
import requests
import yfinance as yf
from datetime import datetime, timedelta, timezone

# Read secrets from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# -------- ONLY Your 4 Stocks --------
SYMBOLS = {
    "POLYSIL": "POLYSIL.NS",
    "MVKAGRO": "MVKAGRO.NS",
    "ARUNIS": "ARUNIS.NS",
    "SHISHIND": "SHISHIND.NS"
}


def get_open_close(ticker: str):
    """Fetch latest daily Open & Close price."""
    t = yf.Ticker(ticker)
    hist = t.history(period="2d", interval="1d")

    if hist is None or len(hist) == 0:
        return None, None

    today = hist.iloc[-1]
    open_price = float(today["Open"])
    close_price = float(today["Close"])

    return open_price, close_price


def format_price(v: float) -> str:
    return f"₹{round(v, 2)}"


def build_message() -> str:
    today = datetime.now(timezone.utc) + timedelta(hours=5.5)
    date_str = today.strftime("%Y-%m-%d")

    msg = f"📊 *Daily Open & Close Update* — {date_str}\n\n"

    for name, symbol in SYMBOLS.items():
        op, cl = get_open_close(symbol)

        if op is None or cl is None:
            msg += f"{name} — Data not available\n"
        else:
            msg += (
                f"🔹 *{name}*\n"
                f"   Open:  {format_price(op)}\n"
                f"   Close: {format_price(cl)}\n\n"
            )

    return msg


def send_message(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("Missing BOT_TOKEN or CHAT_ID env")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }

    requests.post(url, json=payload, timeout=30)


if __name__ == "__main__":
    try:
        message = build_message()
        send_message(message)
    except Exception as e:
        print("Error:", e)
