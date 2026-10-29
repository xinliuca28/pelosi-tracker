import pandas as pd
import streamlit as st

# 页面基础配置
st.set_page_config(
    page_title="佩洛西股票持仓与期权实时看板", layout="wide"
)

# ------------------------------------
# 1. 基础数据源定义
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
}

df_holdings = pd.DataFrame(holdings_data)
df_options = pd.DataFrame(options_data)

# 自动获取当前数据集中的最新披露日期
latest_filing_date = df_options["国会申报/披露日期 (Filing Date)"].max()

# ------------------------------------
# 2. 页面 Header 及自动加载的小字说明
# ------------------------------------
st.title("🏛️ 佩洛西（Nancy Pelosi）持仓与交易自动追踪看板")

# 开头动态渲染的小字：根据最新 Filing Date 自动变动
st.caption(
    f"📌 **数据披露更新**：根据美国国会 STOCK Act 官方申报公开资料，截至"
    f" **{latest_filing_date}** 的最新披露信息自动汇总生成。"
)

st.write("")  # 增加间距

# ------------------------------------
# 模块一：佩洛西目前的主要持仓（还原截图 1 样式）
# ------------------------------------
st.markdown("### 1. 佩洛西目前的主要持仓")
st.write(
    "根据 Capitol Ledger 公开申报资料核对，网站估算其股票及期权组合约为 **1.537"
    " 亿美元**，涉及约 35 个持仓项目。"
    " 这是基于披露金额区间等数据计算的估算值，并非官方公布的实时账户余额。"
)

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

st.write("")  # 增加间距

# ------------------------------------
# 模块二：最近披露了哪些买入？（还原截图 2 样式，增加期权标注）
# ------------------------------------
st.markdown("### 2. 最近披露了哪些买入？")
st.write("截至目前检索到的最新披露，主要有以下记录：")

# 列表要点说明
st.markdown(
    f"- **{latest_filing_date} 申报**：申报投资 REOF XXX, LLC，金额为 50 万至 100"
    " 万美元；这是房地产相关 LLC 投资，并非普通股票。"
)
st.markdown(
    "- **2026 年 8 月 21 日申报**：多笔 Bloom Energy (BE) 股票及看涨期权交易。"
)
st.markdown(
    "- **2026 年 8 月 21 日申报**：多笔 Intel (INTC) 股票及期权交易。"
)
st.markdown(
    "- **2026 年 6 月 23 日申报**：披露购买 Uber 股票及相关看涨期权。"
)

st.write("")

# 呈现带分栏的完整明细表格
st.subheader("📋 详细披露与期权明细（包含交易日与申报日）")
st.dataframe(
    df_options,
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
        )
    },
)

st.write("")  # 增加间距

# ------------------------------------
# 模块三：如何理解这些数据？（还原截图 2 底部注意事项）
# ------------------------------------
st.markdown("### 3. 如何理解这些数据？")
st.write("有三点需要注意：")
st.markdown(
    "1. **披露不等于实时持仓**。"
    " 美国国会议员可以在交易发生后的一段时间内申报，因此公开数据存在时间差。"
)
st.markdown(
    "2. **金额是区间**。 例如，申报金额可能是 100 万至 500"
    " 万美元，第三方网站通常用区间中点等方法估算。"
)
st.markdown(
    "3. **股票和期权要分开看**。"
    " 看涨期权并不等同于直接持有相同数量的股票，风险和价值变化方式也不同。"
)
