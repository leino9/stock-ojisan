#!/usr/bin/env python3
# fetch_top50.py
# 毎日、Yahoo Finance 日本版の時価総額ランキングページをスクレイピングして
# 上位 count 件の銘柄コードを取得し top50.json に保存するスクリプト

import requests
import json
import sys
import argparse
import urllib.parse
from bs4 import BeautifulSoup

DEFAULT_COUNT = 50
DEFAULT_OUTPUT = 'top50.json'
HEADERS = {'User-Agent': 'Mozilla/5.0'}


def fetch_top(count, output):
    """
    Yahoo Finance 日本版の時価総額ランキングページから
    上位 count 件の銘柄コードを取得し、output ファイルに保存する
    """
    url = 'https://finance.yahoo.co.jp/stocks/ranking/marketCapitalHigh'
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"通信エラー: {e}", file=sys.stderr)
        return False

    soup = BeautifulSoup(resp.text, 'html.parser')
    # 銘柄詳細へのリンクをすべて取得
    # 各行のTRから直接解析
    rows = soup.select('tr[class^="RankingTable__row"]')
    tickers = []
    for row in rows:
        # 補足リスト内の li 要素にコードが入っている
        li = row.select_one('li.RankingTable__supplement__vv_m')
        if not li or not li.text.strip().isdigit():
            continue
        code = li.text.strip()
        tickers.append(code)
        if len(tickers) >= count:
            break
    tickers = []
    for link in links:
        href = link.get('href', '')
        # URLからクエリパラメータ code を抽出
        try:
            qs = urllib.parse.urlparse(href).query
            params = urllib.parse.parse_qs(qs)
            code_t = params.get('code')
            if not code_t:
                continue
            code = code_t[0].split('.')[0]
        except Exception:
            continue
        if code in tickers:
            continue
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
    parser = argparse.ArgumentParser(
        description='Yahoo Finance日本版から時価総額上位銘柄を取得'
    )
    parser.add_argument('-c', '--count', type=int, default=DEFAULT_COUNT, help='取得件数')
    parser.add_argument('-o', '--output', default=DEFAULT_OUTPUT, help='出力ファイル')
    parser.add_argument('-r', '--region', help='(未使用) 市場コードを指定', default=None)
    args = parser.parse_args()

    success = fetch_top(args.count, args.output)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
