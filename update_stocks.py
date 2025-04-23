import requests
import json
import os

api_key = os.environ.get('FINNHUB_API_KEY') or 'YOUR_API_KEY_HERE'

tickers = {
    "7974.T": "任天堂（7974）",
    "7203.T": "トヨタ自動車（7203）",
    "6758.T": "ソニーG（6758）",
    "8058.T": "三菱商事（8058）",
    "9984.T": "ソフトバンクG（9984）",
    "8306.T": "三菱UFJ（8306）",
    "8035.T": "東京エレクトロン（8035）",
    "6861.T": "キーエンス（6861）",
    "4063.T": "信越化学（4063）",
    "6098.T": "リクルート（6098）"
}

output = []

for symbol, name in tickers.items():
    url = f"https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token={api_key}"
    res = requests.get(url)
    metrics = res.json().get("metric", {})

    if not metrics:
        print(f"❌ {symbol}: データ取得失敗")
        continue

    stock = {
        "name": name,
        "code": symbol.replace(".T", ""),
        "level": round(metrics.get("marketCapitalization", 0)),
        "attack": round(metrics.get("roe", 0), 1),
        "defense": round(metrics.get("currentRatio", 0), 1),  # ← 流動比率を防御力に！
        "hp": round(metrics.get("cashRatio", 0) * 100, 1)
    }

    output.append(stock)
    print(f"✅ {symbol}: OK")

with open("stocks.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"✨ {len(output)} 件の銘柄を書き出しました")