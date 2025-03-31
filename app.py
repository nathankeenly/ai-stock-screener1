import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st

# --- RSI Function ---
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# --- Screener Function ---
def screener(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    data = ticker.history(period="6mo")
    info = ticker.info

    # Technical Indicators
    data["EMA_20"] = data["Close"].ewm(span=20).mean()
    data["SMA_50"] = data["Close"].rolling(window=50).mean()
    data["RSI"] = compute_rsi(data["Close"])
    data["Volume_Trend"] = data["Volume"].rolling(window=10).mean()

    # Fundamental Data (static for display)
    pe_ratio = info.get("trailingPE", np.nan)

    # Decision logic based on last row
    latest = data.iloc[-1]
    criteria = (
        pe_ratio < 30 and
        latest["RSI"] < 70 and
        latest["Close"] > latest["EMA_20"] > latest["SMA_50"]
    )

    return criteria, data, pe_ratio

# --- Streamlit App ---
st.title("AI-Powered Stock Screener")
ticker_input = st.text_input("Enter Ticker Symbol (e.g. AAPL, MSFT, TSLA):")

if ticker_input:
    try:
        meets_criteria, chart_data, pe = screener(ticker_input)
        st.write(f"**P/E Ratio**: {pe:.2f}")
        st.line_chart(chart_data[["Close", "EMA_20", "SMA_50"]])

        if meets_criteria:
            st.success("✅ This stock meets the high-growth criteria!")
        else:
            st.warning("⚠️ This stock does not meet the criteria.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
