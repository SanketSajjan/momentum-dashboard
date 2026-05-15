import requests
import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup
from supertrend import calculate_supertrend
from stock_indicators import indicators
from stock_indicators.indicators.common.quote import Quote

# ============================================
# 🔹 REGIME ENGINE TEST
# ============================================

print("========== REGIME TEST ==========")

# --------------------------------------------
# NIFTY WEEKLY SUPERTREND
# --------------------------------------------

nifty = yf.download(
    "^NSEI",
    period="3y",
    interval="1wk",
    progress=False,
    auto_adjust=True
)

if isinstance(
    nifty.columns,
    pd.MultiIndex
):
    nifty.columns = (
        nifty.columns.get_level_values(0)
    )

# Convert to Quote objects
quotes = []

for idx, row in nifty.iterrows():

    quotes.append(
        Quote(
            date=idx,
            open=float(row["Open"]),
            high=float(row["High"]),
            low=float(row["Low"]),
            close=float(row["Close"]),
            volume=0
        )
    )

# TradingView-like Supertrend
st = indicators.get_super_trend(
    quotes,
    lookback_periods=10,
    multiplier=3
)

# Latest valid result
latest_st = None

for x in reversed(st):

    if x.super_trend is not None:

        latest_st = float(x.super_trend)

        break

latest_close = float(
    nifty["Close"].iloc[-1]
)

f1 = latest_close > latest_st

print(f"Latest Close : {latest_close}")

print(
    f"Latest Supertrend : "
    f"{latest_st}"
)

print(f"F1 Supertrend : {f1}")

# --------------------------------------------
# NIFTY PE
# --------------------------------------------

try:

    pe_url = "https://www.screener.in/company/NIFTY/"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        pe_url,
        headers=headers
    )

    print(response.status_code)

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    pe = None

    for li in soup.find_all("li"):

        text = li.get_text(" ", strip=True)

        if "P/E" in text:

            print(text)

            parts = text.split()

            for p in parts:

                try:
                    pe = float(p)
                    break
                except:
                    pass

            if pe is not None:
                break

    nifty_pe = pe

except Exception as e:

    print("PE ERROR")

    print(e)

    nifty_pe = None

print(f"NIFTY PE : {nifty_pe}")

# --------------------------------------------
# F2
# --------------------------------------------

f2 = (
    nifty_pe is not None
    and nifty_pe < 25
)

print(f"F2 PE Filter : {f2}")

# --------------------------------------------
# INDIA VIX
# --------------------------------------------

vix_data = yf.download(
    "^INDIAVIX",
    period="6mo",
    interval="1wk",
    progress=False,
    auto_adjust=True
)

if isinstance(
    vix_data.columns,
    pd.MultiIndex
):
    vix_data.columns = (
        vix_data.columns.get_level_values(0)
    )

vix_close = vix_data["Close"]

current_vix = float(
    vix_close.iloc[-1]
)

# 4 weekly candles ago
vix_4w = float(
    vix_close.iloc[-5]
)

vix_change = (
    (current_vix - vix_4w)
    / vix_4w
) * 100

print(f"Current VIX : {current_vix}")

print(f"4W VIX Change : {vix_change}")

# --------------------------------------------
# F3
# --------------------------------------------

f3 = current_vix < 25

print(f"F3 VIX <25 : {f3}")

# --------------------------------------------
# F4
# --------------------------------------------

f4 = not (
    current_vix > 18
    and vix_change > 40
)

print(f"F4 VIX Spike : {f4}")

# --------------------------------------------
# REGIME SCORE
# --------------------------------------------

score = sum([f1, f2, f3, f4])

print(f"SCORE : {score}")

if score >= 3:

    regime = "FULL"

else:

    regime = "HALF"

print(f"REGIME : {regime}")


import json

regime_data = {

    "score": score,

    "regime": regime,

    "factors": {

        "supertrend": f1,

        "peFilter": f2,

        "vixBelow25": f3,

        "vixSpikeSafe": f4
    },

    "marketData": {

        "niftyClose": latest_close,

        "supertrend": latest_st,

        "niftyPE": nifty_pe,

        "indiaVIX": current_vix,

        "vixChange4Week": vix_change
    }
}

with open(
    "data/regime_test.json",
    "w"
) as f:

    json.dump(
        regime_data,
        f,
        indent=4
    )

print("regime_test.json saved")
