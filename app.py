import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Portfolio Tracker", page_icon="🏛️", layout="wide")

# 1. 强容错加载 JSON 数据
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

# 2. 动态构建成员数据库
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
    "party": "Institutional",
    "chamber": "Berkshire Hathaway",
    "focus": "Value Investing",
    "holdings": pd.DataFrame(buffett_data.get("holdings", [])),
    "trades": pd.DataFrame(buffett_data.get("trades", [])),
}

# 3. 渲染 UI
st.sidebar.title("🏛️ Member Selection")
selected_member_name = st.sidebar.selectbox("Select Profile:", options=list(MEMBERS_DATABASE.keys()))

member_info = MEMBERS_DATABASE[selected_member_name]
df_holdings = member_info["holdings"]
df_options = member_info["trades"]

st.title(f"🏛️ {selected_member_name.split(' (')[0]} Tracker")
st.sidebar.markdown(f"**Focus**: {member_info['focus']}")

if not df_holdings.empty:
    st.markdown("### 1. Dynamic Holdings")
    st.dataframe(df_holdings, use_container_width=True, hide_index=True)
else:
    st.info("No holdings data available.")

if not df_options.empty:
    st.markdown("### 2. Trade History (API Driven)")
    st.dataframe(df_options, use_container_width=True, hide_index=True)
else:
    st.info("No trade data available.")
