import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ---------------- AUTO REFRESH ----------------
st_autorefresh(interval=300000, key="refresh")  # 5 min

st.set_page_config(layout="wide")
st.title("🚀 Smart Trading Dashboard")

st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ---------------- MARKET OVERVIEW ----------------
st.subheader("📊 Market Overview")

col1, col2, col3 = st.columns(3)

def get_index(symbol):
    try:
        data = yf.download(symbol, period="1d", interval="1m", progress=False)
        price = round(data["Close"].iloc[-1], 2)
        change = round(price - data["Open"].iloc[0], 2)
        return price, change
    except:
        return "-", "-"

nifty, n_change = get_index("^NSEI")
sensex, s_change = get_index("^BSESN")
banknifty, b_change = get_index("^NSEBANK")

col1.metric("NIFTY 50", nifty, n_change)
col2.metric("SENSEX", sensex, s_change)
col3.metric("BANK NIFTY", banknifty, b_change)

# Market Mood
if isinstance(n_change, float):
    if n_change > 50:
        mood = "📈 Bullish"
    elif n_change < -50:
        mood = "📉 Bearish"
    else:
        mood = "⚖️ Neutral"
else:
    mood = "Loading..."

st.info(f"Market Mood: {mood}")

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

        if price > ma50:
            score += 3
            reasons.append("Uptrend")

        if price > ma20:
            score += 2
            reasons.append("Above MA20")

        if price > data["Close"].iloc[-5]:
            score += 2
            reasons.append("Momentum")

        recent_high = data["High"].rolling(20).max().iloc[-1]
        if price >= recent_high * 0.98:
            score += 3
            reasons.append("Breakout")

        confidence = min(100, score * 10)

        buy_low = round(price * 0.99, 2)
        buy_high = round(price * 1.01, 2)

        target = round(price * 1.05, 2)
        stop = round(price * 0.95, 2)

        # Risk Level
        if confidence >= 70:
            risk = "Low"
        elif confidence >= 50:
            risk = "Medium"
        else:
            risk = "High"

        return {
            "Stock": ticker,
            "Buy Zone": f"{buy_low}-{buy_high}",
            "Price": round(price, 2),
            "Target": target,
            "Stop": stop,
            "Confidence": confidence,
            "Risk": risk,
            "Strength": "🔥" * max(1, confidence // 20),
            "Reason": ", ".join(reasons)
        }

    except:
        return None

# ---------------- CONTROLS ----------------
st.subheader("📊 Top Opportunities")

show_top = st.radio("Select View", ["Top 10", "Top 50"])

if st.button("🔍 Refresh Scan"):
    st.rerun()

# ---------------- SCAN ----------------
results = []

with st.spinner("Analyzing market..."):
    for stock in stock_list:
        res = analyze_stock(stock)
        if res:
            results.append(res)

if results:
    df = pd.DataFrame(results).sort_values(by="Confidence", ascending=False)

    if show_top == "Top 10":
        df = df.head(10)
    else:
        df = df.head(50)

    st.dataframe(df, use_container_width=True)
else:
    st.error("Error loading data. Try refreshing.")
