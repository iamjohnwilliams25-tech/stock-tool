import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide")
st.title("🚀 Strong Buy Stock Scanner")

# ---------------- STOCK LIST ----------------
stock_list = [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
    "LT.NS","SBIN.NS","AXISBANK.NS","WIPRO.NS","BHARTIARTL.NS",
    "ASIANPAINT.NS","MARUTI.NS","HCLTECH.NS","SUNPHARMA.NS","ITC.NS"
]

# ---------------- ANALYSIS ----------------
def analyze_stock(ticker):
    try:
        data = yf.download(ticker, period="3mo", progress=False)

        if data.empty:
            return None

        price = data["Close"].iloc[-1]
        ma50 = data["Close"].rolling(50).mean().iloc[-1]
        ma200 = data["Close"].rolling(200).mean().iloc[-1]

        score = 0
        reasons = []

        # Strong Trend
        if price > ma200:
            score += 3
            reasons.append("Strong uptrend")

        if price > ma50:
            score += 2
            reasons.append("Above MA50")

        # Momentum
        if data["Close"].iloc[-1] > data["Close"].iloc[-5]:
            score += 2
            reasons.append("Positive momentum")

        # Breakout
        recent_high = data["High"].rolling(20).max().iloc[-1]
        if price >= recent_high * 0.98:
            score += 2
            reasons.append("Near breakout")

        # Only return STRONG BUY
        if score >= 7:
            target = round(price * 1.06, 2)
            stop = round(price * 0.95, 2)

            return {
                "Stock": ticker,
                "Buy Price": round(price, 2),
                "Target": target,
                "Stop Loss": stop,
                "Reason": ", ".join(reasons)
            }

        return None

    except:
        return None

# ---------------- UI ----------------
if st.button("🔍 Find Strong Buy Stocks"):
    results = []

    for stock in stock_list:
        res = analyze_stock(stock)
        if res:
            results.append(res)

    if results:
        df = pd.DataFrame(results)
        st.success(f"Found {len(df)} Strong Buy Stocks")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No strong buy stocks found right now. Market may not be favorable.")
