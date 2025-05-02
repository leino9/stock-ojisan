#!/usr/bin/env python3
# fetch_top50.py
# 毎日、Yahoo Finance の大型株スクリーナーから
# 時価総額上位銘柄を取得して JSON に保存するスクリプト

import requests
import json
import argparse
import sys

API_URL = 'https://query2.finance.yahoo.com/v1/finance/screener'
HEADERS = {'User-Agent': 'Mozilla/5.0'}
DEFAULT_COUNT = 50
DEFAULT_OUTPUT = 'top50.json'
DEFAULT_REGION = 'JP'  # 日本市場


def fetch_top(count, output, region):
    """
    指定件数の時価総額上位銘柄を取得し、JSONファイルに書き出す
    :param count: 取得件数
    :param output: 出力ファイルパス
    :param region: 市場コード (例: 'JP' or 'US')
    :return: 成功時 True, 失敗時 False
    """
    params = {
        'formatted': 'true',
        'lang': 'ja-JP',
        'region': region,
        'scrIds': 'large_cap',
        'count': str(count),
        'start': '0'
    }
    try:
        resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"通信エラー: {e}", file=sys.stderr)
        return False
    except ValueError:
        print("JSONの解析に失敗しました", file=sys.stderr)
        return False

    quotes = data.get('finance', {}).get('result', [{}])[0].get('quotes', [])
    tickers = [q.get('symbol') for q in quotes if 'symbol' in q]

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
        description="Yahoo Financeから時価総額上位銘柄を取得してJSON保存する"
    )
    parser.add_argument(
        '--count', '-c', type=int, default=DEFAULT_COUNT,
        help=f"取得件数 (デフォルト: {DEFAULT_COUNT})"
    )
    parser.add_argument(
        '--output', '-o', default=DEFAULT_OUTPUT,
        help=f"出力ファイル (デフォルト: {DEFAULT_OUTPUT})"
    )
    parser.add_argument(
        '--region', '-r', default=DEFAULT_REGION,
        help=f"市場コード (デフォルト: {DEFAULT_REGION})"
    )
    args = parser.parse_args()

    success = fetch_top(args.count, args.output, args.region)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
