import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# 页面基础配置
st.set_page_config(
    page_title="佩洛西股票持仓与期权实时看板",
    page_icon="🏛️",
    layout="wide",
)

# ------------------------------------
# 1. 基础数据源定义（补充合约股数与区间金额数字）
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

options_data = {
    "国会申报/披露日期 (Filing Date)": [
        "2026-10-02",
        "2026-08-21",
        "2026-08-21",
        "2026-08-21",
        "2026-08-21",
        "2026-06-23",
        "2026-06-23",
        "2026-01-23",
    ],
    "实际交易日期 (Trade Date)": [
        "2026-09-08",
        "2026-07-28",
        "2026-07-28",
        "2026-07-24",
        "2026-07-24",
        "2026-05-29",
        "2026-05-29",
        "2026-01-16",
    ],
    "标的代码": ["REOF", "BE", "BE", "BE", "INTC", "INTC", "UBER", "NVDA"],
    "资产分类": [
        "LLC Real Estate (房地产投资)",
        "Call Option (看涨期权)",
        "Common Stock (普通股)",
        "Call Option (看涨期权)",
        "Call Option (看涨期权)",
        "Call Option (看涨期权)",
        "Call Option (看涨期权)",
        "Option Exercised (期权行权)",
    ],
    "交易细节描述 / 行权价与到期日": [
        "REOF XXX, LLC 实体投资 (San Francisco 商业地产)",
        "100 Calls · $100 Strike (Exp 06/17/27)",
        "买入 5,000 股正股",
        "100 Calls · $100 Strike (Exp 06/17/27)",
        "50 Calls · $50 Strike (Exp 03/19/27)",
        "200 Calls · $50 Strike (Exp 03/19/27)",
        "200 Calls · $50 Strike (Exp 03/19/27)",
        "行权 50 份 Call ($80 Strike) 转化为 5,000 股正股",
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
    ],
    # 计算估算权利金所需的参数 (区间中点与对应标的股数)
    "midpoint_val": [
        750000,
        750000,
        750000,
        3000000,
        375000,
        3000000,
        750000,
        375000,
    ],
    "underlying_shares": [None, 10000, 5000, 10000, 5000, 20000, 20000, 5000],
}

df_holdings = pd.DataFrame(holdings_data)
df_options = pd.DataFrame(options_data)

# ------------------------------------
# 2. 动态计算估算权利金 (Premium)
# ------------------------------------
# 仅对 Call Option 类型计算每股权利金 (区间中点 / 对应正股总数)
df_options["估算单股买入价 / 权利金 ($)"] = df_options.apply(
    lambda row: round(row["midpoint_val"] / row["underlying_shares"], 2)
    if row["underlying_shares"] and "Call" in row["资产分类"]
    else (
        round(row["midpoint_val"] / row["underlying_shares"], 2)
        if row["underlying_shares"] and "Stock" in row["资产分类"]
        else None
    ),
    axis=1,
)


# ------------------------------------
# 3. 核心行情抓取：yfinance
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


with st.spinner("正在链接 Yahoo Finance 实时行情并生成 Plotly 交互图表..."):
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

latest_filing_date = df_options["国会申报/披露日期 (Filing Date)"].max()

# ------------------------------------
# 4. Header 与小字
# ------------------------------------
st.title("🏛️ 佩洛西（Nancy Pelosi）持仓与交易自动追踪看板")

st.caption(
    f"📌 **数据披露更新**：根据美国国会 STOCK Act 官方申报公开资料，截至"
    f" **{latest_filing_date}** 的最新披露信息自动汇总生成。| ⚡ **行情与图表**：对接到"
    " Yahoo Finance 实时报价与 Plotly 动态分析。"
)

st.write("")

# ------------------------------------
# 5. Plotly 可视化模块
# ------------------------------------
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

# ------------------------------------
# 6. 表格展示 (含最新加注的估算权利金)
# ------------------------------------
st.markdown("### 1. 佩洛西目前的主要持仓（实时行情）")

df_display = df_holdings[
    [
        "股票代码",
        "公司",
        "估算持仓金额 (万美元)",
        "估算占比 (%)",
        "买入参考基准价 ($)",
        "当前最新价 ($)",
        "估算持仓表现 (%)",
    ]
]

st.dataframe(
    df_display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "股票代码": st.column_config.TextColumn("股票代码", width="small"),
        "公司": st.column_config.TextColumn("公司", width="medium"),
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

st.markdown("### 2. 最近披露了哪些买入？")
st.caption(
    "💡 **注**：根据 STOCK Act"
    " 规定，官方仅申报总金额区间。下表中新增的「**估算每股权利金**」是基于申报区间中点与合约对应股数反推得出的参考价。"
)

# 过滤并按合适顺序输出交易明细表
df_options_display = df_options[
    [
        "国会申报/披露日期 (Filing Date)",
        "实际交易日期 (Trade Date)",
        "标的代码",
        "资产分类",
        "交易细节描述 / 行权价与到期日",
        "申报区间金额",
        "估算单股买入价 / 权利金 ($)",
    ]
]

st.dataframe(
    df_options_display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "资产分类": st.column_config.SelectboxColumn(
            "资产分类",
            options=[
                "Common Stock (普通股)",
                "Call Option (看涨期权)",
                "Option Exercised (期权行权)",
                "LLC Real Estate (房地产投资)",
            ],
            required=True,
        ),
        "估算单股买入价 / 权利金 ($)": st.column_config.NumberColumn(
            "估算单股权利金/买价 ($)", format="$%.2f"
        ),
    },
)

st.write("")

# ------------------------------------
# 7. 说明事项
# ------------------------------------
st.markdown("### 3. 如何理解这些数据？")
st.markdown(
    "1. **披露不等于实时持仓**。"
    " 美国国会议员可以在交易发生后的一段时间内申报，因此公开数据存在时间差。"
)
st.markdown(
    "2. **金额是区间与中点估算**。 申报金额为区间（如 $1,000,001 - $5,000,000），每股权利金是由区间中点值除以标的股数推算出来的估算参考值。"
)
st.markdown(
    "3. **股票和期权要分开看**。"
    " 看涨期权（Call Option）自带杠杆效应，买入价格为权利金（Premium），并不等同于直接持有正股。"
)
