import streamlit as st
import yfinance as yf
import requests
import pandas as pd

# Konfigurasi Halaman Streamlit
st.set_page_config(page_title="Owen AI Trading Assistant", layout="wide")

st.title("🤖 Owen AI Trading Assistant - Crypto Edition")
st.markdown("Sistem pemantau pasar kripto cerdas dengan integrasi sinyal Telegram & manajemen risiko 5%.")

# --- SIDEBAR: KONTROL BOT & PARAMETER ---
st.sidebar.header("⚙️ Pengaturan Bot & Telegram")
telegram_token = st.sidebar.text_input("Telegram Bot Token", type="password")
chat_id = st.sidebar.text_input("Telegram Chat ID")

st.sidebar.header("📊 Parameter Trading & Batasan")
crypto_symbol = st.sidebar.selectbox("Pilih Aset Kripto", ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"])
target_pct = st.sidebar.slider("Target Profit & Stop Loss (%)", min_value=1.0, max_value=10.0, value=5.0, step=0.5)

# Fungsi untuk mengirim pesan Telegram
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

# --- UTAMA: ANALISIS & SINYAL KRIPTO ---
st.subheader(f"Monitoring Real-Time: {crypto_symbol}")

# Tombol Analisis Otomatis
if st.button("🔍 Jalankan Pemindaian & Analisis AI"):
    with st.spinner("Memindai pergerakan pasar kripto dan indikator..."):
        # Ambil data historis
        data = yf.download(crypto_symbol, period="5d", interval="1h")
        
        if not data.empty:
            current_price = float(data['Close'].iloc[-1].item())
            prev_price = float(data['Close'].iloc[-2].item())
            price_change = ((current_price - prev_price) / prev_price) * 100

            # Hitung indikator sederhana (Moving Average 20 & 50 untuk deteksi tren)
            data['MA20'] = data['Close'].rolling(window=20).mean()
            data['MA50'] = data['Close'].rolling(window=50).mean()
            
            ma20_val = float(data['MA20'].iloc[-1].item())
            ma50_val = float(data['MA50'].iloc[-1].item())

            col1, col2, col3 = st.columns(3)
            col1.metric("Harga Terkini", f"${current_price:,.2f}", f"{price_change:.2f}%")
            col2.metric("Target Profit (+%)", f"+{target_pct}%")
            col3.metric("Batas Risiko (-%)", f"-{target_pct}%")

            st.line_chart(data[['Close', 'MA20', 'MA50']])

            # --- LOGIKA KEPUTUSAN AI & BATASAN 5% ---
            st.markdown("### 🤖 Hasil Analisis AI & Sinyal Eksekusi")
            
            # Simulasi Evaluasi Berdasarkan Tren dan Batasan
            if current_price > ma20_val and price_change > 0:
                signal_type = "🟢 SINYAL BELI (BUY)"
                signal_desc = f"Harga berada di atas rata-rata tren pendek dengan momentum positif. Potensi kenaikan menuju target profit **+{target_pct}%**."
            elif current_price < ma20_val and price_change < 0:
                signal_type = "🔴 SINYAL JUAL / HATI-HATI (SELL / CUT LOSS)"
                signal_desc = f"Harga menembus di bawah rata-rata tren. Waspadai penurunan yang mendekati batas risiko **-{target_pct}%**."
            else:
                signal_type = "🟡 BERTAHAN (HOLD / WAIT)"
                signal_desc = "Pasar bergerak mendatar (*konsolidasi*). Tunggu momentum breakout atau koreksi sehat."

            st.markdown(f"**Status Sinyal:** {signal_type}")
            st.write(signal_desc)

            # Tombol Kirim Notifikasi Live ke Telegram
            if st.button("📤 Kirim Sinyal Ini ke Telegram Sekarang"):
                if telegram_token and chat_id:
                    telegram_message = (
                        f"🤖 *Owen AI Trading Alert*\n\n"
                        f"📌 **Aset:** {crypto_symbol}\n"
                        f"💰 **Harga Saat Ini:** ${current_price:,.2f} ({price_change:.2f}%)\n"
                        f"📊 **Sinyal:** {signal_type}\n"
                        f"⚙️ **Target / Batasan:** {target_pct}%\n\n"
                        f"_{signal_desc}_"
                    )
                    if send_telegram_alert(telegram_token, chat_id, telegram_message):
                        st.success("Pemberitahuan sinyal berhasil dikirim ke Telegram Anda!")
                    else:
                        st.error("Gagal mengirim Telegram. Periksa kembali Token Bot dan Chat ID Anda di sidebar.")
                else:
                    st.warning("Mohon isi Telegram Bot Token dan Chat ID terlebih dahulu di panel sebelah kiri.")
        else:
            st.error("Gagal memuat data pasar. Silakan coba beberapa saat lagi.")