import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")
st.title("🚀 Top Short-Term Stock Picks (Auto Updated)")

st.write(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ---------------- STOCK LIST ----------------
stock_list = [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
    "LT.NS","SBIN.NS","AXISBANK.NS","WIPRO.NS","BHARTIARTL.NS",
    "ASIANPAINT.NS","MARUTI.NS","HCLTECH.NS","SUNPHARMA.NS","ITC.NS",
    "KOTAKBANK.NS","ULTRACEMCO.NS","TITAN.NS","BAJFINANCE.NS","NESTLEIND.NS",
    "POWERGRID.NS","NTPC.NS","ONGC.NS","ADANIENT.NS","ADANIPORTS.NS",
    "JSWSTEEL.NS","TATASTEEL.NS","HINDALCO.NS","COALINDIA.NS","DRREDDY.NS",
    "CIPLA.NS","DIVISLAB.NS","EICHERMOT.NS","HEROMOTOCO.NS","BAJAJ-AUTO.NS",
    "GRASIM.NS","TECHM.NS","UPL.NS","BRITANNIA.NS","HAVELLS.NS",
    "DABUR.NS","GODREJCP.NS","PIDILITIND.NS","SIEMENS.NS","ABB.NS",
    "BOSCHLTD.NS","MCDOWELL-N.NS","COLPAL.NS","VEDL.NS","BANKBARODA.NS"
]

# ---------------- ANALYSIS ----------------
def analyze_stock(ticker):
    try:
        data = yf.download(ticker, period="3mo", progress=False)

        if data.empty:
            return None

        price = data["Close"].iloc[-1]
        ma20 = data["Close"].rolling(20).mean().iloc[-1]
        ma50 = data["Close"].rolling(50).mean().iloc[-1]

        score = 0
        reasons = []

        # Trend
        if price > ma50:
            score += 3
            reasons.append("Uptrend")

        # Short-term momentum
        if price > ma20:
            score += 2
            reasons.append("Above MA20")

        if price > data["Close"].iloc[-5]:
            score += 2
            reasons.append("Momentum")

        # Breakout
        recent_high = data["High"].rolling(20).max().iloc[-1]
        if price >= recent_high * 0.98:
            score += 3
            reasons.append("Breakout")

        confidence = min(100, score * 10)

        # Buy zone (slightly below current price)
        buy_low = round(price * 0.99, 2)
        buy_high = round(price * 1.01, 2)

        target = round(price * 1.05, 2)
        stop = round(price * 0.95, 2)

        return {
            "Stock": ticker,
            "Buy Zone": f"{buy_low} - {buy_high}",
            "Current Price": round(price, 2),
            "Target": target,
            "Stop Loss": stop,
            "Confidence %": confidence,
            "Strength": "🔥" * (confidence // 20 if confidence >= 20 else 1),
            "Reason": ", ".join(reasons)
        }

    except:
        return None

# ---------------- MAIN ----------------
st.subheader("📊 Top 50 Short-Term Opportunities")

results = []

with st.spinner("Analyzing market..."):
    for stock in stock_list:
        res = analyze_stock(stock)
        if res:
            results.append(res)

if results:
    df = pd.DataFrame(results)

    # Sort by confidence
    df = df.sort_values(by="Confidence %", ascending=False)

    # Show top 50
    st.dataframe(df.head(50), use_container_width=True)

    st.success("Showing best available short-term opportunities (ranked)")
else:
    st.error("Error fetching data. Please refresh.")
