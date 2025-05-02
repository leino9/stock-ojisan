#!/usr/bin/env python3
# fetch_top50.py
# 日本版Yahoo Financeの時価総額ランキングページをスクレイピングして
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
    # <a>タグのhrefに "quote/{code}.T" を含む要素をすべて取得
    links = soup.find_all('a', href=re.compile(r'quote/\d+\.T'))
    tickers = []

    for link in links:
        href = link.get('href', '')
        m = re.search(r'quote/(\d+)\.T', href)
        if not m:
            continue
        code = m.group(1)
        if code in tickers:
            continue
        tickers.append(code)
        if len(tickers) >= count:
            break

    if not tickers:
        print("⚠️ 銘柄が1件も取得できませんでした。CSSセレクタを確認してください。", file=sys.stderr)
    elif len(tickers) < count:
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
    parser.add_argument('-r', '--region', help='市場コード（互換性維持用）', default=None)
    args = parser.parse_args()

    success = fetch_top(args.count, args.output)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
