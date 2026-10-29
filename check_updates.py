import os
import pandas as pd
import requests

# 1. 设置您关注的 5 位议员白名单
TARGET_MEMBERS = [
    "Nancy Pelosi",
    "Tommy Tuberville",
    "Mark Green",
    "Dan Crenshaw",
    "Josh Gottheimer",
]

# 2. 开源国会交易数据集 CSV 地址
DATA_URL = "https://www.capitolstockwatch.com/data/open-data/congress_trades_latest.csv"


def send_wxpusher(member, ticker, action, date):
  """使用原生 requests 向 WxPusher 发送微信提醒"""
  app_token = os.environ.get("WXPUSHER_APP_TOKEN")
  user_uid = os.environ.get("WXPUSHER_UID")

  if not app_token or not user_uid:
    print("⚠️ 未检测到 WxPusher 环境变量，跳过微信推送。")
    return

  url = "https://wxpusher.zjiecode.com/api/send/message"
  payload = {
      "appToken": app_token,
      "content": f"""
### 🏛️ 发现白名单议员最新交易!

* **议员**: {member}
* **代码**: {ticker}
* **动作**: {action}
* **披露日期**: {date}

[点击查看您的 Streamlit 看板](https://share.streamlit.io/)
        """,
      "contentType": 2,  # 2 代表 Markdown 格式
      "uids": [user_uid],
  }

  try:
    res = requests.post(url, json=payload)
    print("📲 WxPusher 推送响应:", res.json())
  except Exception as e:
    print("❌ WxPusher 推送失败:", e)


def check_and_filter_trades():
  print("🔍 正在检查最新的国会交易披露...")
  try:
    df = pd.read_csv(DATA_URL)

    if "member_name" in df.columns:
      filtered_df = df[df["member_name"].isin(TARGET_MEMBERS)]
      print(f"✅ 筛选成功，找到目标议员交易记录: {len(filtered_df)} 条")

      if not filtered_df.empty:
        # 获取最新的一笔交易进行推送
        latest_trade = filtered_df.iloc[0]
        send_wxpusher(
            member=latest_trade.get("member_name", "Unknown"),
            ticker=latest_trade.get("ticker", "N/A"),
            action=latest_trade.get("type", "N/A"),
            date=latest_trade.get("disclosure_date", "N/A"),
        )
    else:
      print("⚠️ 数据源中未找到 'member_name' 列。")

  except Exception as e:
    print(f"❌ 运行检查时出错: {e}")


if __name__ == "__main__":
  check_and_filter_trades()
