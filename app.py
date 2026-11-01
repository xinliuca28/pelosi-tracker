import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Portfolio Tracker", page_icon="🏛️", layout="wide")

# ------------------------------------
# 1. 强容错加载 JSON 数据 (绝对动态，无硬编码)
# ------------------------------------
def load_json(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error reading {filepath}: {e}")
            return {}
    return {}

congress_data = load_json("data/congress_data.json")
buffett_data = load_json("data/buffett_data.json")

# ------------------------------------
# 2. 动态构建成员数据库
# ------------------------------------
MEMBERS_DATABASE = {}

politician_metas = {
    "Nancy Pelosi (D - House)": {"party": "Democrat", "chamber": "House", "focus": "Tech, AI"},
    "Tommy Tuberville (R - Senate)": {"party": "Republican", "chamber": "Senate", "focus": "Defense, Energy"},
    "Mark Green (R - House)": {"party": "Republican", "chamber": "House", "focus": "Energy"},
    "Dan Crenshaw (R - House)": {"party": "Republican", "chamber": "House", "focus": "Tech, Energy"},
    "Josh Gottheimer (D - House)": {"party": "Democrat", "chamber": "House", "focus": "Financials"},
}

for name, meta in politician_metas.items():
    member_json = congress_data.get(name, {})
    MEMBERS_DATABASE[name] = {
        "party": meta["party"],
        "chamber": meta["chamber"],
        "focus": meta["focus"],
        "holdings": pd.DataFrame(member_json.get("holdings", [])),
        "trades": pd.DataFrame(member_json.get("trades", [])),
    }

MEMBERS_DATABASE["Warren Buffett (Berkshire)"] = {
    "party": "Institutional Investor (13F)",
    "chamber": "Berkshire Hathaway",
    "focus": "Value Investing",
    "holdings": pd.DataFrame(buffett_data.get("holdings", [])),
    "trades": pd.DataFrame(buffett_data.get("trades", [])),
}

# ------------------------------------
# 3. 渲染侧边栏
# ------------------------------------
st.sidebar.title("🏛️ Member Selection")
selected_member_name = st.sidebar.selectbox("Select Profile:", options=list(MEMBERS_DATABASE.keys()))

member_info = MEMBERS_DATABASE[selected_member_name]
df_holdings = member_info["holdings"]
df_options = member_info["trades"]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Party & Chamber**: {member_info['party']} - {member_info['chamber']}")
st.sidebar.markdown(f"**Focus**: {member_info['focus']}")

# ------------------------------------
# 4. 实时计算与可视化层 (基于纯 API 数据)
# ------------------------------------
st.title(f"🏛️ {selected_member_name.split(' (')[0]} Tracker")

# 如果持仓数据不为空，调取 Yahoo Finance 实时价格
if not df_holdings.empty and "Ticker" in df_holdings.columns:
    with st.spinner("Fetching real-time market data..."):
        tickers_list = df_holdings["Ticker"].tolist()
        try:
            market_data = yf.Tickers(" ".join(tickers_list))
            prices = {}
            for t in tickers_list:
                # 获取实时现价
                prices[t] = market_data.tickers[t].fast_info.get("lastPrice", 0.0)
            
            df_holdings["Current Price ($)"] = df_holdings["Ticker"].map(lambda t: round(prices.get(t, 0.0), 2))
            
            # 计算 ROI
            if "Est. Cost Basis ($)" in df_holdings.columns:
                df_holdings["Est. ROI (%)"] = (((df_holdings["Current Price ($)"] - df_holdings["Est. Cost Basis ($)"]) / df_holdings["Est. Cost Basis ($)"]) * 100).round(2)
        except Exception as e:
            st.warning("Could not fetch real-time prices at this moment.")

    # 渲染图表
    st.markdown("### 📊 Portfolio Visualizations")
    col1, col2 = st.columns(2)
    
    with col1:
        if "Est. Allocation (%)" in df_holdings.columns:
            fig_pie = px.pie(df_holdings, values="Est. Allocation (%)", names="Ticker", 
                             title="<b>Dynamic Asset Allocation</b>", hole=0.4)
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_pie, use_container_width=True)
            
    with col2:
        if "Est. ROI (%)" in df_holdings.columns:
            colors = ["#26a69a" if val >= 0 else "#ef5350" for val in df_holdings["Est. ROI (%)"]]
            fig_bar = go.Figure(data=[go.Bar(x=df_holdings["Ticker"], y=df_holdings["Est. ROI (%)"], marker_color=colors, text=df_holdings["Est. ROI (%)"].apply(lambda x: f"{x:+.1f}%"), textposition="auto")])
            fig_bar.update_layout(title="<b>Estimated ROI vs Cost Basis</b>", yaxis_title="Gain / Loss (%)")
            st.plotly_chart(fig_bar, use_container_width=True)

    # 渲染动态持仓表（带高亮格式）
    st.markdown("### 1. Dynamic Holdings (Aggregated from 5-Yr History)")
    st.dataframe(df_holdings, use_container_width=True, hide_index=True, 
                 column_config={
                     "Est. Value ($10k)": st.column_config.NumberColumn("Est. Value ($10k)", format="$%d0k"),
                     "Est. Allocation (%)": st.column_config.NumberColumn("Allocation (%)", format="%.1f%%"),
                     "Est. Cost Basis ($)": st.column_config.NumberColumn("Cost Basis ($)", format="$%.2f"),
                     "Current Price ($)": st.column_config.NumberColumn("Current Price ($)", format="$%.2f"),
                     "Est. ROI (%)": st.column_config.NumberColumn("Est. ROI (%)", format="%.2f%%"),
                 })
else:
    st.info("No holdings data available to visualize.")

# ------------------------------------
# 5. 渲染历史交易层
# ------------------------------------
st.markdown("### 2. Trade History (Direct from API)")
if not df_options.empty:
    st.dataframe(df_options, use_container_width=True, hide_index=True, height=min(max(len(df_options) * 35 + 45, 150), 600))
else:
    st.info("No 5-year trade data available from API.")
