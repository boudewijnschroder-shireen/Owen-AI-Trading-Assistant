import yfinance as yf
import pandas as pd
import numpy as np

def analisis_dan_manajemen_risiko(ticker_symbol, modal_total=200000, risiko_persen=1.0):
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

        # 3. Kalkulasi Manajemen Risiko & Position Sizing
        if is_buy_signal:
            maks_risiko_rp = modal_total * (risiko_persen / 100)
            stop_loss_harga = harga_sekarang * 0.95
            risiko_per_lembar = harga_sekarang - stop_loss_harga

            if risiko_per_lembar > 0:
                jumlah_saham = int(maks_risiko_rp / risiko_per_lembar)
                total_investasi = jumlah_saham * harga_sekarang

                print(f"----------------------------------------")
                print(f" [ MANAJEMEN RISIKO (PEMULA) ]")
                print(f" Modal Portofolio : Rp {modal_total:,.2f}")
                print(f" Batas Risiko     : {risiko_persen}% (Rp {maks_risiko_rp:,.2f})")
                print(f" Harga Stop-Loss  : Rp {stop_loss_harga:,.2f} (-5%)")
                print(f" Alokasi Pembelian: {jumlah_saham:,} lembar")
                print(f" Total Dana Masuk : Rp {total_investasi:,.2f}")
                print(f"----------------------------------------")

        print(f"----------------------------------------\n")

    except Exception as e:
        print(f"[ERROR] Terjadi kesalahan saat memproses {ticker_symbol}: {e}")


def pantau_portofolio(portofolio_saya):
    print("=" * 42)
    print("      PANTAUAN PORTOFOLIO SAYA")
    print("=" * 42)
    
    total_nilai_aset = 0
    total_modal_awal = 0

    for item in portofolio_saya:
        ticker = item['ticker']
        jumlah = item['jumlah_lembar']
        harga_beli = item['harga_beli']
        
        try:
            saham = yf.Ticker(ticker)
            harga_sekarang = saham.history(period="1d")['Close'].iloc[-1]
            
            nilai_sekarang = jumlah * harga_sekarang
            modal_awal_item = jumlah * harga_beli
            profit_loss = nilai_sekarang - modal_awal_item
            profit_loss_persen = (profit_loss / modal_awal_item) * 100 if modal_awal_item > 0 else 0
            
            total_nilai_aset += nilai_sekarang
            total_modal_awal += modal_awal_item

            status_pl = f"PROFIT 🟢" if profit_loss >= 0 else f"LOSS 🔴"

            print(f" Emiten        : {ticker}")
            print(f" Jumlah Lembar : {jumlah:,}")
            print(f" Harga Beli    : Rp {harga_beli:,.2f}")
            print(f" Harga Sekarang: Rp {harga_sekarang:,.2f}")
            print(f" Nilai Total   : Rp {nilai_sekarang:,.2f}")
            print(f" P/L           : Rp {profit_loss:,.2f} ({profit_loss_persen:.2f}%) [{status_pl}]")
            print("-" * 42)

        except Exception as e:
            print(f"[ERROR] Gagal memuat data portofolio untuk {ticker}: {e}")

    total_pl_portofolio = total_nilai_aset - total_modal_awal
    print(f" Total Modal Awal : Rp {total_modal_awal:,.2f}")
    print(f" Total Nilai Aset : Rp {total_nilai_aset:,.2f}")
    print(f" Total Profit/Loss: Rp {total_pl_portofolio:,.2f}")
    print("=" * 42 + "\n")


if __name__ == "__main__":
    MODAL_AWAL = 200000 
    
    # 1. Menjalankan Analisis Watchlist
    watchlist = ["BBCA.JK", "BBRI.JK", "ASII.JK", "TLKM.JK"]
    print("\n--- MENJALANKAN SCANNER & ANALISIS PASAR ---")
    for emiten in watchlist:
        analisis_dan_manajemen_risiko(emiten, modal_total=MODAL_AWAL, risiko_persen=1.0)

    # 2. Simulasi Portofolio Anda (Contoh: Anda mencatat kepemilikan saham di sini)
    # Anda bisa mengubah kode emiten, jumlah lembar, dan harga beli sesuai transaksi nyata Anda nantinya
    portofolio_pengguna = [
        {"ticker": "ASII.JK", "jumlah_lembar": 100, "harga_beli": 4750.00},
        {"ticker": "TLKM.JK", "jumlah_lembar": 100, "harga_beli": 2600.00}
    ]
    
    print("\n--- MENJALANKAN PELACAKAN PORTOFOLIO ---")
    pantau_portofolio(portofolio_pengguna)