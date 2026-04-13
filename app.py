import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")
st.title("🚀 Smart Trading Dashboard")

st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ---------------- STOCK LIST (REDUCED FOR STABILITY) ----------------
stock_list = [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
    "LT.NS","SBIN.NS","AXISBANK.NS","BHARTIARTL.NS","ITC.NS",
    "KOTAKBANK.NS","TITAN.NS","BAJFINANCE.NS","ADANIPORTS.NS",
    "JSWSTEEL.NS","TATASTEEL.NS","HINDALCO.NS","DRREDDY.NS",
    "CIPLA.NS","ULTRACEMCO.NS"
]

# ---------------- SAFE FETCH ----------------
def get_data(ticker):
    try:
        data = yf.download(ticker, period="3mo", progress=False)
        if data.empty:
            return None
        return data
    except:
        return None

# ---------------- ANALYSIS ----------------
def analyze_stock(ticker):
    data = get_data(ticker)
    if data is None:
        return None

    try:
        price = float(data["Close"].iloc[-1])
        ma20 = data["Close"].rolling(20).mean().iloc[-1]
        ma50 = data["Close"].rolling(50).mean().iloc[-1]

        score = 0

        if price > ma50:
            score += 3
        if price > ma20:
            score += 2
        if price > data["Close"].iloc[-5]:
            score += 2

        recent_high = data["High"].rolling(20).max().iloc[-1]
        if price >= recent_high * 0.98:
            score += 3

        confidence = min(100, score * 10)

        return {
            "Stock": ticker,
            "Price": round(price, 2),
            "Target": round(price * 1.05, 2),
            "Stop": round(price * 0.95, 2),
            "Confidence": confidence
        }

    except:
        return None

# ---------------- SCAN ----------------
st.subheader("📊 Top Opportunities")

view = st.radio("Select View", ["Top 10", "Top 20"])

if st.button("🔍 Scan Market"):
    results = []

    with st.spinner("Scanning..."):
        for stock in stock_list:
            res = analyze_stock(stock)
            if res:
                results.append(res)

    if results:
        df = pd.DataFrame(results).sort_values(by="Confidence", ascending=False)

        if view == "Top 10":
            df = df.head(10)
        else:
            df = df.head(20)

        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Data fetch issue. Try again in a few seconds.")
