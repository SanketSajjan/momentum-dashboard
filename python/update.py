import pandas as pd
import yfinance as yf
import json
from datetime import datetime
import time

# =========================
# SETTINGS
# =========================

INITIAL_CAPITAL = 500000
TOP_STOCKS = 10

# =========================
# GET NIFTY LARGEMIDCAP 250
# =========================
import requests
from io import StringIO

csv_url = "https://www.niftyindices.com/IndexConstituent/ind_niftylargemidcap250list.csv"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(csv_url, headers=headers)
csv_data = StringIO(response.text)
stocks_df = pd.read_csv(csv_data)

stocks_df.columns = stocks_df.columns.str.strip()
print(stocks_df.columns)

symbol_column = [col for col in stocks_df.columns if 'Symbol' in col][0]
symbols = stocks_df[symbol_column].tolist()

# Add .NS suffix
symbols = [symbol + '.NS' for symbol in symbols]

# Remove dummy symbols
symbols = [s for s in symbols if 'DUMMY' not in s]

results = []

print(f"Total Stocks: {len(symbols)}")

# =========================
# CALCULATE RETURNS
# =========================
for symbol in symbols:

    time.sleep(1)

    try:

        print(f"Processing: {symbol}")

        data = yf.download(
            symbol,
            period='1y',
            progress=False,
            auto_adjust=True
        )

        if data.empty:
            continue

        close_prices = data['Close'].squeeze()

        if len(close_prices) < 130:
            continue

        current_price = float(close_prices.iloc[-1])

        price_3m = float(close_prices.iloc[-63])

        price_6m = float(close_prices.iloc[-126])

        price_12m = float(close_prices.iloc[0])

        return_3m = (
            (current_price - price_3m)
            / price_3m
        ) * 100

        return_6m = (
            (current_price - price_6m)
            / price_6m
        ) * 100

        return_12m = (
            (current_price - price_12m)
            / price_12m
        ) * 100

        momentum_score = (
            (return_12m * 0.50) +
            (return_6m * 0.30) +
            (return_3m * 0.20)
        )

        results.append({
            'symbol': symbol.replace('.NS', ''),
            'currentPrice': round(current_price, 2),
            'return3M': round(return_3m, 2),
            'return6M': round(return_6m, 2),
            'return12M': round(return_12m, 2),
            'momentumScore': round(momentum_score, 2)
        })

    except Exception as e:

        print(f"Error in {symbol}: {e}")

# =========================
# CREATE DATAFRAME
# =========================
print(results[:5])
momentum_df = pd.DataFrame(results)

print(momentum_df.head())

print(f"Total valid stocks: {len(momentum_df)}")

if momentum_df.empty:
    raise Exception("No valid momentum data generated")

momentum_df = momentum_df.sort_values(
    by='momentumScore',
    ascending=False
)

# Top 20 stocks

top20_df = momentum_df.sort_values(
    by='momentumScore',
    ascending=False
).head(20)

# =========================
# TOP 10 PORTFOLIO
# =========================

portfolio_df = momentum_df.head(TOP_STOCKS).copy()

allocation_per_stock = INITIAL_CAPITAL / TOP_STOCKS

portfolio_data = []

for _, row in portfolio_df.iterrows():

    qty = int(allocation_per_stock / row['currentPrice'])

    invested_amount = qty * row['currentPrice']

    portfolio_data.append({
        'symbol': row['symbol'],
        'price': row['currentPrice'],
        'quantity': qty,
        'investedAmount': round(invested_amount, 2),
        'momentumScore': row['momentumScore']
    })

# =========================
# OUTPUT JSON
# =========================

output = {
    'lastUpdated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'top20': top20_df.to_dict(orient='records'),
    'portfolio': portfolio_data,
    'capital': INITIAL_CAPITAL
}

with open('data/output.json', 'w') as f:
    json.dump(output, f, indent=4)

print('output.json updated successfully')
