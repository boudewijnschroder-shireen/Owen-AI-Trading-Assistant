import yfinance as yf
import pandas as pd
import numpy as np

def ambil_dan_analisis_saham(ticker_symbol):
    print(f"\n[ANALISIS PROFESIONAL] Mengambil data pasar untuk {ticker_symbol}...")
    
    try:
        saham = yf.Ticker(ticker_symbol)
        df = saham.history(period="6mo")
        
        if df.empty or len(df) < 50:
            print(f"[PERINGATAN] Data historis untuk {ticker_symbol} tidak mencukupi.")
            return

        # 1. Menghitung Moving Average (SMA 20 dan SMA 50) untuk Tren
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()

        # 2. Menghitung Relative Strength Index (RSI 14) untuk Momentum
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # Mengambil data baris terakhir (sesi perdagangan terkini)
        terbaru = df.iloc[-1]
        harga_sekarang = terbaru['Close']
        sma_20 = terbaru['SMA_20']
        sma_50 = terbaru['SMA_50']
        rsi = terbaru['RSI']

        print(f"----------------------------------------")
        print(f" Emiten          : {ticker_symbol}")
        print(f" Harga Terakhir  : {harga_sekarang:,.2f}")
        print(f" SMA 20          : {sma_20:,.2f}")
        print(f" SMA 50          : {sma_50:,.2f}")
        print(f" RSI (14)        : {rsi:.2f}")
        print(f"----------------------------------------")

        # Logika Pengambilan Keputusan Profesional (Rule-Based Trading)
        sinyal = "TAHAN (HOLD) - Pasar bergerak konsolidasi."
        
        if sma_20 > sma_50 and rsi < 40:
            sinyal = "BELI (BUY) - Tren utama bullish dan harga dalam zona diskon (Oversold)."
        elif sma_20 < sma_50 or rsi > 70:
            sinyal = "JUAL (SELL) - Tren melemah atau aset sudah jenuh beli (Overbought)."

        print(f" KEPUTUSAN TRADING : {sinyal}")
        print(f"----------------------------------------\n")

    except Exception as e:
        print(f"[ERROR] Terjadi kesalahan saat memproses {ticker_symbol}: {e}")

if __name__ == "__main__":
    # Daftar pantauan awal (Watchlist) bursa lokal Indonesia
    watchlist = ["BBCA.JK", "BBRI.JK", "ASII.JK", "TLKM.JK"]
    
    for emiten in watchlist:
        ambil_dan_analisis_saham(emiten)