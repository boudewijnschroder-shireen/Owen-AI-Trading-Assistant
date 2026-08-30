import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Konfigurasi Halaman Web
st.set_page_config(page_title="Owen AI Trading Assistant", page_icon="📈", layout="wide")

st.title("📈 Owen AI Trading Assistant & Portfolio Tracker")
st.markdown("Sistem analisis teknikal otomatis, manajemen risiko pemula, dan pelacakan portofolio real-time.")

# Sidebar untuk Pengaturan Pengguna
st.sidebar.header("⚙️ Pengaturan Risiko")
modal_awal = st.sidebar.number_input("Modal Portofolio (Rp)", value=200000, step=50000)
risiko_persen = st.sidebar.slider("Batas Risiko per Transaksi (%)", min_value=0.5, max_value=5.0, value=1.0, step=0.5)

# Daftar Watchlist Saham Indonesia
watchlist = ["BBCA.JK", "BBRI.JK", "ASII.JK", "TLKM.JK"]

st.markdown("---")
st.subheader("🔍 Pindai Sinyal Pasar & Manajemen Risiko")

if st.button("Jalankan Pemindaian Pasar"):
    for ticker in watchlist:
        with st.container():
            st.markdown(f"### Analisis Emiten: `{ticker}`")
            try:
                saham = yf.Ticker(ticker)
                df = saham.history(period="6mo")
                
                if df.empty or len(df) < 50:
                    st.warning(f"Data historis untuk {ticker} tidak mencukupi.")
                    continue

                # Indikator Teknikal
                df['SMA_20'] = df['Close'].rolling(window=20).mean()
                df['SMA_50'] = df['Close'].rolling(window=50).mean()

                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                df['RSI'] = 100 - (100 / (1 + rs))

                terbaru = df.iloc[-1]
                harga_sekarang = terbaru['Close']
                sma_20 = terbaru['SMA_20']
                sma_50 = terbaru['SMA_50']
                rsi = terbaru['RSI']

                # Kolom Informasi Metrik
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Harga Terakhir", f"Rp {harga_sekarang:,.2f}")
                col2.metric("SMA 20", f"Rp {sma_20:,.2f}")
                col3.metric("SMA 50", f"Rp {sma_50:,.2f}")
                col4.metric("RSI (14)", f"{rsi:.2f}")

                # Logika Sinyal
                if sma_20 > sma_50 and rsi < 40:
                    st.success("🟢 **KEPUTUSAN: BELI (BUY)** - Tren utama bullish dan harga dalam zona diskon (Oversold).")
                    
                    # Manajemen Risiko
                    maks_risiko_rp = modal_awal * (risiko_persen / 100)
                    stop_loss_harga = harga_sekarang * 0.95
                    risiko_per_lembar = harga_sekarang - stop_loss_harga
                    
                    if risiko_per_lembar > 0:
                        jumlah_saham = int(maks_risiko_rp / risiko_per_lembar)
                        total_investasi = jumlah_saham * harga_sekarang

                        st.info(f"""
                        **Rencana Manajemen Risiko (PRO):**
                        * **Batas Risiko:** {risiko_persen}% (Rp {maks_risiko_rp:,.2f})
                        * **Harga Stop-Loss:** Rp {stop_loss_harga:,.2f} (-5%)
                        * **Saran Alokasi Pembelian:** **{jumlah_saham:,} lembar** (Total Dana: Rp {total_investasi:,.2f})
                        """)
                elif sma_20 < sma_50 or rsi > 70:
                    st.error("🔴 **KEPUTUSAN: JUAL (SELL)** - Tren melemah atau aset sudah jenuh beli (Overbought).")
                else:
                    st.warning("🟡 **KEPUTUSAN: TAHAN (HOLD)** - Pasar bergerak konsolidasi.")
                
                st.markdown("---")
            except Exception as e:
                st.error(f"Terjadi kesalahan saat memproses {ticker}: {e}")

# Bagian Pelacakan Portofolio Web
st.subheader("📊 Pelacakan Portofolio Nyata")
st.markdown("Berikut adalah simulasi portofolio yang sedang Anda pantau:")

portofolio_pengguna = [
    {"ticker": "ASII.JK", "jumlah_lembar": 100, "harga_beli": 4750.00},
    {"ticker": "TLKM.JK", "jumlah_lembar": 100, "harga_beli": 2600.00}
]

data_tabel = []
total_nilai_aset = 0
total_modal_awal = 0

for item in portofolio_pengguna:
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

        status_pl = "PROFIT 🟢" if profit_loss >= 0 else "LOSS 🔴"

        data_tabel.append({
            "Emiten": ticker,
            "Jumlah Lembar": jumlah,
            "Harga Beli": f"Rp {harga_beli:,.2f}",
            "Harga Sekarang": f"Rp {harga_sekarang:,.2f}",
            "Total Nilai": f"Rp {nilai_sekarang:,.2f}",
            "P/L (Rp)": f"Rp {profit_loss:,.2f}",
            "P/L (%)": f"{profit_loss_persen:.2f}%",
            "Status": status_pl
        })
    except Exception as e:
        st.error(f"Gagal memuat portofolio {ticker}: {e}")

if data_tabel:
    df_portofolio = pd.DataFrame(data_tabel)
    st.dataframe(df_portofolio, use_container_width=True)

    total_pl_portofolio = total_nilai_aset - total_modal_awal
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Total Modal Awal", f"Rp {total_modal_awal:,.2f}")
    col_b.metric("Total Nilai Aset", f"Rp {total_nilai_aset:,.2f}")
    col_c.metric("Total Profit / Loss", f"Rp {total_pl_portofolio:,.2f}")