import yfinance as yf


def get_stock_data(ticker):
    stock = yf.Ticker(ticker)

    info = stock.fast_info

    return {
        "ticker": ticker,
        "price": info["lastPrice"],
        "open": info["open"],
        "high": info["dayHigh"],
        "low": info["dayLow"],
        "volume": info["lastVolume"],
    }