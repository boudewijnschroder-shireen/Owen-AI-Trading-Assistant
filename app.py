import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import time

# Konfigurasi Halaman Web
st.set_page_config(page_title="Owen Crypto & Asset AI Assistant", page_icon="⚡", layout="wide")

st.title("⚡ Owen Crypto & Asset AI Trading Assistant")
st.markdown("Sistem analisis teknikal otomatis, manajemen risiko, dan pemantauan live market (Kripto & Saham US) dengan notifikasi Telegram.")

# --- SIDEBAR: PENGATURAN & TELEGRAM ---
st.sidebar.header("⚙️ Pengaturan Telegram Bot")

if 'token_input' not in st.session_state:
    st.session_state.token_input = "8973867458:AAFcsei2M-2ZfmYmSRWEYP3O6mRi3I31piI"
if 'chat_input' not in st.session_state:
    st.session_state.chat_input = "1738067289"

telegram_token = st.sidebar.text_input("Telegram Bot Token", value=st.session_state.token_input, type="password")
chat_id = st.sidebar.text_input("Telegram Chat ID", value=st.session_state.chat_input)

st.session_state.token_input = telegram_token
st.session_state.chat_input = chat_id

def send_telegram_alert(token, chat_id, message):
    if not token or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        return False

if st.sidebar.button("🧪 Tes Kirim Pesan ke Telegram"):
    if not telegram_token or not chat_id:
        st.sidebar.error("Token atau Chat ID masih kosong!")
    else:
        pesan_tes = "Hallo bossku. Pesan uji coba berhasil terkirim!"
        if send_telegram_alert(telegram_token, chat_id, pesan_tes):
            st.sidebar.success("Berhasil terkirim ke Telegram!")
        else:
            st.sidebar.error("Gagal mengirim pesan uji coba.")

st.sidebar.header("⚙️ Pengaturan Risiko & Live")
modal_awal = st.sidebar.number_input("Modal Portofolio ($ USD)", value=10000.0, step=1000.0)
risiko_persen = st.sidebar.slider("Batas Risiko per Transaksi (%)", min_value=0.5, max_value=5.0, value=1.0, step=0.5)

# Pilihan Market di Sidebar
market_pilihan = st.sidebar.selectbox("Pilih Pasar untuk Dipindai", ["Kripto (Crypto)", "Saham Amerika (US Stock)"])

# Fitur Auto-Refresh Live (1 Menit)
live_mode = st.sidebar.checkbox("⚡ Aktifkan Live Auto-Refresh (1 Menit)", value=False)

# Tentukan Watchlist Berdasarkan Pilihan Pasar
if market_pilihan == "Kripto (Crypto)":
    watchlist = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD"]
    label_market = "Crypto"
else:
    watchlist = ["AAPL", "MSFT", "TSLA", "NVDA", "AMZN"]
    label_market = "US Stock"

st.markdown("---")
st.subheader(f"🔍 Pindai Sinyal Pasar {label_market} & Manajemen Risiko")

if st.button("Jalankan Pemindaian Market") or live_mode:
    for ticker in watchlist:
        with st.container():
            st.markdown(f"### Analisis Aset: `{ticker}`")
            try:
                saham = yf.Ticker(ticker)
                df = saham.history(period="6mo")
                
                if df.empty or len(df) < 50:
                    st.warning(f"Data historis untuk {ticker} tidak mencukupi.")
                    continue

                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)

                df['SMA_20'] = df['Close'].rolling(window=20).mean()
                df['SMA_50'] = df['Close'].rolling(window=50).mean()

                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                df['RSI'] = 100 - (100 / (1 + rs))

                terbaru = df.iloc[-1]
                harga_sekarang = float(terbaru['Close'].item() if hasattr(terbaru['Close'], 'item') else terbaru['Close'])
                sma_20 = float(terbaru['SMA_20'].item() if hasattr(terbaru['SMA_20'], 'item') else terbaru['SMA_20'])
                sma_50 = float(terbaru['SMA_50'].item() if hasattr(terbaru['SMA_50'], 'item') else terbaru['SMA_50'])
                rsi = float(terbaru['RSI'].item() if hasattr(terbaru['RSI'], 'item') else terbaru['RSI'])

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Harga Terakhir", f"${harga_sekarang:,.2f}")
                col2.metric("SMA 20", f"${sma_20:,.2f}")
                col3.metric("SMA 50", f"${sma_50:,.2f}")
                col4.metric("RSI (14)", f"{rsi:.2f}")

                keputusan_teks = ""
                if sma_20 > sma_50 and rsi < 40:
                    keputusan_teks = "🟢 KEPUTUSAN: BELI (BUY) - Tren bullish & harga diskon."
                    st.success(keputusan_teks)
                elif sma_20 < sma_50 or rsi > 70:
                    keputusan_teks = "🔴 KEPUTUSAN: JUAL (SELL) - Tren melemah / jenuh beli."
                    st.error(keputusan_teks)
                else:
                    keputusan_teks = "🟡 KEPUTUSAN: TAHAN (HOLD) - Pasar konsolidasi."
                    st.warning(keputusan_teks)
                
                # Kirim otomatis ke Telegram
                pesan_analisis = (
                    f"🚀 *Owen Crypto AI Trading Alert*\n\n"
                    f"📌 *Aset:* `{ticker}`\n"
                    f"💰 *Harga:* ${harga_sekarang:,.2f}\n"
                    f"📊 *RSI:* {rsi:.2f}\n"
                    f"📢 *Status:* {keputusan_teks}"
                )
                if send_telegram_alert(telegram_token, chat_id, pesan_analisis):
                    st.info(f"📤 Sinyal {ticker} terkirim ke Telegram.")

                st.markdown("---")
            except Exception as e:
                st.error(f"Terjadi kesalahan saat memproses {ticker}: {e}")

    # Logika Live Auto-Refresh setiap 60 detik (1 Menit)
    if live_mode:
        st.toast("⏳ Memperbarui data market secara otomatis...", icon="🔄")
        time.sleep(60)
        st.rerun()

# Bagian Pelacakan Portofolio Kripto/Aset
st.subheader("📊 Pelacakan Portofolio Aktif")
portofolio_aset = [
    {"ticker": "BTC-USD", "jumlah_lembar": 0.15, "harga_beli": 62000.00},
    {"ticker": "ETH-USD", "jumlah_lembar": 1.5, "harga_beli": 2900.00},
    {"ticker": "SOL-USD", "jumlah_lembar": 15.0, "harga_beli": 135.00}
]

data_tabel = []
total_nilai_aset = 0
total_modal_awal = 0

for item in portofolio_aset:
    ticker = item['ticker']
    jumlah = item['jumlah_lembar']
    harga_beli = item['harga_beli']
    
    try:
        saham = yf.Ticker(ticker)
        df_hist = saham.history(period="1d")
        if isinstance(df_hist.columns, pd.MultiIndex):
            df_hist.columns = df_hist.columns.get_level_values(0)
            
        harga_sekarang = float(df_hist['Close'].iloc[-1].item() if hasattr(df_hist['Close'].iloc[-1], 'item') else df_hist['Close'].iloc[-1])
        
        nilai_sekarang = jumlah * harga_sekarang
        modal_awal_item = jumlah * harga_beli
        profit_loss = nilai_sekarang - modal_awal_item
        profit_loss_persen = (profit_loss / modal_awal_item) * 100 if modal_awal_item > 0 else 0
        
        total_nilai_aset += nilai_sekarang
        total_modal_awal += modal_awal_item

        status_pl = "PROFIT 🟢" if profit_loss >= 0 else "LOSS 🔴"

        data_tabel.append({
            "Aset": ticker,
            "Jumlah": jumlah,
            "Harga Beli": f"${harga_beli:,.2f}",
            "Harga Sekarang": f"${harga_sekarang:,.2f}",
            "Total Nilai": f"${nilai_sekarang:,.2f}",
            "P/L ($)": f"${profit_loss:,.2f}",
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
    col_a.metric("Total Modal Awal", f"${total_modal_awal:,.2f}")
    col_b.metric("Total Nilai Aset", f"${total_nilai_aset:,.2f}")
    col_c.metric("Total Profit / Loss", f"${total_pl_portofolio:,.2f}")