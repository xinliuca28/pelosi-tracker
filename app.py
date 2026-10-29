import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# 页面配置
st.set_page_config(
    page_title="佩洛西股票持仓与期权实时看板", layout="wide"
)

st.title("🏛️ 佩洛西（Nancy Pelosi）持仓与交易自动追踪看板")
st.caption(
    "数据同步自 GitHub 开源数据集 (capitol-stock-watch-open-data)，实时自动更新。"
)

# 1. 自动拉取 GitHub 上的最新公开数据集
TRADES_URL = "https://raw.githubusercontent.com/capitol-stock-watch/capitol-stock-watch-open-data/main/congress_trades_latest.csv"
OPTIONS_URL = "https://raw.githubusercontent.com/capitol-stock-watch/capitol-stock-watch-open-data/main/congress_options_trades.csv"


@st.cache_data(ttl=3600)  # 每小时自动刷新缓存
def load_data():
    try:
        trades_df = pd.read_csv(TRADES_URL)
        options_df = pd.read_csv(OPTIONS_URL)
        return trades_df, options_df
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return pd.DataFrame(), pd.DataFrame()


trades_df, options_df = load_data()

# 2. 过滤 Nancy Pelosi 的交易记录
pelosi_trades = trades_df[
    trades_df["politician"].str.contains("Pelosi", na=False)
].copy()

# ------------------------------------
# 模块一：核心持仓汇总（呈现为您截图中的样式）
# ------------------------------------
st.markdown("### 1. 佩洛西目前的主要持仓")

# 处理金额区间，计算估算金额中点
amount_map = {
    "$1,001 - $15,000": 8000,
    "$15,001 - $50,000": 32500,
    "$50,001 - $100,000": 75000,
    "$100,001 - $250,000": 175000,
    "$250,001 - $500,000": 375000,
    "$500,001 - $1,000,000": 750000,
    "$1,000,001 - $5,000,000": 3000000,
    "$5,000,001 - $25,000,000": 15000000,
    "$25,000,001 - $50,000,000": 37500000,
}

if not pelosi_trades.empty:
    pelosi_trades["est_amount"] = (
        pelosi_trades["amount"].map(amount_map).fillna(50000)
    )

    # 按股票代码聚合估算金额
    portfolio = (
        pelosi_trades.groupby(["ticker", "asset_description"])[
            "est_amount"
        ]
        .sum()
        .reset_index()
    )
    total_val = portfolio["est_amount"].sum()

    portfolio["估算占比"] = (
        (portfolio["est_amount"] / total_val) * 100
    ).round(1).astype(str) + "%"
    portfolio["网站估算持仓金额"] = portfolio["est_amount"].apply(
        lambda x: f"约 ${x/1000000:.2f} 万"
        if x < 10000000
        else f"约 ${x/10000:.0f} 万"
    )

    # 改名重组列，完美对齐截图界面
    portfolio_display = portfolio.rename(
        columns={"ticker": "股票代码", "asset_description": "公司"}
    )[["股票代码", "公司", "网站估算持仓金额", "估算占比"]]

    # 渲染卡片总计
    st.info(
        f"**当前汇总**：估算持仓项目共 `{len(portfolio)}` 个，估算组合总价值"
        f" **${total_val/1000000:.2f}M 美元**。"
    )

    # 渲染表格（支持隐藏索引）
    st.dataframe(portfolio_display, use_container_width=True, hide_index=True)

# ------------------------------------
# 模块二：近期公开申报记录（普通股 vs 期权）
# ------------------------------------
st.markdown("### 2. 最近披露的买入与期权交易")

if not pelosi_trades.empty:
    recent_trades = pelosi_trades.sort_values(
        by="transaction_date", ascending=False
    ).head(15)
    st.dataframe(
        recent_trades[
            [
                "transaction_date",
                "ticker",
                "type",
                "amount",
                "asset_description",
            ]
        ],
        use_container_width=True,
        hide_index=True,
        column_config={
            "transaction_date": "交易/披露日期",
            "ticker": "股票代码",
            "type": "交易类型 (Buy/Sell)",
            "amount": "申报区间金额",
            "asset_description": "资产详细描述 (含期权标注)",
        },
    )
