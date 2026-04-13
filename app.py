import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import sqlite3
from streamlit_autorefresh import st_autorefresh

# AUTO REFRESH
st_autorefresh(interval=10000, key="refresh")

st.set_page_config(layout="wide")
st.title("📊 Smart Trading Tool")

# ---------------- DATABASE ----------------
conn = sqlite3.connect("portfolio.db", check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS portfolio (
    ticker TEXT,
    buy_price REAL
)
''')
conn.commit()

# ---------------- ANALYSIS ----------------
def analyze_stock(ticker):
    try:
        data = yf.download(ticker, period="3mo", progress=False)

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
            suggestion = "BUY"
        elif score >= 4:
            suggestion = "HOLD"
        else:
            suggestion = "AVOID"

        return price, target, stop, suggestion, ", ".join(reasons), score

    except:
        return None

# ---------------- TOP STOCK SCANNER ----------------
st.subheader("🚀 Top Buy Opportunities")

stock_list = [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
    "LT.NS","SBIN.NS","AXISBANK.NS","WIPRO.NS","BHARTIARTL.NS",
    "ASIANPAINT.NS","MARUTI.NS","HCLTECH.NS","SUNPHARMA.NS","ITC.NS"
]

scan_results = []

if st.button("🔍 Scan Market"):
    for stock in stock_list:
        result = analyze_stock(stock)

        if result:
            price, target, stop, suggestion, reason, score = result

            if score >= 5:  # only strong ones
                scan_results.append({
                    "Stock": stock,
                    "Buy Price": price,
                    "Target": target,
                    "Stop Loss": stop,
                    "Suggestion": suggestion,
                    "Score": score,
                    "Reason": reason
                })

    df_scan = pd.DataFrame(scan_results).sort_values(by="Score", ascending=False)

    st.dataframe(df_scan, use_container_width=True)

# ---------------- ADD STOCK ----------------
st.subheader("➕ Add Stock")

ticker = st.text_input("Stock (example: RELIANCE.NS)")
buy_price = st.number_input("Buy Price")

if st.button("Save Stock"):
    if ticker != "":
        c.execute("INSERT INTO portfolio VALUES (?, ?)", (ticker.upper(), buy_price))
        conn.commit()
        st.success("Stock Saved!")

# ---------------- DELETE STOCK ----------------
st.subheader("🗑️ Delete Stock")

stocks = c.execute("SELECT rowid, * FROM portfolio").fetchall()

for row in stocks:
    col1, col2 = st.columns(2)
    col1.write(f"{row[1]} @ {row[2]}")

    if col2.button("Delete", key=row[0]):
        c.execute("DELETE FROM portfolio WHERE rowid=?", (row[0],))
        conn.commit()
        st.experimental_rerun()

# ---------------- PORTFOLIO ----------------
st.subheader("📊 Portfolio Analysis")

rows = []

for row in stocks:
    ticker = row[1]
    buy_price = row[2]

    result = analyze_stock(ticker)

    if result:
        current, target, stop, suggestion, reason, score = result
        pnl = round(((current - buy_price) / buy_price) * 100, 2)

        rows.append({
            "Stock": ticker,
            "Buy Price": buy_price,
            "Current Price": current,
            "P/L %": pnl,
            "Target": target,
            "Stop Loss": stop,
            "Suggestion": suggestion,
            "Reason": reason
        })

df = pd.DataFrame(rows)

if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("No stocks added yet.")
