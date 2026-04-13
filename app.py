import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import sqlite3
from streamlit_autorefresh import st_autorefresh

# AUTO REFRESH
st_autorefresh(interval=15000, key="refresh")

st.set_page_config(layout="wide")
st.title("📊 Smart Trading Tool (Pro Version)")

# DATABASE
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

        price = float(latest["Close"])

        # TREND
        if latest["Close"] > latest["MA200"]:
            score += 3
            reasons.append("Strong uptrend (above MA200)")
        if latest["Close"] > latest["MA50"]:
            score += 2
            reasons.append("Short-term bullish (above MA50)")

        # RSI
        if 45 < latest["RSI"] < 65:
            score += 2
            reasons.append("Healthy RSI")
        elif latest["RSI"] < 35:
            score += 1
            reasons.append("Near oversold (bounce possible)")
        elif latest["RSI"] > 70:
            score -= 2
            reasons.append("Overbought")

        # BREAKOUT (last 20 days high)
        recent_high = data["High"].rolling(20).max().iloc[-1]
        if price >= recent_high * 0.98:
            score += 2
            reasons.append("Near breakout zone")

        # VOLUME
        if data["Volume"].iloc[-1] > data["Volume"].rolling(10).mean().iloc[-1]:
            score += 1
            reasons.append("Volume support")

        # CONFIDENCE %
        confidence = min(100, score * 10)

        # TARGET & STOP
        target = round(price * 1.05, 2)
        stop = round(price * 0.96, 2)

        # SUGGESTION
        if score >= 7:
            suggestion = "STRONG BUY"
        elif score >= 5:
            suggestion = "BUY"
        elif score >= 3:
            suggestion = "HOLD"
        else:
            suggestion = "AVOID"

        return price, target, stop, suggestion, ", ".join(reasons), score, confidence

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
            price, target, stop, suggestion, reason, score, confidence = result

            if score >= 5:
                scan_results.append({
                    "Stock": stock,
                    "Buy Price": price,
                    "Target": target,
                    "Stop Loss": stop,
                    "Confidence %": confidence,
                    "Suggestion": suggestion,
                    "Reason": reason
                })

    if len(scan_results) > 0:
        df_scan = pd.DataFrame(scan_results).sort_values(by="Confidence %", ascending=False)
        st.dataframe(df_scan, use_container_width=True)
    else:
        st.warning("No strong stocks found right now.")

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
        current, target, stop, suggestion, reason, score, confidence = result
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
