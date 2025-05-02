#!/usr/bin/env python3
# fetch_top50.py
# 毎日、Yahoo Finance の Large Cap predefined スクリーンページをスクレイピングして
# 時価総額上位銘柄を取得し top50.json に保存するスクリプト

import requests
import json
import sys
import argparse
from bs4 import BeautifulSoup

DEFAULT_COUNT = 50
DEFAULT_OUTPUT = 'top50.json'
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def fetch_top(count, output):
    """
    Yahoo Finance の Large Cap predefined スクリーンページから
    上位 count 件のティッカーを取得し、output ファイルに保存する
    """
    url = 'https://finance.yahoo.com/screener/predefined/large_cap'
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"通信エラー: {e}", file=sys.stderr)
        return False

    soup = BeautifulSoup(resp.text, 'html.parser')
    rows = soup.select('table tbody tr')
    tickers = []
    for row in rows[:count]:
        link = row.select_one('td:nth-child(1) a')
        if link and link.text:
            tickers.append(link.text.strip())

    if len(tickers) < count:
        print(f"⚠️ 取得件数が少ない: {len(tickers)} 件 (期待値: {count})", file=sys.stderr)

    try:
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(tickers, f, ensure_ascii=False, indent=2)
        print(f"✔️ 取得完了: {len(tickers)} 件を '{output}' に保存しました")
        return True
    except IOError as e:
        print(f"ファイル書き込みエラー: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Yahoo Financeから時価総額上位銘柄をスクレイピングして取得'
        python fetch_top50.py --count 50 --output top50.json --region JP

    )
    parser.add_argument(
        '-c', '--count', type=int, default=DEFAULT_COUNT,
        help='取得件数 (デフォルト: 50)'
    )
    parser.add_argument(
        '-o', '--output', default=DEFAULT_OUTPUT,
        help='出力JSONファイル名 (デフォルト: top50.json)'
    )
    args = parser.parse_args()

    success = fetch_top(args.count, args.output)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()

