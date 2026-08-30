import yfinance as yf


def get_trend(ticker):
    stock = yf.Ticker(ticker)

    history = stock.history(period="3mo")

    ma20 = history["Close"].rolling(20).mean().iloc[-1]
    ma50 = history["Close"].rolling(50).mean().iloc[-1]

    if ma20 > ma50:
        return "📈 Bullish"

    elif ma20 < ma50:
        return "📉 Bearish"

    else:
        return "➖ Sideways"