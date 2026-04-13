import streamlit as st
import yfinance as yf
import pandas as pd
import sqlite3
from streamlit_autorefresh import st_autorefresh

# ---------------- AUTO REFRESH ----------------
st_autorefresh(interval=15000, key="refresh")

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

# ---------------- SIMPLE ANALYSIS ----------------
def analyze_stock(ticker):
    try:
        data = yf.download(ticker, period="3mo", progress=False)

        if data.empty:
            return None

        latest = data.iloc[-1]

        price = float(latest["Close"])

        ma50 = data["Close"].rolling(50).mean().iloc[-1]
        ma200 = data["Close"].rolling(200).mean().iloc[-1]

        score = 0
        reasons = []

        # Trend
        if price > ma200:
            score += 3
            reasons.append("Uptrend")
        if price > ma50:
            score += 2
            reasons.append("Above MA50")

        # Momentum
        if data["Close"].iloc[-1] > data["Close"].iloc[-5]:
            score += 2
            reasons.append("Positive momentum")

        # Simple confidence
        confidence = min(100, score * 10)

        target = round(price * 1.05, 2)
        stop = round(price * 0.95, 2)

        # Suggestion
        if score >= 5:
            suggestion = "BUY"
        elif score >= 3:
            suggestion = "HOLD"
        else:
            suggestion = "AVOID"

        return price, target, stop, suggestion, ", ".join(reasons), confidence

    except:
        return None

# ---------------- TOP STOCK SCANNER ----------------
st.subheader("🚀 Top Stocks (Auto Ranked)")

stock_list = [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
    "LT.NS","SBIN.NS","AXISBANK.NS","WIPRO.NS","BHARTIARTL.NS",
    "ASIANPAINT.NS","MARUTI.NS","HCLTECH.NS","SUNPHARMA.NS","ITC.NS"
]

if st.button("🔍 Scan Market"):
    results = []

    for stock in stock_list:
        result = analyze_stock(stock)

        if result:
            price, target, stop, suggestion, reason, confidence = result

            results.append({
                "Stock": stock,
                "Buy Price": price,
                "Target": target,
                "Stop Loss": stop,
                "Confidence %": confidence,
                "Suggestion": suggestion,
                "Reason": reason
            })

    if len(results) > 0:
        df = pd.DataFrame(results).sort_values(by="Confidence %", ascending=False)

        # Show TOP 10 always
        st.dataframe(df.head(10), use_container_width=True)

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
        current, target, stop, suggestion, reason, confidence = result
        pnl = round(((current - buy_price) / buy_price) * 100, 2)

        rows.append({
            "Stock": ticker,
            "Buy Price": buy_price,
            "Current Price": current,
            "P/L %": pnl,
            "Target": target,
            "Stop Loss": stop,
            "Confidence %": confidence,
            "Suggestion": suggestion,
            "Reason": reason
        })

df = pd.DataFrame(rows)

if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("No stocks added yet.")
