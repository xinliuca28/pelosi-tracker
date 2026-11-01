import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="U.S. Congressional & Institutional Portfolio Tracker",
    page_icon="🏛️",
    layout="wide",
)

# 独立加载国会数据
congress_data = {}
if os.path.exists("data/congress_data.json"):
  with open("data/congress_data.json", "r", encoding="utf-8") as f:
    congress_data = json.load(f)

# 独立加载巴菲特 13F 数据
buffett_data = {}
if os.path.exists("data/buffett_data.json"):
  with open("data/buffett_data.json", "r", encoding="utf-8") as f:
    buffett_data = json.load(f)

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
        "trades": pd.DataFrame(
            congress_data.get("Nancy Pelosi (D - House)", [])
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
            congress_data.get("Tommy Tuberville (R - Senate)", [])
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
        "trades": pd.DataFrame(congress_data.get("Mark Green (R - House)", [])),
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
            congress_data.get("Dan Crenshaw (R - House)", [])
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
            congress_data.get("Josh Gottheimer (D - House)", [])
        ),
    },
    "Warren Buffett (Berkshire)": {
        "party": "Institutional Investor (13F)",
        "chamber": "Berkshire Hathaway",
        "focus": "Value Investing, Financials, Consumer Staples, Tech",
        "holdings": pd.DataFrame(
            buffett_data.get(
                "holdings",
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
        "trades": pd.DataFrame(buffett_data.get("trades", [])),
    },
}

# --- 后续的侧边栏、实时行情与 Plotly 图表渲染逻辑保持完全不变 ---
