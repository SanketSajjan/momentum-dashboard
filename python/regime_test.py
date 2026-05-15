import pandas_ta as ta
from bs4 import BeautifulSoup

# ============================================
# 🔹 REGIME ENGINE TEST
# ============================================

print("========== REGIME TEST ==========")

# --------------------------------------------
# TEMPORARY F1
# --------------------------------------------

f1 = True

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

try:

    vix_data = yf.download(
        "^INDIAVIX",
        period="2mo",
        progress=False,
        auto_adjust=True
    )

    if isinstance(vix_data.columns, pd.MultiIndex):
        vix_data.columns = (
            vix_data.columns.get_level_values(0)
        )

    vix_close = vix_data["Close"]

    current_vix = float(vix_close.iloc[-1])

    vix_4w = float(vix_close.iloc[-21])

    vix_change = (
        (current_vix / vix_4w) - 1
    ) * 100

except Exception as e:

    print("VIX ERROR")

    print(e)

    current_vix = 999
    vix_change = 999

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
