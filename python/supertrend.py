import pandas as pd


def calculate_supertrend(
    df,
    period=10,
    multiplier=3
):

    high = df['High']
    low = df['Low']
    close = df['Close']

    # -----------------------------------
    # TRUE RANGE
    # -----------------------------------

    tr1 = high - low

    tr2 = abs(
        high - close.shift(1)
    )

    tr3 = abs(
        low - close.shift(1)
    )

    tr = pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)

    # -----------------------------------
    # ATR
    # -----------------------------------

    atr = tr.rolling(period).mean()

    # -----------------------------------
    # BASIC BANDS
    # -----------------------------------

    hl2 = (high + low) / 2

    upperband = hl2 + (
        multiplier * atr
    )

    lowerband = hl2 - (
        multiplier * atr
    )

    # -----------------------------------
    # FINAL BANDS
    # -----------------------------------

    final_upperband = upperband.copy()

    final_lowerband = lowerband.copy()

    for i in range(1, len(df)):

        if (
            upperband.iloc[i]
            < final_upperband.iloc[i - 1]
            or close.iloc[i - 1]
            > final_upperband.iloc[i - 1]
        ):

            final_upperband.iloc[i] = (
                upperband.iloc[i]
            )

        else:

            final_upperband.iloc[i] = (
                final_upperband.iloc[i - 1]
            )

        if (
            lowerband.iloc[i]
            > final_lowerband.iloc[i - 1]
            or close.iloc[i - 1]
            < final_lowerband.iloc[i - 1]
        ):

            final_lowerband.iloc[i] = (
                lowerband.iloc[i]
            )

        else:

            final_lowerband.iloc[i] = (
                final_lowerband.iloc[i - 1]
            )

    # -----------------------------------
    # SUPERTREND
    # -----------------------------------

    supertrend = pd.Series(
        index=df.index,
        dtype='float64'
    )

    for i in range(period, len(df)):

        if (
            close.iloc[i]
            <= final_upperband.iloc[i]
        ):

            supertrend.iloc[i] = (
                final_upperband.iloc[i]
            )

        else:

            supertrend.iloc[i] = (
                final_lowerband.iloc[i]
            )

    return supertrend
