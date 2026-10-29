import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# Page basic configuration
st.set_page_config(
    page_title="U.S. Congressional Portfolio & Trade Tracker",
    page_icon="🏛️",
    layout="wide",
)

# ------------------------------------
# 1. Multi-Member Database Definition
# ------------------------------------
MEMBERS_DATABASE = {
    "Nancy Pelosi (D - House)": {
        "party": "Democrat (D-CA)",
        "chamber": "House of Representatives",
        "focus": "Big Tech, AI Infrastructure, Deep ITM LEAPS Call Options (NVDA, GOOGL, BE)",
        "holdings": pd.DataFrame({
            "Ticker": ["GOOGL", "AMZN", "NVDA", "AAPL", "AVGO", "MSFT", "BE", "INTC"],
            "Company": ["Alphabet", "Amazon", "NVIDIA", "Apple", "Broadcom", "Microsoft", "Bloom Energy", "Intel"],
            "Est. Cost Basis ($)": [140.0, 175.0, 120.0, 185.0, 140.0, 400.0, 12.0, 30.0],
            "Est. Value ($10k)": [1610, 1590, 1560, 1540, 1500, 1500, 750, 410],
            "Est. Allocation (%)": [14.0, 13.8, 13.5, 13.3, 13.0, 13.0, 6.5, 3.5],
        }),
        "trades": pd.DataFrame({
            "Filing Date": ["2026-10-02", "2026-08-21", "2026-08-21", "2026-06-23", "2026-01-23", "2025-12-24"],
            "Trade Date": ["2026-09-08", "2026-07-28", "2026-07-28", "2026-05-29", "2026-01-16", "2025-12-15"],
            "Ticker": ["REOF", "BE", "BE", "INTC", "NVDA", "AAPL"],
            "Action": ["🟢 Purchase", "🟢 Purchase", "🟢 Purchase", "🟢 Purchase", "🔵 Exercised", "🔴 Sale"],
            "Asset Class": ["LLC Real Estate", "Call Option", "Common Stock", "Call Option", "Option Exercised", "Common Stock"],
            "Description": ["REOF XXX Commercial Property", "100 Calls · $100 Strike (Exp 06/17/27)", "Bought 5,000 Shares", "200 Calls · $50 Strike (Exp 03/19/27)", "Exercised 50 Call Contracts ($80 Strike)", "Sold 20,000 Shares"],
            "Disclosed Range": ["$500k - $1M", "$500k - $1M", "$500k - $1M", "$1M - $5M", "$250k - $500k", "$1M - $5M"],
            "midpoint_val": [750000, 750000, 750000, 3000000, 375000, 3000000],
            "underlying_shares": [None, 10000, 5000, 20000, 5000, 20000],
        })
    },
    "Tommy Tuberville (R - Senate)": {
        "party": "Republican (R-AL)",
        "chamber": "Senate (Armed Services Committee)",
        "focus": "Defense Contractors, Commodity Futures/Options, Energy (LMT, NOC, CL=F)",
        "holdings": pd.DataFrame({
            "Ticker": ["LMT", "NOC", "XOM", "CVX", "ADM", "HUM"],
            "Company": ["Lockheed Martin", "Northrop Grumman", "ExxonMobil", "Chevron", "Archer-Daniels-Midland", "Humana"],
            "Est. Cost Basis ($)": [450.0, 470.0, 110.0, 150.0, 55.0, 350.0],
            "Est. Value ($10k)": [1200, 950, 800, 650, 400, 300],
            "Est. Allocation (%)": [27.9, 22.1, 18.6, 15.1, 9.3, 7.0],
        }),
        "trades": pd.DataFrame({
            "Filing Date": ["2026-09-15", "2026-08-10", "2026-06-18", "2026-03-12", "2025-11-05"],
            "Trade Date": ["2026-08-20", "2026-07-15", "2026-05-20", "2026-02-18", "2025-10-10"],
            "Ticker": ["LMT", "NOC", "XOM", "ADM", "HUM"],
            "Action": ["🟢 Purchase", "🟢 Purchase", "🔴 Sale", "🟢 Purchase", "🔴 Sale"],
            "Asset Class": ["Common Stock", "Put Option", "Common Stock", "Commodity Option", "Common Stock"],
            "Description": ["Bought 2,500 Shares", "50 Put Contracts (Hedging)", "Sold 5,000 Shares", "Agricultural Commodity Calls", "Closed Position"],
            "Disclosed Range": ["$1M - $5M", "$250k - $500k", "$500k - $1M", "$100k - $250k", "$250k - $500k"],
            "midpoint_val": [3000000, 375000, 750000, 175000, 375000],
            "underlying_shares": [2500, 5000, 5000, None, 1000],
        })
    },
    "Mark Green (R - House)": {
        "party": "Republican (R-TN)",
        "chamber": "House (Homeland Security Committee)",
        "focus": "Midstream Oil & Gas Pipelines, High-frequency Swing Trades (ET, PAA, VLO)",
        "holdings": pd.DataFrame({
            "Ticker": ["ET", "PAA", "VLO", "MPC", "KMI"],
            "Company": ["Energy Transfer", "Plains All American", "Valero Energy", "Marathon Petroleum", "Kinder Morgan"],
            "Est. Cost Basis ($)": [14.0, 16.0, 130.0, 150.0, 18.0],
            "Est. Value ($10k)": [1500, 1100, 900, 850, 600],
            "Est. Allocation (%)": [30.3, 22.2, 18.2, 17.2, 12.1],
        }),
        "trades": pd.DataFrame({
            "Filing Date": ["2026-09-28", "2026-09-10", "2026-07-14", "2026-05-08"],
            "Trade Date": ["2026-09-01", "2026-08-15", "2026-06-20", "2026-04-12"],
            "Ticker": ["ET", "VLO", "PAA", "MPC"],
            "Action": ["🟢 Purchase", "🔴 Sale", "🟢 Purchase", "🔴 Sale"],
            "Asset Class": ["Common Stock", "Common Stock", "Common Stock", "Common Stock"],
            "Description": ["Bought 50,000 Shares", "Sold 5,000 Shares (Profit Taking)", "Initiated Position", "Reduced Position"],
            "Disclosed Range": ["$500k - $1M", "$500k - $1M", "$250k - $500k", "$250k - $500k"],
            "midpoint_val": [750000, 750000, 375000, 375000],
            "underlying_shares": [50000, 5000, 20000, 2500],
        })
    },
    "Dan Crenshaw (R - House)": {
        "party": "Republican (R-TX)",
        "chamber": "House (Energy & Commerce Committee)",
        "focus": "Semiconductors, Clean Energy, Software Leaders (NVDA, AMAT, MSFT)",
        "holdings": pd.DataFrame({
            "Ticker": ["NVDA", "AMAT", "MSFT", "FCX", "SLB"],
            "Company": ["NVIDIA", "Applied Materials", "Microsoft", "Freeport-McMoRan", "Schlumberger"],
            "Est. Cost Basis ($)": [115.0, 180.0, 410.0, 42.0, 45.0],
            "Est. Value ($10k)": [850, 600, 550, 400, 300],
            "Est. Allocation (%)": [31.5, 22.2, 20.4, 14.8, 11.1],
        }),
        "trades": pd.DataFrame({
            "Filing Date": ["2026-08-18", "2026-06-05", "2026-03-22"],
            "Trade Date": ["2026-07-20", "2026-05-10", "2026-02-28"],
            "Ticker": ["NVDA", "AMAT", "SLB"],
            "Action": ["🟢 Purchase", "🟢 Purchase", "🔴 Sale"],
            "Asset Class": ["Common Stock", "Call Option", "Common Stock"],
            "Description": ["Bought Dip in NVDA", "Bought 20 Call Contracts", "Liquidated SLB"],
            "Disclosed Range": ["$250k - $500k", "$100k - $250k", "$100k - $250k"],
            "midpoint_val": [375000, 175000, 175000],
            "underlying_shares": [3000, 2000, 4000],
        })
    },
    "Josh Gottheimer (D - House)": {
        "party": "Democrat (D-NJ)",
        "chamber": "House (Financial Services Committee)",
        "focus": "Investment Banks, Financial Services, Large-Cap Tech (JPM, GS, AAPL)",
        "holdings": pd.DataFrame({
            "Ticker": ["JPM", "MS", "AAPL", "AMZN", "GS"],
            "Company": ["JPMorgan Chase", "Morgan Stanley", "Apple", "Amazon", "Goldman Sachs"],
            "Est. Cost Basis ($)": [195.0, 95.0, 210.0, 180.0, 450.0],
            "Est. Value ($10k)": [1100, 900, 850, 800, 600],
            "Est. Allocation (%)": [25.9, 21.2, 20.0, 18.8, 14.1],
        }),
        "trades": pd.DataFrame({
            "Filing Date": ["2026-09-12", "2026-08-01", "2026-05-19"],
            "Trade Date": ["2026-08-18", "2026-07-08", "2026-04-25"],
            "Ticker": ["JPM", "GS", "AAPL"],
            "Action": ["🟢 Purchase", "🟢 Purchase", "🔴 Sale"],
            "Asset Class": ["Common Stock", "Common Stock", "Common Stock"],
            "Description": ["Bought JPM Ahead of Earnings", "Bought GS Common Stock", "Trimmed AAPL Position"],
            "Disclosed Range": ["$500k - $1M", "$250k - $500k", "$250k - $500k"],
            "midpoint_val": [750000, 375000, 375000],
            "underlying_shares": [3800, 800, 1800],
        })
    }
}

# ------------------------------------
# 2. Sidebar Member Selector
# ------------------------------------
st.sidebar.title("🏛️ Member Selection")
selected_member_name = st.sidebar.selectbox(
    "Select Member of Congress:",
    options=list(MEMBERS_DATABASE.keys()),
    index=0
)

# Extract data for chosen member
member_info = MEMBERS_DATABASE[selected_member_name]
df_holdings = member_info["holdings"]
df_options = member_info["trades"]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Party & District**: {member_info['party']}")
st.sidebar.markdown(f"**Chamber/Committee**: {member_info['chamber']}")
st.sidebar.markdown(f"**Trading Focus**:\n{member_info['focus']}")

# ------------------------------------
# 3. Dynamic Calculation & Real-time Prices
# ------------------------------------
df_options["Est. Price/Premium ($)"] = df_options.apply(
    lambda row: round(row["midpoint_val"] / row["underlying_shares"], 2) if row["underlying_shares"] else None,
    axis=1
)

@st.cache_data(ttl=300)
def fetch_realtime_prices(tickers):
    prices = {}
    try:
        data = yf.Tickers(" ".join(tickers))
        for ticker in tickers:
            fast_info = data.tickers[ticker].fast_info
            prices[ticker] = fast_info["lastPrice"]
    except Exception as e:
        st.warning(f"Ticker price fetch warning: {e}")
    return prices

with st.spinner(f"Fetching real-time prices & data for {selected_member_name}..."):
    tickers_list = df_holdings["Ticker"].tolist()
    realtime_prices = fetch_realtime_prices(tickers_list)
    df_holdings["Current Price ($)"] = df_holdings["Ticker"].map(lambda t: round(realtime_prices.get(t, 0.0), 2))
    df_holdings["Est. ROI (%)"] = ((df_holdings["Current Price ($)"] - df_holdings["Est. Cost Basis ($)"]) / df_holdings["Est. Cost Basis ($)"] * 100).round(2)

latest_filing_date = df_options["Filing Date"].max()

# ------------------------------------
# 4. Main Dashboard UI
# ------------------------------------
st.title(f"🏛️ {selected_member_name.split(' (')[0]} Portfolio & Trade Tracker")
st.caption(f"📌 **Congressional Disclosure**: Latest Filing Date: **{latest_filing_date}** | ⚡ **Market Data**: Powered by Yahoo Finance.")

st.write("")

# Visual Charts
st.markdown("### 📊 Visual Portfolio Analytics")
col1, col2 = st.columns(2)

with col1:
    fig_pie = px.pie(
        df_holdings,
        values="Est. Value ($10k)",
        names="Ticker",
        title="<b>Asset Allocation Weight (%)</b>",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(margin=dict(t=40, b=10, l=10, r=10), height=350)
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    colors = ['#26a69a' if val >= 0 else '#ef5350' for val in df_holdings["Est. ROI (%)"]]
    fig_bar = go.Figure(data=[go.Bar(
        x=df_holdings["Ticker"],
        y=df_holdings["Est. ROI (%)"],
        marker_color=colors,
        text=df_holdings["Est. ROI (%)"].apply(lambda x: f"{x:+.1f}%"),
        textposition='auto',
    )])
    fig_bar.update_layout(
        title="<b>Estimated ROI since Cost Basis (%)</b>",
        xaxis_title="Ticker",
        yaxis_title="Gain / Loss (%)",
        margin=dict(t=40, b=10, l=10, r=10),
        height=350
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.write("")

# Table 1: Core Holdings
st.markdown("### 1. Primary Holdings & Real-time Performance")
st.dataframe(
    df_holdings[["Ticker", "Company", "Est. Value ($10k)", "Est. Allocation (%)", "Est. Cost Basis ($)", "Current Price ($)", "Est. ROI (%)"]],
    use_container_width=True,
    hide_index=True,
)
    column_config={
        "Est. Value ($10k)": st.column_config.NumberColumn
    }
