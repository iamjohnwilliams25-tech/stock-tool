import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import sqlite3
import time

st.set_page_config(layout="wide")

st.title("📊 Smart Trading Tool")

# AUTO REFRESH
time.sleep(5)
st.experimental_rerun()

# DB
conn = sqlite3.connect("portfolio.db", check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS portfolio (
    ticker TEXT,
    buy_price REAL
)
''')
conn.commit()

# ANALYSIS
def analyze_stock(ticker):
    data = yf.download(ticker, period="3mo")

    if data.empty:
        return None

    data["RSI"] = ta.momentum.RSIIndicator(data["Close"]).rsi()
    data["MA50"] = data["Close"].rolling(50).mean()
    data["MA200"] = data["Close"].rolling(200).mean()

    latest = data.iloc[-1]

    score = 0
    reasons = []

    if latest["Close"] > latest["MA50"]:
        score += 2
        reasons.append("Above MA50")

    if latest["Close"] > latest["MA200"]:
        score += 3
        reasons.append("Above MA200")

    if 45 < latest["RSI"] < 65:
        score += 2
        reasons.append("Healthy RSI")

    price = float(latest["Close"])

    target = round(price * 1.04, 2)
    stop = round(price * 0.97, 2)

    if score >= 6:
        suggestion = "BUY MORE"
    elif score >= 4:
        suggestion = "HOLD"
    else:
        suggestion = "SELL"

    return price, target, stop, suggestion, ", ".join(reasons)

# ADD STOCK
st.subheader("➕ Add Stock")

ticker = st.text_input("Stock (e.g. RELIANCE.NS)")
buy_price = st.number_input("Buy Price")

if st.button("Save"):
    c.execute("INSERT INTO portfolio VALUES (?, ?)", (ticker, buy_price))
    conn.commit()
    st.success("Saved!")

# DELETE
st.subheader("🗑️ Delete Stock")

stocks = c.execute("SELECT rowid, * FROM portfolio").fetchall()

for row in stocks:
    col1, col2 = st.columns(2)
    col1.write(f"{row[1]} @ {row[2]}")
    if col2.button("Delete", key=row[0]):
        c.execute("DELETE FROM portfolio WHERE rowid=?", (row[0],))
        conn.commit()
        st.experimental_rerun()

# ANALYZE
st.subheader("📊 Portfolio Analysis")

rows = []

for row in stocks:
    result = analyze_stock(row[1])

    if result:
        current, target, stop, suggestion, reason = result
        pnl = round(((current - row[2]) / row[2]) * 100, 2)

        rows.append({
            "Stock": row[1],
            "Buy": row[2],
            "Current": current,
            "P/L %": pnl,
            "Target": target,
            "Stop": stop,
            "Suggestion": suggestion,
            "Reason": reason
        })

df = pd.DataFrame(rows)

st.dataframe(df)
