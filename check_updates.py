import os
import smtplib
from email.header import Header
from email.mime.text import MIMEText
import pandas as pd

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


def send_email(member, ticker, action, date):
  """使用 Hotmail / Outlook SMTP 发送邮件提醒"""
  mail_host = "smtp-mail.outlook.com"  # Hotmail / Outlook 官方 SMTP 服务器
  mail_port = 587  # TLS 端口

  mail_user = os.environ.get("MAIL_USER")
  mail_pass = os.environ.get("MAIL_PASS")
  receiver = os.environ.get("RECEIVER_MAIL")

  if not mail_user or not mail_pass or not receiver:
    print("⚠️ 未配置完整的邮件环境变量，跳过发送。")
    return

  # 邮件 HTML 格式正文
  content = f"""
    <h2>🏛️ 发现白名单议员最新交易!</h2>
    <ul>
        <li><b>议员</b>: {member}</li>
        <li><b>代码</b>: {ticker}</li>
        <li><b>动作</b>: {action}</li>
        <li><b>披露日期</b>: {date}</li>
    </ul>
    <p><a href="https://share.streamlit.io/">点击查看您的 Streamlit 看板</a></p>
    """

  message = MIMEText(content, "html", "utf-8")
  message["From"] = Header(f"国会监控系统 <{mail_user}>")
  message["To"] = Header(receiver)
  message["Subject"] = Header(
      f"🏛️ 国会交易提醒: {member} ({ticker})", "utf-8"
  )

  try:
    # 创建 SMTP 连接并启用 TLS 加密
    server = smtplib.SMTP(mail_host, mail_port)
    server.starttls()  # 启动 TLS 安全传输
    server.login(mail_user, mail_pass)
    server.sendmail(mail_user, [receiver], message.as_string())
    server.quit()
    print("📧 Hotmail 邮件提醒发送成功！")
  except Exception as e:
    print("❌ 邮件发送失败:", e)


def check_and_filter_trades():
  print("🔍 正在检查最新的国会交易披露...")
  try:
    df = pd.read_csv(DATA_URL)

    if "member_name" in df.columns:
      filtered_df = df[df["member_name"].isin(TARGET_MEMBERS)]
      print(f"✅ 筛选成功，找到目标议员交易记录: {len(filtered_df)} 条")

      if not filtered_df.empty:
        latest_trade = filtered_df.iloc[0]
        send_email(
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
