import requests
import pandas as pd
import yfinance as yf
import json
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings("ignore")

# ============================================
# SETTINGS
# ============================================

INITIAL_CAPITAL = 500000
TOP_STOCKS = 10

# ============================================
# LOAD REGIME DATA
# ============================================

with open(
    "data/regime_test.json",
    "r"
) as f:

    regime_data = json.load(f)

score = regime_data["score"]

regime = regime_data["regime"]

if regime == "FULL":

    req_stock = 80
    req_gold = 20
    req_debt = 0

else:

    req_stock = 40
    req_gold = 30
    req_debt = 30

print(f"Loaded Regime : {regime}")

# ============================================
# FETCH FNO SYMBOLS
# ============================================

def get_fno_symbols():

    url = (
        "https://www.nseindia.com/api/"
        "equity-stockIndices?"
        "index=SECURITIES%20IN%20F%26O"
    )

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.nseindia.com/"
    }

    session = requests.Session()

    session.get(
        "https://www.nseindia.com",
        headers=headers
    )

    data = session.get(
        url,
        headers=headers
    ).json()["data"]

    symbols = []

    for stock in data:

        symbol = stock["symbol"]

        # Remove index symbols
        if symbol in [
            "NIFTY",
            "BANKNIFTY",
            "FINNIFTY",
            "MIDCPNIFTY",
            "NIFTYNXT50"
        ]:
            continue

        symbols.append(symbol + ".NS")

    return symbols

# ============================================
# GET SYMBOLS
# ============================================

symbols = get_fno_symbols()

print(f"Total F&O Stocks : {len(symbols)}")

# ============================================
# DOWNLOAD DATA
# ============================================

end = datetime.today()

start = end - timedelta(days=400)

data = yf.download(
    symbols,
    start=start,
    end=end,
    progress=False,
    auto_adjust=True
)

# ============================================
# SAFE PRICE SELECTION
# ============================================

if isinstance(
    data.columns,
    pd.MultiIndex
):

    if "Adj Close" in data.columns.levels[0]:

        price = data["Adj Close"]

    else:

        price = data["Close"]

else:

    if "Adj Close" in data.columns:

        price = data["Adj Close"]

    else:

        price = data["Close"]

# ============================================
# MOMENTUM CALCULATION
# ============================================

r3 = (
    price.pct_change(63).iloc[-1]
    * 100
)

r6 = (
    price.pct_change(126).iloc[-1]
    * 100
)

r12 = (
    price.pct_change(252).iloc[-1]
    * 100
)

df = pd.DataFrame({

    "Symbol": r3.index.str.replace(
        ".NS",
        "",
        regex=False
    ),

    "12M": r12.values,

    "6M": r6.values,

    "3M": r3.values

}).dropna()

# ============================================
# MOMENTUM SCORE
# ============================================

df["MomentumScore"] = (

    (df["12M"] * 0.50) +

    (df["6M"] * 0.30) +

    (df["3M"] * 0.20)

)

# ============================================
# SORT
# ============================================

df = df.sort_values(
    "MomentumScore",
    ascending=False
).reset_index(drop=True)

df.insert(
    0,
    "Rank",
    range(1, len(df) + 1)
)

print(df.head())

# ============================================
# TOP 20
# ============================================

top20 = df.head(20).copy()

# ============================================
# TOP 10 PORTFOLIO
# ============================================

portfolio_df = df.head(
    TOP_STOCKS
).copy()

allocation_per_stock = (
    INITIAL_CAPITAL / TOP_STOCKS
)

portfolio = []

for _, row in portfolio_df.iterrows():

    symbol = row["Symbol"]

    current_price = float(

        price[symbol + ".NS"]
        .dropna()
        .iloc[-1]

    )

    qty = int(
        allocation_per_stock
        / current_price
    )

    invested_amount = (
        qty * current_price
    )

    portfolio.append({

        "symbol": symbol,

        "price": round(
            current_price,
            2
        ),

        "quantity": qty,

        "investedAmount": round(
            invested_amount,
            2
        ),

        "momentumScore": round(
            row["MomentumScore"],
            2
        )
    })

# ============================================
# FINAL OUTPUT
# ============================================

output = {

    "lastUpdated": datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    ),

    "regime": regime_data,

    "requiredAllocation": {

        "stocks": req_stock,

        "gold": req_gold,

        "debt": req_debt
    },

    "top20": top20.to_dict(
        orient="records"
    ),

    "portfolio": portfolio,

    "capital": INITIAL_CAPITAL
}

# ============================================
# SAVE JSON
# ============================================

with open(
    "data/output.json",
    "w"
) as f:

    json.dump(
        output,
        f,
        indent=4
    )

print("output.json updated successfully")
