import yfinance as yf
import json
time

# プライム市場上位50社（ティッカーコード）
tickers = [
    "7203.T", "6758.T", "9984.T", "6861.T", "8306.T", "7974.T", "9432.T", "8035.T", "4063.T", "6098.T",
    "6367.T", "2914.T", "9020.T", "9433.T", "8411.T", "9434.T", "4502.T", "5108.T", "9501.T", "7267.T",
    "3382.T", "9983.T", "6954.T", "9503.T", "8001.T", "7201.T", "8725.T", "6869.T", "4543.T", "4452.T",
    "7751.T", "6301.T", "3402.T", "8031.T", "8591.T", "7182.T", "4661.T", "2503.T", "9101.T", "5706.T",
    "6770.T", "6095.T", "6971.T", "6501.T", "2768.T", "4324.T", "2502.T", "2802.T", "6981.T", "4503.T"
]

output = []
for symbol in tickers:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        name = info.get('longName', '不明')
        code = symbol.replace('.T', '')
        prev_close = info.get('previousClose', 0)
        level = round(prev_close)

        attack = round(info.get('trailingPE', 0), 1) if info.get('trailingPE') else 0
        defense = round(info.get('priceToBook', 0), 1) if info.get('priceToBook') else 0
        hp = round(info.get('returnOnEquity', 0) * 100, 1) if info.get('returnOnEquity') else 0
        dividend_yield = round(info.get('dividendYield', 0) * 100, 1) if info.get('dividendYield') else 0

        output.append({
            'name': name,
            'code': code,
            'prevClose': prev_close,
            'attack': attack,
            'defense': defense,
            'hp': hp,
            'dividendYield': dividend_yield
        })
        time.sleep(0.5)
    except Exception as e:
        print(f"❌ {symbol} エラー: {e}")

with open('stocks.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f"✅ {len(output)} 件の銘柄を書き出しました")
