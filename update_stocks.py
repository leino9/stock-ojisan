#!/usr/bin/env python3
# update_stocks.py
# top50.json から銘柄リストを読み込み、Yahoo Finance から各種指標を取得して stocks.json を更新するスクリプト

import json
import time
import sys
import argparse
import math
import yfinance as yf

TOP_FILE = 'top50.json'
OUTPUT_FILE = 'stocks.json'
SLEEP_SEC = 1


def clean_val(val):
    """None や NaN を JSON に書き込める形式に変換"""
    if val is None:
        return None
    try:
        if isinstance(val, float) and math.isnan(val):
            return None
    except Exception:
        pass
    return val


def update_stocks(top_file, output_file, sleep_sec):
    # ティッカー一覧読み込み
    try:
        with open(top_file, 'r', encoding='utf-8') as f:
            tickers_objs = json.load(f)
    except Exception as e:
        print(f"銘柄リストの読み込みに失敗: {e}", file=sys.stderr)
        return False

    results = []
    for obj in tickers:
        symbol = obj['code']
        name_jp = obj.get('name_jp')
        
        # 「7203」→「7203.T」に整形
        symbol_t = symbol + '.T'
        code = symbol
        
        print(f"🔄 {symbol_t} のデータ取得中…")

        price = None
        per = None
        pbr = None
        roe = None
        div_yield = None
        name = name_jp or symbol

        try:
            ticker = yf.Ticker(symbol_t)
            # まず簡易に終値を history で取得
            hist = ticker.history(period='2d')
            if not hist.empty:
                # 直近2日分の終値があれば前日分
                price = float(hist['Close'].iloc[-2]) if len(hist) >= 2 else float(hist['Close'].iloc[0])
            # 次に info で他指標を取得
            info = ticker.info
            name = info.get('shortName') or info.get('longName')
            per = info.get('trailingPE')
            pbr = info.get('priceToBook')
            roe = info.get('returnOnEquity')
            div_yield = info.get('dividendYield')
        except Exception as e:
            # 404や一時的エラーはスキップ
            print(f"⚠️ {symbol_t} の取得エラー: {e}", file=sys.stderr)
        finally:
            time.sleep(sleep_sec)

        record = {
            'code': code,
            'name': name,
            'price': clean_val(price),
            'per': clean_val(per),
            'pbr': clean_val(pbr),
            'roe': clean_val(roe),
            'dividendYield': clean_val(div_yield)
        }
        results.append(record)
        print(f"✅ {symbol_t} の処理完了")

    # JSON 出力
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"✨ {len(results)} 件の銘柄を '{output_file}' に書き出しました")
        return True
    except Exception as e:
        print(f"出力ファイル書き込みエラー: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description='top50.json から指標を取得し stocks.json を更新')
    parser.add_argument('--top', '-t', default=TOP_FILE, help='入力銘柄リスト (デフォルト: top50.json)')
    parser.add_argument('--output', '-o', default=OUTPUT_FILE, help='出力ファイル (デフォルト: stocks.json)')
    parser.add_argument('--sleep', '-s', type=float, default=SLEEP_SEC, help='取得間インターバル秒数')
    args = parser.parse_args()

    success = update_stocks(args.top, args.output, args.sleep)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
