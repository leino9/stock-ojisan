#!/usr/bin/env python3
# update_stocks.py
# top50.json から銘柄リストを読み込み、Yahoo Finance から各種指標を取得して stocks.json を更新するスクリプト

import json
import time
import yfinance as yf
import argparse
import sys

TOP_FILE = 'top50.json'
OUTPUT_FILE = 'stocks.json'
SLEEP_SEC = 1


def update_stocks(top_file, output_file, sleep_sec):
    """
    top_file に記載されたティッカー一覧からデータを取得し、output_file に書き出す
    :param top_file: 銘柄リストJSON (例: ['7203.T', ...])
    :param output_file: 出力先 stocks.json
    :param sleep_sec: 取得間インターバル(秒)
    :return: True/False
    """
    # ティッカー一覧読み込み
    try:
        with open(top_file, 'r', encoding='utf-8') as f:
            tickers = json.load(f)
    except Exception as e:
        print(f"銘柄リストの読み込みに失敗: {e}", file=sys.stderr)
        return False

    updated = []
    for symbol in tickers:
        # Yahoo の形式に合わせる
        if not symbol.upper().endswith('.T'):
            symbol_t = symbol.upper() + '.T'
        else:
            symbol_t = symbol.upper()
        code = symbol_t.replace('.T', '')
        print(f"🔄 {symbol_t} のデータ取得中…")

        try:
            ticker = yf.Ticker(symbol_t)
            info = ticker.info
        except Exception as e:
            print(f"⚠️ {symbol_t} の取得エラー: {e}", file=sys.stderr)
            time.sleep(sleep_sec)
            continue

        # 指標を抽出
        record = {
            'code': code,
            'name': info.get('shortName', ''),
            'price': info.get('previousClose'),
            'per': info.get('trailingPE'),
            'pbr': info.get('priceToBook'),
            'roe': info.get('returnOnEquity'),
            'dividendYield': info.get('dividendYield')
        }
        updated.append(record)
        print(f"✅ {symbol_t} の更新完了")
        time.sleep(sleep_sec)

    # JSON に書き出し
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(updated, f, ensure_ascii=False, indent=2)
        print(f"✨ {len(updated)} 件の銘柄を '{output_file}' に書き出しました")
        return True
    except Exception as e:
        print(f"出力ファイル書き込みエラー: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description='top50.json から指標を取得し stocks.json を更新')
    parser.add_argument('--top', '-t', default=TOP_FILE, help=f"入力銘柄リスト (デフォルト: {TOP_FILE})")
    parser.add_argument('--output', '-o', default=OUTPUT_FILE, help=f"出力ファイル (デフォルト: {OUTPUT_FILE})")
    parser.add_argument('--sleep', '-s', type=float, default=SLEEP_SEC, help='取得間インターバル秒数')
    args = parser.parse_args()

    success = update_stocks(args.top, args.output, args.sleep)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
