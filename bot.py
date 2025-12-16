import yfinance as yf
import pandas as pd
import requests
import os
from datetime import date

# Get secrets from GitHub
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Load stock list
stocks = pd.read_csv("stocks.csv")
symbols = stocks["symbol"].tolist()

# Download last 2 days to calculate change vs previous close
data = yf.download(
    tickers=symbols,
    period="2d",
    group_by="ticker",
    threads=True
)

message_lines = []
message_lines.append(f"📊 Opening Price Update – {date.today()}\n")

for _, row in stocks.iterrows():
    symbol = row["symbol"]
    name = row["name"]

    try:
        today_open = data[symbol]["Open"].iloc[-1]
        prev_close = data[symbol]["Close"].iloc[-2]

        change = ((today_open - prev_close) / prev_close) * 100
        change = round(change, 2)
        today_open = round(today_open, 2)

        sign = "+" if change >= 0 else ""

        message_lines.append(
            f"{name}  {sign}{change}%  {{₹{today_open} open}}"
        )
    except Exception:
        continue

# Join message
message = "\n".join(message_lines)

# Send to Telegram
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
requests.post(url, data={
    "chat_id": CHAT_ID,
    "text": message
})
