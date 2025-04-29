# update_stocks.py
# 日本株の前日終値、PER、PBR、ROE、配当利回りを取得して stocks.json に書き出す
import json
import yfinance as yf

# 対象銘柄辞書（キーは Yahoo Finance のティッカーシンボル）
tickers = {
    "7974.T": "任天堂（7974）",
    "7203.T": "トヨタ自動車（7203）",
    "6758.T": "ソニーグループ（6758）",
    "8058.T": "三菱商事（8058）",
    # …他のプライム50銘柄を同様に追加
}

output = []
for symbol, name in tickers.items():
    print(f"🔄 {symbol} のデータ取得中…")
    ticker = yf.Ticker(symbol)
    info = ticker.info

    stock = {
        "name": name,
        "code": symbol.replace(".T", ""),
        "price": info.get("previousClose"),       # 前日終値
        "per":   info.get("trailingPE"),          # PER
        "pbr":   info.get("priceToBook"),         # PBR
        "roe":   info.get("returnOnEquity"),      # ROE
        "dividendYield": info.get("dividendYield")  # 配当利回り
    }
    output.append(stock)
    print(f"✅ {symbol}: データ取得完了")

with open("stocks.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"✨ {len(output)} 件の銘柄を書き出しました")

