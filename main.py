import yfinance as yf
import pandas as pd
import numpy as np

def analisis_dan_manajemen_risiko(ticker_symbol, modal_total=10000000, risiko_persen=1.0):
    print(f"\n[ANALISIS & MANAJEMEN RISIKO] Memproses {ticker_symbol}...")
    
    try:
        saham = yf.Ticker(ticker_symbol)
        df = saham.history(period="6mo")
        
        if df.empty or len(df) < 50:
            print(f"[PERINGATAN] Data historis untuk {ticker_symbol} tidak mencukupi.")
            return

        # 1. Menghitung Indikator Teknikal (SMA & RSI)
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()

        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # Data Sesi Perdagangan Terkini
        terbaru = df.iloc[-1]
        harga_sekarang = terbaru['Close']
        sma_20 = terbaru['SMA_20']
        sma_50 = terbaru['SMA_50']
        rsi = terbaru['RSI']

        print(f"----------------------------------------")
        print(f" Emiten           : {ticker_symbol}")
        print(f" Harga Terakhir   : Rp {harga_sekarang:,.2f}")
        print(f" SMA 20           : Rp {sma_20:,.2f}")
        print(f" SMA 50           : Rp {sma_50:,.2f}")
        print(f" RSI (14)         : {rsi:.2f}")
        print(f"----------------------------------------")

        # 2. Logika Sinyal Trading
        sinyal = "TAHAN (HOLD) - Pasar bergerak konsolidasi."
        is_buy_signal = False

        if sma_20 > sma_50 and rsi < 40:
            sinyal = "BELI (BUY) - Tren utama bullish dan harga dalam zona diskon (Oversold)."
            is_buy_signal = True
        elif sma_20 < sma_50 or rsi > 70:
            sinyal = "JUAL (SELL) - Tren melemah atau aset sudah jenuh beli (Overbought)."

        print(f" KEPUTUSAN TRADING  : {sinyal}")

        # 3. Kalkulasi Manajemen Risiko & Position Sizing (Hanya dihitung jika sinyal BELI)
        if is_buy_signal:
            # Risiko maksimal yang diizinkan dalam Rupiah (misal 1% dari modal total)
            maks_risiko_rp = modal_total * (risiko_persen / 100)
            
            # Menentukan titik Stop-Loss 5% di bawah harga beli
            stop_loss_harga = harga_sekarang * 0.95
            risiko_per_lembar = harga_sekarang - stop_loss_harga

            # Menghitung jumlah lembar saham yang aman dibeli
            if risiko_per_lembar > 0:
                jumlah_saham = int(maks_risiko_rp / risiko_per_lembar)
                total_investasi = jumlah_saham * harga_sekarang

                print(f"----------------------------------------")
                print(f" [ MANAJEMEN RISIKO (PRO) ]")
                print(f" Modal Portofolio : Rp {modal_total:,.2f}")
                print(f" Batas Risiko     : {risiko_persen}% (Rp {maks_risiko_rp:,.2f})")
                print(f" Harga Stop-Loss  : Rp {stop_loss_harga:,.2f} (-5%)")
                print(f" Alokasi Pembelian: {jumlah_saham:,} lembar")
                print(f" Total Dana Masuk : Rp {total_investasi:,.2f}")
                print(f"----------------------------------------")

        print(f"----------------------------------------\n")

    except Exception as e:
        print(f"[ERROR] Terjadi kesalahan saat memproses {ticker_symbol}: {e}")

if __name__ == "__main__":
    # Simulasikan total modal portofolio Anda (Contoh: Rp 10.000.000)
    MODAL_AWAL = 10000000 
    
    watchlist = ["BBCA.JK", "BBRI.JK", "ASII.JK", "TLKM.JK"]
    
    for emiten in watchlist:
        analisis_dan_manajemen_risiko(emiten, modal_total=MODAL_AWAL, risiko_persen=1.0)