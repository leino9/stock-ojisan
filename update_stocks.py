# update_stocks.py
# stocks.json から銘柄リストを読み込み、Yahoo Finance から指標を取得して更新するスクリプト
import json
import yfinance as yf

# 既存の stocks.json を読み込み
with open('stocks.json', 'r', encoding='utf-8') as f:
    stocks = json.load(f)  # [{'code': '7203', 'name': 'トヨタ自動車', ...}, ...]

output = []
for s in stocks:
    code = s.get('code')
    name = s.get('name')
    symbol = f"{code}.T"
    print(f"🔄 {symbol} のデータ取得中…")
    ticker = yf.Ticker(symbol)
    info = ticker.info

    stock = {
        "name": name,
        "code": code,
        "price": info.get("previousClose"),       # 前日終値
        "per":   info.get("trailingPE"),          # PER
        "pbr":   info.get("priceToBook"),         # PBR
        "roe":   info.get("returnOnEquity"),      # ROE
        "dividendYield": info.get("dividendYield") # 配当利回り
    }
    output.append(stock)
    print(f"✅ {symbol}: データ取得完了")

# 新しいデータで stocks.json を上書き
with open('stocks.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"✨ {len(output)} 件の銘柄を書き出しました")

