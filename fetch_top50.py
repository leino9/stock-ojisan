#!/usr/bin/env python3
# fetch_top50.py
# 毎日、Yahoo Finance 日本版の時価総額ランキングページをスクレイピングして
# 上位 count 件の銘柄コードを取得し top50.json に保存するスクリプト

import requests
import json
import sys
import argparse
import re
from bs4 import BeautifulSoup

DEFAULT_COUNT = 50
DEFAULT_OUTPUT = 'top50.json'
HEADERS = {'User-Agent': 'Mozilla/5.0'}


def fetch_top(count, output):
    """
    日本版Yahoo Financeの時価総額ランキングから上位count件の銘柄コードを抽出し保存
    """
    url = 'https://finance.yahoo.co.jp/stocks/ranking/marketCapitalHigh'
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"通信エラー: {e}", file=sys.stderr)
        return False

    soup = BeautifulSoup(resp.text, 'html.parser')
    # quoteリンクからコード抽出
    links = soup.select('a[href*="/quote/"]')
    tickers = []
    for link in links:
        href = link.get('href', '')
        m = re.search(r"/quote/(\d+)\.T", href)
        if not m:
            continue
        code = m.group(1)
        if code not in tickers:
            tickers.append(code)
        if len(tickers) >= count:
            break

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
    parser = argparse.ArgumentParser(description='日本版Yahoo Financeから時価総額TOP銘柄を取得')
    parser.add_argument('-c', '--count', type=int, default=DEFAULT_COUNT, help='取得件数')
    parser.add_argument('-o', '--output', default=DEFAULT_OUTPUT, help='出力ファイル')
    # 互換性維持用に --region オプションを追加（未使用）
    parser.add_argument('-r', '--region', help='(未使用) 市場コードを指定', default=None)
    args = parser.parse_args()()

    success = fetch_top(args.count, args.output)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
