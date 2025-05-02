#!/usr/bin/env python3
# fetch_top50.py
# 日本版Yahoo Financeの時価総額ランキングページをスクレイピングして
# 上位 count 件の銘柄コードと日本語社名を取得し top50.json に保存するスクリプト

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
    日本版Yahoo Financeの時価総額ランキングから上位count件の銘柄コードと日本語名称を抽出し保存
    """
    url = 'https://finance.yahoo.co.jp/stocks/ranking/marketCapitalHigh'
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"通信エラー: {e}", file=sys.stderr)
        return False

    soup = BeautifulSoup(resp.text, 'html.parser')
    rows = soup.select('tr[class^="RankingTable__row__"]')
    results = []

    for row in rows:
        # 日本語名称はリンクテキスト、コードは補足リスト内 li
        link = row.select_one('a[href*="/quote/"]')
        li = row.select_one('li.RankingTable__supplement__vv_m')
        if not link or not li:
            continue
        name_jp = link.text.strip()
        code = li.text.strip()
        if not code.isdigit():
            continue
        results.append({'code': code, 'name_jp': name_jp})
        if len(results) >= count:
            break

    if len(results) < count:
        print(f"⚠️ 取得件数が少ない: {len(results)} 件 (期待値: {count})", file=sys.stderr)

    try:
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"✔️ 取得完了: {len(results)} 件を '{output}' に保存しました")
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

