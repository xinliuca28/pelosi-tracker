import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# 页面基础配置
st.set_page_config(
    page_title="佩洛西持仓与交易自动追踪看板",
    page_icon="🏛️",
    layout="wide",
)

# ------------------------------------
# 1. 持仓汇总数据 (Holdings)
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
    "买入参考基准价 ($)": [
        140.0,
        175.0,
        120.0,
        185.0,
        140.0,
        400.0,
        270.0,
        275.0,
        12.0,
        30.0,
    ],
    "估算持仓金额 (万美元)": [
        1610,
        1590,
        1560,
        1540,
        1500,
        1500,
        1500,
        1500,
        750,
        410,
    ],
    "估算占比 (%)": [
        10.5,
        10.4,
        10.1,
        10.0,
        9.8,
        9.8,
        9.8,
        9.8,
        4.9,
        2.7,
    ],
}

# ------------------------------------
# 2. 全量交易明细数据 (包含正股买卖、期权与实体投资)
# ------------------------------------
options_data = {
    "国会申报/披露日期": [
        "2026-10-02",
        "2026-08-21",
        "2026-08-21",
        "2026-08-21",
        "2026-08-21",
        "2026-06-23",
        "2026-06-23",
        "2026-01-23",
        "2026-01-23",
        "2026-01-23",
    ],
    "实际交易日期": [
        "2026-09-08",
        "2026-07-28",
        "2026-07-28",
        "2026-07-24",
        "2026-07-24",
        "2026-05-29",
        "2026-05-29",
        "2026-01-16",
        "2025-12-30",
        "2025-12-24",
    ],
    "标的代码": [
        "REOF",
        "BE",
        "BE",
        "BE",
        "INTC",
        "INTC",
        "UBER",
        "NVDA",
        "DIS",
        "AAPL",
    ],
    "交易动作": [
        "🟢 买入 (Purchase)",
        "🟢 买入 (Purchase)",
        "🟢 买入 (Purchase)",
        "🟢 买入 (Purchase)",
        "🟢 买入 (Purchase)",
        "🟢 买入 (Purchase)",
        "🟢 买入 (Purchase)",
        "🔵 行权 (Exercised)",
        "🔴 卖出 (Sale)",
        "🔴 卖出 (Sale)",
    ],
    "资产分类": [
        "LLC 房地产实体",
        "Call Option (看涨期权)",
        "Common Stock (正股)",
        "Call Option (看涨期权)",
        "Call Option (看涨期权)",
        "Call Option (看涨期权)",
        "Call Option (看涨期权)",
        "Option Exercised (期权行权)",
        "Common Stock (正股)",
        "Common Stock (正股)",
    ],
    "交易细节描述 / 数量": [
        "REOF XXX, LLC 实体投资 (旧金山商业地产)",
        "买入 100 份 Call · $100 Strike (Exp 06/17/27)",
        "买入 5,000 股正股",
        "买入 100 份 Call · $100 Strike (Exp 06/17/27)",
        "买入 50 份 Call · $50 Strike (Exp 06/17/27)",
        "买入 200 份 Call · $50 Strike (Exp 03/19/27)",
        "买入 200 份 Call · $50 Strike (Exp 03/19/27)",
        "行权 50 份 Call ($80 Strike) 转化为 5,000 股正股",
        "卖出 10,000 股迪士尼正股",
        "卖出 45,000 股苹果正股",
    ],
    "申报区间金额": [
        "$500,001 - $1,000,000",
        "$500,001 - $1,000,000",
        "$500,001 - $1,000,000",
        "$1,000,001 - $5,000,000",
        "$250,001 - $500,000",
        "$1,000,001 - $5,000,000",
        "$500,001 - $1,000,000",
        "$250,001 - $500,000",
        "$1,000,001 - $5,000,000",
        "$5,000,001 - $25,000,000",
    ],
    # 计算估算权利金或正股买价
    "midpoint_val": [
        750000,
        750000,
        750000,
        3000000,
        375000,
        3000000,
        750000,
        375000,
        3000000,
        15000000,
    ],
    "underlying_shares": [
        None,
        10000,
        5000,
        10000,
        5000,
        20000,
        20000,
        5000,
        10000,
        45000,
    ],
}

df_holdings = pd.DataFrame(holdings_data)
df_options = pd.DataFrame(options_data)

# ------------------------------------
# 3. 估算单价 / 权利金计算
# ------------------------------------
df_options["估算单价/权利金 ($)"] = df_options.apply(
    lambda row: round(row["midpoint_val"] / row["underlying_shares"], 2)
    if row["underlying_shares"]
    else None,
    axis=1,
)


# ------------------------------------
# 4. 实时行情对接 (yfinance)
# ------------------------------------
@st.cache_data(ttl=300)
def fetch_realtime_prices(tickers):
    prices = {}
    try:
        data = yf.Tickers(" ".join(tickers))
        for ticker in tickers:
            fast_info = data.tickers[ticker].fast_info
            prices[ticker] = fast_info["lastPrice"]
    except Exception as e:
        st.warning(f"行情接口提示: {e}")
    return prices


with st.spinner("正在链接 Yahoo Finance 实时行情与交易明细..."):
    tickers_list = df_holdings["股票代码"].tolist()
    realtime_prices = fetch_realtime_prices(tickers_list)

    df_holdings["当前最新价 ($)"] = df_holdings["股票代码"].map(
        lambda t: round(realtime_prices.get(t, 0.0), 2)
    )

    df_holdings["估算持仓表现 (%)"] = (
        (
            df_holdings["当前最新价 ($)"]
            - df_holdings["买入参考基准价 ($)"]
        )
        / df_holdings["买入参考基准价 ($)"]
        * 100
    ).round(2)

latest_filing_date = df_options["国会申报/披露日期"].max()

# ------------------------------------
# 5. Dashboard 界面渲染
# ------------------------------------
st.title("🏛️ 佩洛西（Nancy Pelosi）持仓与交易自动追踪看板")

st.caption(
    f"📌 **数据披露更新**：截至 **{latest_filing_date}** 的最新披露。| ⚡"
    " **实时行情**：对接 Yahoo Finance 市场报价。"
)

st.write("")

# 图表模块
st.markdown("### 📊 持仓组合可视化分析 (Plotly)")
col1, col2 = st.columns(2)

with col1:
    fig_pie = px.pie(
        df_holdings,
        values="估算持仓金额 (万美元)",
        names="股票代码",
        title="<b>重仓股资产配置占比 (%)</b>",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig_pie.update_traces(
        textposition="inside", textinfo="percent+label"
    )
    fig_pie.update_layout(margin=dict(t=40, b=10, l=10, r=10), height=350)
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    colors = [
        "#26a69a" if val >= 0 else "#ef5350"
        for val in df_holdings["估算持仓表现 (%)"]
    ]
    fig_bar = go.Figure(
        data=[
            go.Bar(
                x=df_holdings["股票代码"],
                y=df_holdings["估算持仓表现 (%)"],
                marker_color=colors,
                text=df_holdings["估算持仓表现 (%)"].apply(
                    lambda x: f"{x:+.1f}%"
                ),
                textposition="auto",
            )
        ]
    )
    fig_bar.update_layout(
        title="<b>买入参考基准至今的估算盈亏表现 (%)</b>",
        xaxis_title="股票代码",
        yaxis_title="涨跌幅 (%)",
        margin=dict(t=40, b=10, l=10, r=10),
        height=350,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.write("")

# 模块：持仓列表
st.markdown("### 1. 佩洛西目前的主要持仓（实时行情）")
st.dataframe(
    df_holdings[
        [
            "股票代码",
            "公司",
            "估算持仓金额 (万美元)",
            "估算占比 (%)",
            "买入参考基准价 ($)",
            "当前最新价 ($)",
            "估算持仓表现 (%)",
        ]
    ],
    use_container_width=True,
    hide_index=True,
    column_config={
        "估算持仓金额 (万美元)": st.column_config.NumberColumn(
            "估算持仓金额 (万美元)", format="$%d万"
        ),
        "当前最新价 ($)": st.column_config.NumberColumn(
            "当前最新价 ($)", format="$%.2f"
        ),
        "买入参考基准价 ($)": st.column_config.NumberColumn(
            "买入参考基准价 ($)", format="$%.2f"
        ),
        "估算持仓表现 (%)": st.column_config.NumberColumn(
            "估算持仓表现 (%)", format="%.2f%%"
        ),
    },
)

st.write("")

# 模块：交易历史明细（支持正股买卖/期权/筛选）
st.markdown("### 2. 国会 STOCK Act 全量交易明细（含正股买卖与期权）")

# 筛选器交互
action_filter = st.multiselect(
    "🔍 按交易动作筛选：",
    options=df_options["交易动作"].unique(),
    default=df_options["交易动作"].unique(),
)

df_filtered = df_options[df_options["交易动作"].isin(action_filter)]

df_options_display = df_filtered[
    [
        "国会申报/披露日期",
        "实际交易日期",
        "标的代码",
        "交易动作",
        "资产分类",
        "交易细节描述 / 数量",
        "申报区间金额",
        "估算单价/权利金 ($)",
    ]
]

st.dataframe(
    df_options_display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "交易动作": st.column_config.TextColumn("交易动作", width="medium"),
        "估算单价/权利金 ($)": st.column_config.NumberColumn(
            "估算单价/权利金 ($)", format="$%.2f"
        ),
    },
)
