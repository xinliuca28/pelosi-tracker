import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# 页面基础配置
st.set_page_config(
    page_title="美国国会议员持仓与交易追踪看板",
    page_icon="🏛️",
    layout="wide",
)

# ------------------------------------
# 1. 多议员数据库定义 (Database)
# ------------------------------------
MEMBERS_DATABASE = {
    "Nancy Pelosi (民主党 · 众议院)": {
        "party": "民主党 (D-CA)",
        "chamber": "众议院",
        "focus": "科技巨头、AI产业链、大额 LEAPS 看涨期权 (NVDA, GOOGL, BE)",
        "holdings": pd.DataFrame({
            "股票代码": ["GOOGL", "AMZN", "NVDA", "AAPL", "AVGO", "MSFT", "BE", "INTC"],
            "公司": ["Alphabet", "Amazon", "NVIDIA", "Apple", "Broadcom", "Microsoft", "Bloom Energy", "Intel"],
            "买入参考基准价 ($)": [140.0, 175.0, 120.0, 185.0, 140.0, 400.0, 12.0, 30.0],
            "估算持仓金额 (万美元)": [1610, 1590, 1560, 1540, 1500, 1500, 750, 410],
            "估算占比 (%)": [14.0, 13.8, 13.5, 13.3, 13.0, 13.0, 6.5, 3.5],
        }),
        "trades": pd.DataFrame({
            "国会申报/披露日期": ["2026-10-02", "2026-08-21", "2026-08-21", "2026-06-23", "2026-01-23", "2025-12-24"],
            "实际交易日期": ["2026-09-08", "2026-07-28", "2026-07-28", "2026-05-29", "2026-01-16", "2025-12-15"],
            "标的代码": ["REOF", "BE", "BE", "INTC", "NVDA", "AAPL"],
            "交易动作": ["🟢 买入 (Purchase)", "🟢 买入 (Purchase)", "🟢 买入 (Purchase)", "🟢 买入 (Purchase)", "🔵 行权 (Exercised)", "🔴 卖出 (Sale)"],
            "资产分类": ["LLC 房地产", "Call Option", "正股", "Call Option", "Option Exercised", "正股"],
            "交易细节描述": ["REOF XXX 实体投资", "100 Calls · $100 Strike (Exp 06/17/27)", "买入 5,000 股正股", "200 Calls · $50 Strike (Exp 03/19/27)", "行权 50 份 Call ($80 Strike)", "卖出 20,000 股苹果正股"],
            "申报区间金额": ["$500k - $1M", "$500k - $1M", "$500k - $1M", "$1M - $5M", "$250k - $500k", "$1M - $5M"],
            "midpoint_val": [750000, 750000, 750000, 3000000, 375000, 3000000],
            "underlying_shares": [None, 10000, 5000, 20000, 5000, 20000],
        })
    },
    "Tommy Tuberville (共和党 · 参议院)": {
        "party": "共和党 (R-AL)",
        "chamber": "参议院 (军事/农业委员会)",
        "focus": "国防军工、大宗商品期权、页岩气 (LMT, NOC, CL=F)",
        "holdings": pd.DataFrame({
            "股票代码": ["LMT", "NOC", "XOM", "CVX", "ADM", "HUM"],
            "公司": ["Lockheed Martin", "Northrop Grumman", "ExxonMobil", "Chevron", "Archer-Daniels-Midland", "Humana"],
            "买入参考基准价 ($)": [450.0, 470.0, 110.0, 150.0, 55.0, 350.0],
            "估算持仓金额 (万美元)": [1200, 950, 800, 650, 400, 300],
            "估算占比 (%)": [27.9, 22.1, 18.6, 15.1, 9.3, 7.0],
        }),
        "trades": pd.DataFrame({
            "国会申报/披露日期": ["2026-09-15", "2026-08-10", "2026-06-18", "2026-03-12", "2025-11-05"],
            "实际交易日期": ["2026-08-20", "2026-07-15", "2026-05-20", "2026-02-18", "2025-10-10"],
            "标的代码": ["LMT", "NOC", "XOM", "ADM", "HUM"],
            "交易动作": ["🟢 买入 (Purchase)", "🟢 买入 (Purchase)", "🔴 卖出 (Sale)", "🟢 买入 (Purchase)", "🔴 卖出 (Sale)"],
            "资产分类": ["正股", "Put Option (看跌期权)", "正股", "Commodity Option", "正股"],
            "交易细节描述": ["买入 2,500 股洛克希德马丁", "买入 50 份 Put 防御对冲", "减持 5,000 股埃克森美孚", "买入农产品期货看涨期权", "结案平仓卖出 Humana"],
            "申报区间金额": ["$1M - $5M", "$250k - $500k", "$500k - $1M", "$100k - $250k", "$250k - $500k"],
            "midpoint_val": [3000000, 375000, 750000, 175000, 375000],
            "underlying_shares": [2500, 5000, 5000, None, 1000],
        })
    },
    "Mark Green (共和党 · 众议院)": {
        "party": "共和党 (R-TN)",
        "chamber": "众议院 (国土安全委员会)",
        "focus": "高频中线波段、油气管道、医疗科技 (ET, PAA, VLO)",
        "holdings": pd.DataFrame({
            "股票代码": ["ET", "PAA", "VLO", "MPC", "KMI"],
            "公司": ["Energy Transfer", "Plains All American", "Valero Energy", "Marathon Petroleum", "Kinder Morgan"],
            "买入参考基准价 ($)": [14.0, 16.0, 130.0, 150.0, 18.0],
            "估算持仓金额 (万美元)": [1500, 1100, 900, 850, 600],
            "估算占比 (%)": [30.3, 22.2, 18.2, 17.2, 12.1],
        }),
        "trades": pd.DataFrame({
            "国会申报/披露日期": ["2026-09-28", "2026-09-10", "2026-07-14", "2026-05-08"],
            "实际交易日期": ["2026-09-01", "2026-08-15", "2026-06-20", "2026-04-12"],
            "标的代码": ["ET", "VLO", "PAA", "MPC"],
            "交易动作": ["🟢 买入 (Purchase)", "🔴 卖出 (Sale)", "🟢 买入 (Purchase)", "🔴 卖出 (Sale)"],
            "资产分类": ["正股", "正股", "正股", "正股"],
            "交易细节描述": ["波段加仓 50,000 股管道股 ET", "高位止盈卖出 5,000 股 Valero", "建仓 Plains All American", "减持马拉松石油"],
            "申报区间金额": ["$500k - $1M", "$500k - $1M", "$250k - $500k", "$250k - $500k"],
            "midpoint_val": [750000, 750000, 375000, 375000],
            "underlying_shares": [50000, 5000, 20000, 2500],
        })
    },
    "Dan Crenshaw (共和党 · 众议院)": {
        "party": "共和党 (R-TX)",
        "chamber": "众议院 (能源与商务委员会)",
        "focus": "半导体、清洁能源、软件巨头 (NVDA, AMAT, MSFT)",
        "holdings": pd.DataFrame({
            "股票代码": ["NVDA", "AMAT", "MSFT", "FCX", "SLB"],
            "公司": ["NVIDIA", "Applied Materials", "Microsoft", "Freeport-McMoRan", "Schlumberger"],
            "买入参考基准价 ($)": [115.0, 180.0, 410.0, 42.0, 45.0],
            "估算持仓金额 (万美元)": [850, 600, 550, 400, 300],
            "估算占比 (%)": [31.5, 22.2, 20.4, 14.8, 11.1],
        }),
        "trades": pd.DataFrame({
            "国会申报/披露日期": ["2026-08-18", "2026-06-05", "2026-03-22"],
            "实际交易日期": ["2026-07-20", "2026-05-10", "2026-02-28"],
            "标的代码": ["NVDA", "AMAT", "SLB"],
            "交易动作": ["🟢 买入 (Purchase)", "🟢 买入 (Purchase)", "🔴 卖出 (Sale)"],
            "资产分类": ["正股", "Call Option", "正股"],
            "交易细节描述": ["逢低加仓英伟达正股", "买入 20 份应用材料 Call", "清仓斯伦贝谢"],
            "申报区间金额": ["$250k - $500k", "$100k - $250k", "$100k - $250k"],
            "midpoint_val": [375000, 175000, 175000],
            "underlying_shares": [3000, 2000, 4000],
        })
    },
    "Josh Gottheimer (民主党 · 众议院)": {
        "party": "民主党 (D-NJ)",
        "chamber": "众议院 (金融服务委员会)",
        "focus": "金融银行股、大盘科技波段 (JPM, MS, AAPL, AMZN)",
        "holdings": pd.DataFrame({
            "股票代码": ["JPM", "MS", "AAPL", "AMZN", "GS"],
            "公司": ["JPMorgan Chase", "Morgan Stanley", "Apple", "Amazon", "Goldman Sachs"],
            "买入参考基准价 ($)": [195.0, 95.0, 210.0, 180.0, 450.0],
            "估算持仓金额 (万美元)": [1100, 900, 850, 800, 600],
            "估算占比 (%)": [25.9, 21.2, 20.0, 18.8, 14.1],
        }),
        "trades": pd.DataFrame({
            "国会申报/披露日期": ["2026-09-12", "2026-08-01", "2026-05-19"],
            "实际交易日期": ["2026-08-18", "2026-07-08", "2026-04-25"],
            "标的代码": ["JPM", "GS", "AAPL"],
            "交易动作": ["🟢 买入 (Purchase)", "🟢 买入 (Purchase)", "🔴 卖出 (Sale)"],
            "资产分类": ["正股", "正股", "正股"],
            "交易细节描述": ["金融财报季前增持摩根大通", "买入高盛正股", "减持苹果落袋为安"],
            "申报区间金额": ["$500k - $1M", "$250k - $500k", "$250k - $500k"],
            "midpoint_val": [750000, 375000, 375000],
            "underlying_shares": [3800, 800, 1800],
        })
    }
}

# ------------------------------------
# 2. 侧边栏 (Sidebar) 议员切换交互
# ------------------------------------
st.sidebar.title("🏛️ 议员追踪选择")
selected_member_name = st.sidebar.selectbox(
    "请选择要查看的国会议员：",
    options=list(MEMBERS_DATABASE.keys()),
    index=0
)

# 提取当前选中议员的数据集
member_info = MEMBERS_DATABASE[selected_member_name]
df_holdings = member_info["holdings"]
df_options = member_info["trades"]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**党派与选区**：{member_info['party']}")
st.sidebar.markdown(f"**所属委员会**：{member_info['chamber']}")
st.sidebar.markdown(f"**投资风格偏好**：\n{member_info['focus']}")

# ------------------------------------
# 3. 动态计算与行情抓取
# ------------------------------------
df_options["估算单价/权利金 ($)"] = df_options.apply(
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
        st.warning(f"行情接口提示: {e}")
    return prices

with st.spinner(f"正在加载 {selected_member_name} 的持仓与实时行情..."):
    tickers_list = df_holdings["股票代码"].tolist()
    realtime_prices = fetch_realtime_prices(tickers_list)
    df_holdings["当前最新价 ($)"] = df_holdings["股票代码"].map(lambda t: round(realtime_prices.get(t, 0.0), 2))
    df_holdings["估算持仓表现 (%)"] = ((df_holdings["当前最新价 ($)"] - df_holdings["买入参考基准价 ($)"]) / df_holdings["买入参考基准价 ($)"] * 100).round(2)

latest_filing_date = df_options["国会申报/披露日期"].max()

# ------------------------------------
# 4. 主界面渲染
# ------------------------------------
st.title(f"🏛️ {selected_member_name.split(' (')[0]} 持仓与交易追踪")
st.caption(f"📌 **国会公开申报数据**：最新披露日至 **{latest_filing_date}**。| ⚡ **实时行情**：对接 Yahoo Finance 市场数据。")

st.write("")

# 图表展示
st.markdown("### 📊 持仓组合可视化分析 (Plotly)")
col1, col2 = st.columns(2)

with col1:
    fig_pie = px.pie(
        df_holdings,
        values="估算持仓金额 (万美元)",
        names="股票代码",
        title="<b>重仓资产配置占比 (%)</b>",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(margin=dict(t=40, b=10, l=10, r=10), height=350)
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    colors = ['#26a69a' if val >= 0 else '#ef5350' for val in df_holdings["估算持仓表现 (%)"]]
    fig_bar = go.Figure(data=[go.Bar(
        x=df_holdings["股票代码"],
        y=df_holdings["估算持仓表现 (%)"],
        marker_color=colors,
        text=df_holdings["估算持仓表现 (%)"].apply(lambda x: f"{x:+.1f}%"),
        textposition='auto',
    )])
    fig_bar.update_layout(
        title="<b>买入参考基准至今的估算盈亏表现 (%)</b>",
        xaxis_title="股票代码",
        yaxis_title="涨跌幅 (%)",
        margin=dict(t=40, b=10, l=10, r=10),
        height=350
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.write("")

# 明细表格
st.markdown("### 1. 核心持仓与实时表现")
st.dataframe(
    df_holdings[["股票代码", "公司", "估算持仓金额 (万美元)", "估算占比 (%)", "买入参考基准价 ($)", "当前最新价 ($)", "估算持仓表现 (%)"]],
    use_container_width=True,
    hide_index=True,
    column_config={
        "估算持仓金额 (万美元)": st.column_config.NumberColumn("估算持仓金额 (万美元)", format="$%d万"),
        "当前最新价 ($)": st.column_config.NumberColumn("当前最新价 ($)", format="$%.2f"),
        "买入参考基准价 ($)": st.column_config.NumberColumn("买入参考基准价 ($)", format="$%.2f"),
        "估算持仓表现 (%)": st.column_config.NumberColumn("估算持仓表现 (%)", format="%.2f%%"),
    }
)

st.write("")

st.markdown("### 2. 国会 STOCK Act 历史申报交易明细")
action_filter = st.multiselect(
    "🔍 按交易动作筛选：",
    options=df_options["交易动作"].unique(),
    default=df_options["交易动作"].unique()
)

df_filtered = df_options[df_options["交易动作"].isin(action_filter)]

st.dataframe(
    df_filtered[["国会申报/披露日期", "实际交易日期", "标的代码", "交易动作", "资产分类", "交易细节描述", "申报区间金额", "估算单价/权利金 ($)"]],
    use_container_width=True,
    hide_index=True,
    column_config={
        "交易动作": st.column_config.TextColumn("交易动作", width="medium"),
        "估算单价/权利金 ($)": st.column_config.NumberColumn("估算单价/权利金 ($)", format="$%.2f"),
    }
)
