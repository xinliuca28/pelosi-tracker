from datetime import datetime
import json
import os
import pandas as pd
import requests

def update_congress_dynamically():
    print("Fetching real trade history from public open-source disclosures...")
    
    # 采用开源社区长期维护、结构稳定的公开 JSON 数据源（聚合自美国众议院与参议院公开披露文件）
    url = "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            raw_data = response.json()
            print(f"Successfully fetched {len(raw_data)} raw records from public disclosures.")
        else:
            print(f"Failed to fetch data, status code: {response.status_code}")
            return
    except Exception as e:
        print(f"Exception occurred while fetching data: {e}")
        return

    # 将其转换为 DataFrame 以便进行便捷的数据清洗与聚合
    df = pd.DataFrame(raw_data)
    
    # 预处理字段，适配你的应用展示结构
    # 通常原始数据包含字段如: representative, transaction_date, disclosure_date, ticker, type, amount, asset_description 等
    congress_export = {}
    
    # 按议员分组整理
    # 如果原始字段名略有不同，可根据实际返回调整（此处以 standard house-stock-watcher 字段为准）
    grouped = df.groupby("representative")
    
    for member_name, group in grouped:
        formatted_trades = []
        dynamic_holdings_map = {}
        
        for _, row in group.iterrows():
            # 格式化买卖行为标签
            tx_type = str(row.get("type", "")).capitalize()
            if "Purchase" in tx_type or "Buy" in tx_type:
                action = "🟢 Purchase"
            elif "Sale" in tx_type or "Sell" in tx_type:
                action = "🔴 Sale"
            else:
                action = f"⚪ {tx_type}"
                
            ticker = row.get("ticker", "N/A")
            if not ticker or ticker == "":
                ticker = "OTHER"
                
            trade_date = row.get("transaction_date", "")
            filing_date = row.get("disclosure_date", "")
            amount_range = row.get("amount", "$1,001 - $15,000")
            
            formatted_trades.append({
                "Filing Date": filing_date,
                "Trade Date": trade_date,
                "Ticker": ticker,
                "Action": action,
                "Asset Class": row.get("asset_type", "Common Stock"),
                "Description": row.get("asset_description", f"Disclosed {ticker} transaction"),
                "Disclosed Range": amount_range,
                "midpoint_val": 15000, # 可根据实际区间进行更精细的解析
                "underlying_shares": 0,
            })
            
            # 简易汇总生成当前持仓参考
            if ticker != "OTHER":
                if ticker not in dynamic_holdings_map:
                    dynamic_holdings_map[ticker] = {
                        "Ticker": ticker,
                        "Company": row.get("asset_description", ticker),
                        "Est. Cost Basis ($)": 100.0,
                        "Est. Value ($10k)": 100,
                        "Est. Allocation (%)": 0.0,
                    }

        # 转换为列表
        dynamic_holdings = list(dynamic_holdings_map.values())
        
        # 简单均分持仓占比
        if dynamic_holdings:
            alloc = round(100.0 / len(dynamic_holdings), 2)
            for item in dynamic_holdings:
                item["Est. Allocation (%)"] = alloc

        congress_export[member_name] = {
            "holdings": dynamic_holdings,
            "trades": formatted_trades,
        }

    os.makedirs("data", exist_ok=True)
    with open("data/congress_data.json", "w", encoding="utf-8") as f:
        json.dump(congress_export, f, indent=4, ensure_ascii=False)
        
    print("Successfully generated live-synced congress_data.json with real public records.")

if __name__ == "__main__":
    update_congress_dynamically()
