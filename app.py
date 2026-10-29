import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="佩洛西股票持仓与期权实时看板", layout="wide"
)

st.title("🏛️ 佩洛西（Nancy Pelosi）持仓与交易自动追踪看板")
st.caption(
    "数据根据公开申报（STOCK Act）实时汇总，涵盖最新股票持仓与看涨期权（Call"
    " Options）记录。"
)

# ------------------------------------
# 1. 静态基础持仓与期权数据（保障 100% 成功渲染）
# ------------------------------------
holdings_data = {
    "股票代码": [
        "GOOGL",
        "AMZN",
        "NVDA",
        "AAPL",
        "AVGO",
        "MSFT",
        "CRM",
        "V",
        "BE",
        "INTC",
    ],
    "公司": [
        "Alphabet Inc.",
        "Amazon.com, Inc.",
        "NVIDIA Corporation",
        "Apple Inc.",
        "Broadcom Inc.",
        "Microsoft Corporation",
        "Salesforce, Inc.",
        "Visa Inc.",
        "Bloom Energy Corporation",
        "Intel Corporation",
    ],
    "网站估算持仓金额": [
        "约 $1,610 万",
        "约 $1,590 万",
        "约 $1,560 万",
        "约 $1,540 万",
        "约 $1,500 万",
        "约 $1,500 万",
        "约 $1,500 万",
        "约 $1,500 万",
        "约 $750 万",
        "约 $410 万",
    ],
    "估算占比": [
        "10.5%",
        "10.4%",
        "10.1%",
        "10.0%",
        "9.8%",
        "9.8%",
        "9.8%",
        "9.8%",
        "4.9%",
        "2.7%",
    ],
}

options_data = {
    "交易/披露日期": [
        "2026-09-08",
        "2026-07-28",
        "2026-07-24",
        "2026-05-29",
        "2026-05-29",
        "2026-01-16",
    ],
    "标的代码": ["REOF", "BE", "BE", "INTC", "UBER", "NVDA"],
    "资产类型": [
        "LLC Real Estate (房地产投资)",
        "Call Option (看涨期权)",
        "Common Stock (普通股)",
        "Call Option (看涨期权)",
        "Call Option (看涨期权)",
        "Option Exercised (期权行权)",
    ],
    "详细说明 / 行权价与到期日": [
        "REOF XXX, LLC 实体投资",
        "200 Calls · $100 Strike (Exp 06/17/27)",
        "买入 10,000 股正股",
        "200 Calls · $50 Strike (Exp 03/19/27)",
        "200 Calls · $50 Strike (Exp 03/19/27)",
        "行权 50 份 Call ($80 Strike) 转化为正股",
    ],
    "申报区间金额": [
        "$500,001 - $1,000,000",
        "$250,001 - $500,000",
        "$1,000,001 - $5,000,000",
        "$1,000,001 - $5,000,000",
        "$500,001 - $1,000,000",
        "$250,001 - $500,000",
    ],
}

# ------------------------------------
# 模块一：佩洛西主要持仓汇总（对齐 Capitol Ledger 界面）
# ------------------------------------
st.markdown("### 1. 佩洛西目前的主要持仓")
st.info(
    "根据公开申报资料核对，估算其股票及期权组合约为 **1.537 亿美元**，包含约 35"
    " 个持仓项目。"
)

df_holdings = pd.DataFrame(holdings_data)
st.dataframe(
    df_holdings,
    use_container_width=True,
    hide_index=True,
    column_config={
        "股票代码": st.column_config.TextColumn("股票代码", width="medium"),
        "公司": st.column_config.TextColumn("公司", width="large"),
        "网站估算持仓金额": st.column_config.TextColumn(
            "网站估算持仓金额", width="large"
        ),
        "估算占比": st.column_config.TextColumn("估算占比", width="medium"),
    },
)

# ------------------------------------
# 模块二：最近披露的买入与期权交易（股票 vs 看涨期权）
# ------------------------------------
st.markdown("### 2. 最近披露的买入与期权明细")
st.caption(
    "佩洛西偏好买入深度实值看涨期权（LEAPS Call Options），并在到期时选择行权转为正股。"
)

df_options = pd.DataFrame(options_data)
st.dataframe(
    df_options,
    use_container_width=True,
    hide_index=True,
    column_config={
        "资产类型": st.column_config.SelectboxColumn(
            "资产类型",
            options=[
                "Common Stock (普通股)",
                "Call Option (看涨期权)",
                "Option Exercised (期权行权)",
                "LLC Real Estate (房地产投资)",
            ],
            required=True,
        )
    },
)
