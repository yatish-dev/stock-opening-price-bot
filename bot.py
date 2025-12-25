import os
import requests
import yfinance as yf
from datetime import datetime, timedelta, timezone

# Read secrets from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# -------- Full F&O Stock List (Yahoo .NS symbols) --------
SYMBOLS = [
    "AARTIIND.NS","ABB.NS","ABBOTINDIA.NS","ABCAPITAL.NS","ABFRL.NS","ACC.NS",
    "ADANIENT.NS","ADANIPORTS.NS","ALKEM.NS","AMARAJABAT.NS","AMBUJACEM.NS",
    "APOLLOHOSP.NS","APOLLOTYRE.NS","ASHOKLEY.NS","ASIANPAINT.NS","ASTRAL.NS",
    "ATUL.NS","AUBANK.NS","AUROPHARMA.NS","AXISBANK.NS","BAJAJ-AUTO.NS",
    "BAJAJFINSV.NS","BAJFINANCE.NS","BALKRISIND.NS","BALRAMCHIN.NS",
    "BANDHANBNK.NS","BANKBARODA.NS","BATAINDIA.NS","BEL.NS","BERGEPAINT.NS",
    "BHARATFORG.NS","BHARTIARTL.NS","BHEL.NS","BIOCON.NS","BOSCHLTD.NS",
    "BPCL.NS","BRITANNIA.NS","BSOFT.NS","CANBK.NS","CANFINHOME.NS",
    "CHAMBLFERT.NS","CHOLAFIN.NS","CIPLA.NS","COALINDIA.NS","COFORGE.NS",
    "COLPAL.NS","CONCOR.NS","COROMANDEL.NS","CROMPTON.NS","CUB.NS",
    "CUMMINSIND.NS","DABUR.NS","DALBHARAT.NS","DEEPAKNTR.NS","DELTACORP.NS",
    "DIVISLAB.NS","DIXON.NS","DLF.NS","DRREDDY.NS","EICHERMOT.NS",
    "ESCORTS.NS","EXIDEIND.NS","FEDERALBNK.NS","FSL.NS","GAIL.NS",
    "GLENMARK.NS","GMRINFRA.NS","GNFC.NS","GODREJCP.NS","GODREJPROP.NS",
    "GRANULES.NS","GRASIM.NS","GSPL.NS","GUJGASLTD.NS","HAL.NS",
    "HAVELLS.NS","HCLTECH.NS","HDFC.NS","HDFCAMC.NS","HDFCBANK.NS",
    "HDFCLIFE.NS","HEROMOTOCO.NS","HINDALCO.NS","HINDCOPPER.NS",
    "HINDPETRO.NS","HINDUNILVR.NS","HONAUT.NS","IBULHSGFIN.NS","ICICIBANK.NS",
    "ICICIGI.NS","ICICIPRULI.NS","IDEA.NS","IDFC.NS","IDFCFIRSTB.NS",
    "IEX.NS","IGL.NS","INDHOTEL.NS","INDIACEM.NS","INDIAMART.NS",
    "INDIGO.NS","INDUSINDBK.NS","INDUSTOWER.NS","INFY.NS","INTELLECT.NS",
    "IOC.NS","IPCALAB.NS","IRCTC.NS","ITC.NS","JINDALSTEL.NS",
    "JKCEMENT.NS","JSWSTEEL.NS","JUBLFOOD.NS","KOTAKBANK.NS","L&TFH.NS",
    "LALPATHLAB.NS","LAURUSLABS.NS","LICHSGFIN.NS","LT.NS","LTI.NS",
    "LTTS.NS","LUPIN.NS","M&M.NS","M&MFIN.NS","MANAPPURAM.NS",
    "MARICO.NS","MARUTI.NS","MCDOWELL-N.NS","MCX.NS","METROPOLIS.NS",
    "MFSL.NS","MGL.NS","MINDTREE.NS","MOTHERSON.NS","MPHASIS.NS",
    "MRF.NS","MUTHOOTFIN.NS","NATIONALUM.NS","NAUKRI.NS","NAVINFLUOR.NS",
    "NESTLEIND.NS","NMDC.NS","NTPC.NS","OBEROIRLTY.NS","OFSS.NS",
    "ONGC.NS","PAGEIND.NS","PEL.NS","PERSISTENT.NS","PETRONET.NS",
    "PFC.NS","PIDILITIND.NS","PIIND.NS","PNB.NS","POLYCAB.NS",
    "POWERGRID.NS","PVR.NS","RAIN.NS","RAMCOCEM.NS","RBLBANK.NS",
    "RECLTD.NS","RELIANCE.NS","SAIL.NS","SBICARD.NS","SBILIFE.NS",
    "SBIN.NS","SHREECEM.NS","SIEMENS.NS","SRF.NS","SRTRANSFIN.NS",
    "SUNPHARMA.NS","SUNTV.NS","SYNGENE.NS","TATACHEM.NS","TATACOMM.NS",
    "TATACONSUM.NS","TATAMOTORS.NS","TATAPOWER.NS","TATASTEEL.NS","TCS.NS",
    "TECHM.NS","TITAN.NS","TORNTPHARM.NS","TORNTPOWER.NS","TRENT.NS",
    "TVSMOTOR.NS","UBL.NS","ULTRACEMCO.NS","UPL.NS","VEDL.NS",
    "VOLTAS.NS","WHIRLPOOL.NS","WIPRO.NS","ZEEL.NS","ZYDUSLIFE.NS"
]

NIFTY_SYMBOL = "^NSEI"


def get_open_and_change(ticker: str):
    """Fetch latest daily OHLC and return (open_price, pct_change_from_open)."""
    t = yf.Ticker(ticker)
    hist = t.history(period="2d", interval="1d")
    if hist is None or len(hist) == 0:
        return None, None

    today = hist.iloc[-1]
    open_price = float(today["Open"])
    close_price = float(today["Close"])
    if open_price == 0:
        return None, None

    pct_change = ((close_price - open_price) / open_price) * 100
    return open_price, pct_change


def format_price(v: float) -> str:
    return f"₹{round(v, 2)}"


def build_message() -> str:
    results = []

    for s in SYMBOLS:
        op, pct = get_open_and_change(s)
        if op is None or pct is None:
            continue
        results.append((s.replace(".NS", ""), pct, op))

    gainers = sorted([r for r in results if r[1] >= 0], key=lambda x: x[1], reverse=True)
    losers = sorted([r for r in results if r[1] < 0], key=lambda x: x[1])

    # NIFTY change
    nifty_open, nifty_pct = get_open_and_change(NIFTY_SYMBOL)

    today = datetime.now(timezone.utc) + timedelta(hours=5.5)
    date_str = today.strftime("%Y-%m-%d")

    msg = f"📊 *Opening Price Update* — {date_str}\n"
    if nifty_pct is not None:
        msg += f"\n🟣 NIFTY 50: *{round(nifty_pct,2)}%*"

    msg += "\n\n🔥 *Top Gainers*\n"
    for name, pct, op in gainers[:10]:
        msg += f"{name}  *{round(pct,2)}%*  ({format_price(op)} open)\n"

    msg += "\n💔 *Top Losers*\n"
    for name, pct, op in losers[:10]:
        msg += f"{name}  *{round(pct,2)}%*  ({format_price(op)} open)\n"

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
