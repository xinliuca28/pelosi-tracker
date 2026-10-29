import os
import pandas as pd
import requests

TARGET_MEMBERS = [
    "Nancy Pelosi",
    "Tommy Tuberville",
    "Mark Green",
    "Dan Crenshaw",
    "Josh Gottheimer",
]

DATA_URL = "https://www.capitolstockwatch.com/data/open-data/congress_trades_latest.csv"


def send_pushplus(member, ticker, action, date):
  """使用 pushplus 发送免费微信消息"""
  token = os.environ.get("PUSHPLUS_TOKEN")

  if not token:
    print("⚠️ 未检测到 PUSHPLUS_TOKEN 环境变量，跳过微信推送。")
    return

  url = "http://www.pushplus.plus/send"
  content = f"""
### 🏛️ 发现白名单议员最新交易!

* **议员**: {member}
* **代码**: {ticker}
* **动作**: {action}
* **披露日期**: {date}

[点击查看 Streamlit 看板](https://share.streamlit.io/)
    """

  payload = {
      "token": token,
      "title": f"🏛️ 国会交易提醒: {member} ({ticker})",
      "content": content,
      "template": "markdown",
  }

  try:
    res = requests.post(url, json=payload)
    print("📲 pushplus 推送响应:", res.json())
  except Exception as e:
    print("❌ pushplus 推送失败:", e)


def check_and_filter_trades():
  print("🔍 正在检查最新的国会交易披露...")
  try:
    df = pd.read_csv(DATA_URL)

    if "member_name" in df.columns:
      filtered_df = df[df["member_name"].isin(TARGET_MEMBERS)]
      print(f"✅ 筛选成功，找到目标议员交易记录: {len(filtered_df)} 条")

      if not filtered_df.empty:
        latest_trade = filtered_df.iloc[0]
        send_pushplus(
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
