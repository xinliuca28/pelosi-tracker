import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# Page basic configuration
st.set_page_config(
    page_title="U.S. Congressional & Institutional Portfolio Tracker",
    page_icon="🏛️",
    layout="wide",
)

# ------------------------------------
# 0. Load External Dynamic Data Source
# ------------------------------------
trackers_data = {}
json_path = "data/trackers_data.json"
if os.path.exists(json_path):
  try:
    with open(json_path, "r", encoding="utf-8") as f:
      trackers_data = json.load(f)
  except Exception as e:
    st.error(f"Error loading trackers JSON data: {e}")

# ------------------------------------
# 1. Multi-Member Database Definition
# ------------------------------------
MEMBERS_DATABASE = {
    "Nancy Pelosi (D - House)": {
        "party": "Democrat (D-CA)",
        "chamber": "House of Representatives",
        "focus": "Big Tech, AI Infrastructure, Deep ITM LEAPS Call Options",
        "holdings": pd.DataFrame({
            "Ticker": ["GOOGL", "AMZN", "NVDA", "AAPL", "AVGO", "MSFT", "BE"],
            "Company": [
                "Alphabet",
                "Amazon",
                "NVIDIA",
                "Apple",
                "Broadcom",
                "Microsoft",
                "Bloom Energy",
            ],
            "Est. Cost Basis ($)": [140.0, 175.0, 120.0, 185.0, 140.0, 400.0, 12.0],
            "Est. Value ($10k)": [1610, 1590, 1560, 1540, 1500, 1500, 750],
            "Est. Allocation (%)": [16.0, 15.8, 15.5, 15.3, 15.0, 15.0, 7.4],
        }),
        # 优先读取外部动态拉取的数据，若为空则给一个空 DataFrame 兜底
        "trades": pd.DataFrame(
            trackers_data.get("Nancy Pelosi (D - House)", [])
        ),
    },
    "Tommy Tuberville (R - Senate)": {
        "party": "Republican (R-AL)",
        "chamber": "Senate (Armed Services Committee)",
        "focus": "Defense Contractors, Commodity Futures/Options, Energy",
        "holdings": pd.DataFrame({
            "Ticker": ["LMT", "NOC", "XOM", "CVX"],
            "Company": [
                "Lockheed Martin",
                "Northrop Grumman",
                "ExxonMobil",
                "Chevron",
            ],
            "Est. Cost Basis ($)": [450.0, 470.0, 110.0, 150.0],
            "Est. Value ($10k)": [1200, 950, 800, 650],
            "Est. Allocation (%)": [35.0, 28.0, 22.0, 15.0],
        }),
        "trades": pd.DataFrame(
            trackers_data.get("Tommy Tuberville (R - Senate)", [])
        ),
    },
    "Mark Green (R - House)": {
        "party": "Republican (R-TN)",
        "chamber": "House (Homeland Security Committee)",
        "focus": "Midstream Oil & Gas Pipelines, High-frequency Swing Trades",
        "holdings": pd.DataFrame({
            "Ticker": ["ET", "PAA", "VLO"],
            "Company": ["Energy Transfer", "Plains All American", "Valero Energy"],
            "Est. Cost Basis ($)": [14.0, 16.0, 130.0],
            "Est. Value ($10k)": [1500, 1100, 900],
            "Est. Allocation (%)": [45.0, 33.0, 22.0],
        }),
        "trades": pd.DataFrame(
            trackers_data.get("Mark Green (R - House)", [])
        ),
    },
    "Dan Crenshaw (R - House)": {
        "party": "Republican (R-TX)",
        "chamber": "House (Energy & Commerce Committee)",
        "focus": "Semiconductors, Clean Energy, Software Leaders",
        "holdings": pd.DataFrame({
            "Ticker": ["NVDA", "AMAT", "MSFT"],
            "Company": ["NVIDIA", "Applied Materials", "Microsoft"],
            "Est. Cost Basis ($)": [115.0, 180.0, 410.0],
            "Est. Value ($10k)": [850, 600, 550],
            "Est. Allocation (%)": [42.0, 30.0, 28.0],
        }),
        "trades": pd.DataFrame(
            trackers_data.get("Dan Crenshaw (R - House)", [])
        ),
    },
    "Josh Gottheimer (D - House)": {
        "party": "Democrat (D-NJ)",
        "chamber": "House (Financial Services Committee)",
        "focus": "Investment Banks, Financial Services, Large-Cap Tech",
        "holdings": pd.DataFrame({
            "Ticker": ["JPM", "MS", "AAPL"],
            "Company": ["JPMorgan Chase", "Morgan Stanley", "Apple"],
            "Est. Cost Basis ($)": [195.0, 95.0, 210.0],
            "Est. Value ($10k)": [1100, 900, 850],
            "Est. Allocation (%)": [39.0, 32.0, 29.0],
        }),
        "trades": pd.DataFrame(
            trackers_data.get("Josh Gottheimer (D - House)", [])
        ),
    },
    "Warren Buffett (Berkshire)": {
        "party": "Institutional Investor (13F)",
        "chamber": "Berkshire Hathaway",
        "focus": "Value Investing, Financials, Consumer Staples, Tech",
        "holdings": pd.DataFrame(
            trackers_data.get(
                "Warren Buffett (Berkshire)",
                [
                    {
                        "Ticker": "AAPL",
                        "Company": "Apple",
                        "Est. Cost Basis ($)": 35.0,
                        "Est. Value ($10k)": 842480,
                        "Est. Allocation (%)": 35.0,
                    }
                ],
            )
        ),
        "trades": pd.DataFrame({
            "Filing Date": ["2026-08-14"],
            "Trade Date": ["2026-06-30"],
            "Ticker": ["AAPL"],
            "Action": ["🔴 Sale"],
            "Asset Class": ["Common Stock"],
            "Description": ["Trimmed Position (Q2 13F)"],
            "Disclosed Range": ["$1B+"],
            "midpoint_val": [500000000],
            "underlying_shares": [10000000],
        }),
    },
}

# ------------------------------------
# 2. Sidebar Member Selector
# ------------------------------------
st.sidebar.title("🏛️ Member Selection")
selected_member_name = st.sidebar.selectbox(
    "Select Member of Congress:", options=list(MEMBERS_DATABASE.keys()), index=0
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
if (
    not df_options.empty
    and "midpoint_val" in df_options.columns
    and "underlying_shares" in df_options.columns
):
  df_options["Est. Price/Premium ($)"] = df_options.apply(
      lambda row: round(row["midpoint_val"] / row["underlying_shares"], 2)
      if row["underlying_shares"] and row["underlying_shares"] > 0
      else None,
      axis=1,
  )
else:
  df_options["Est. Price/Premium ($)"] = None


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


with st.spinner(
    f"Fetching real-time prices & data for {selected_member_name}..."
):
  tickers_list = df_holdings["Ticker"].tolist() if not df_holdings.empty else []
  realtime_prices = fetch_realtime_prices(tickers_list)
  if not df_holdings.empty:
    df_holdings["Current Price ($)"] = df_holdings["Ticker"].map(
        lambda t: round(realtime_prices.get(t, 0.0), 2)
    )
    df_holdings["Est. ROI (%)"] = (
        (
            (
                df_holdings["Current Price ($)"]
                - df_holdings["Est. Cost Basis ($)"]
            )
            / df_holdings["Est. Cost Basis ($)"]
        )
        * 100
    ).round(2)

latest_filing_date = (
    df_options["Filing Date"].max()
    if not df_options.empty and "Filing Date" in df_options.columns
    else "N/A"
)

# ------------------------------------
# 4. Main Dashboard UI
# ------------------------------------
st.title(f"🏛️ {selected_member_name.split(' (')[0]} Portfolio & Trade Tracker")
st.caption(
    f"📌 **Congressional Disclosure**: Latest Filing Date: **{latest_filing_date}**"
    " | ⚡ **Market Data**: Powered by Yahoo Finance."
)

st.write("")

# Visual Charts
st.markdown("### 📊 Visual Portfolio Analytics")
col1, col2 = st.columns(2)

with col1:
  if not df_holdings.empty:
    fig_pie = px.pie(
        df_holdings,
        values="Est. Value ($10k)",
        names="Ticker",
        title="<b>Asset Allocation Weight (%)</b>",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    fig_pie.update_layout(margin=dict(t=40, b=10, l=10, r=10), height=350)
    st.plotly_chart(fig_pie, use_container_width=True)
  else:
    st.info("No holdings data available.")

with col2:
  if not df_holdings.empty and "Est. ROI (%)" in df_holdings.columns:
    colors = [
        "#26a69a" if val >= 0 else "#ef5350"
        for val in df_holdings["Est. ROI (%)"]
    ]
    fig_bar = go.Figure(
        data=[
            go.Bar(
                x=df_holdings["Ticker"],
                y=df_holdings["Est. ROI (%)"],
                marker_color=colors,
                text=df_holdings["Est. ROI (%)"].apply(lambda x: f"{x:+.1f}%"),
                textposition="auto",
            )
        ]
    )
    fig_bar.update_layout(
        title="<b>Estimated ROI since Cost Basis (%)</b>",
        xaxis_title="Ticker",
        yaxis_title="Gain / Loss (%)",
        margin=dict(t=40, b=10, l=10, r=10),
        height=350,
    )
    st.plotly_chart(fig_bar, use_container_width=True)
  else:
    st.info("No ROI data available.")

st.write("")

# Table 1: Core Holdings
st.markdown("### 1. Primary Holdings & Real-time Performance")
if not df_holdings.empty:
  st.dataframe(
      df_holdings[[
          "Ticker",
          "Company",
          "Est. Value ($10k)",
          "Est. Allocation (%)",
          "Est. Cost Basis ($)",
          "Current Price ($)",
          "Est. ROI (%)",
      ]],
      use_container_width=True,
      hide_index=True,
      column_config={
          "Est. Value ($10k)": st.column_config.NumberColumn(
              "Est. Value ($10k)", format="$%d0k"
          ),
          "Current Price ($)": st.column_config.NumberColumn(
              "Current Price ($)", format="$%.2f"
          ),
          "Est. Cost Basis ($)": st.column_config.NumberColumn(
              "Est. Cost Basis ($)", format="$%.2f"
          ),
          "Est. ROI (%)": st.column_config.NumberColumn(
              "Est. ROI (%)", format="%.2f%%"
          ),
      },
  )
else:
  st.info("No holdings records.")

st.write("")

# Table 2: Trade History (自动适配高度，无需拖拽)
st.markdown("### 2. Historical Disclosure Records (STOCK Act Filings)")
if not df_options.empty and "Action" in df_options.columns:
  action_options = df_options["Action"].unique().tolist()
  action_filter = st.multiselect(
      "🔍 Filter by Action:",
      options=action_options,
      default=action_options,
  )
  df_filtered = df_options[df_options["Action"].isin(action_filter)]
else:
  df_filtered = pd.DataFrame()

# 根据筛选后的交易笔数动态计算高度
dynamic_height = min(max(len(df_filtered) * 35 + 45, 100), 600)

if not df_filtered.empty:
  st.dataframe(
      df_filtered[[
          "Filing Date",
          "Trade Date",
          "Ticker",
          "Action",
          "Asset Class",
          "Description",
          "Disclosed Range",
          "Est. Price/Premium ($)",
      ]],
      use_container_width=True,
      hide_index=True,
      height=dynamic_height,
      column_config={
          "Action": st.column_config.TextColumn("Action", width="medium"),
          "Est. Price/Premium ($)": st.column_config.NumberColumn(
              "Est. Price/Premium ($)", format="$%.2f"
          ),
      },
  )
else:
  st.info(
      "No transaction records found for this member from the external source."
  )
