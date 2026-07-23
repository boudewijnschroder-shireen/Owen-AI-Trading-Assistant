from market.stock import get_stock_data
from indicators.trend import get_trend

print("=" * 55)
print("         OWEN AI TRADING ASSISTANT")
print("               Version 0.5")
print("=" * 55)

ticker = input("Masukkan kode saham Amerika (contoh: AAPL, NVDA, TSLA): ").strip().upper()

try:
    data = get_stock_data(ticker)
    trend = get_trend(ticker)

    print()
    print(f"Ticker : {data['ticker']}")
    print(f"Harga  : ${data['price']:.2f}")
    print(f"Open   : ${data['open']:.2f}")
    print(f"High   : ${data['high']:.2f}")
    print(f"Low    : ${data['low']:.2f}")
    print(f"Volume : {data['volume']:,}")
    print(f"Trend  : {trend}")

except Exception as e:
    print()
    print("❌ Terjadi kesalahan.")
    print(e)