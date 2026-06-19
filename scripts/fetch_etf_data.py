#!/usr/bin/env python3
"""
ETF 獲利排名數據爬取腳本
台灣 ETF 30 檔 + 美股 ETF 30 檔
輸出：docs/etf_data.json（供 PWA 靜態讀取）
"""

import argparse
import json
import sys
from datetime import datetime

try:
    import yfinance as yf
    import pandas as pd
except ImportError:
    print("pip install yfinance pandas")
    sys.exit(1)

# ── 台灣 ETF 30 檔 ────────────────────────────────────────────────────
TW_ETF_LIST = [
    ("0050.TW",   "元大台灣50"),
    ("0056.TW",   "元大高股息"),
    ("00878.TW",  "國泰永續高股息"),
    ("006208.TW", "富邦台50"),
    ("00919.TW",  "群益台灣精選高息"),
    ("00929.TW",  "復華台灣科技優息"),
    ("00944.TW",  "群益半導體收益"),
    ("00946.TW",  "元大AI晶片半導體"),
    ("00945.TW",  "國泰AI+Robo"),
    ("00891.TW",  "中信關鍵半導體"),
    ("00692.TW",  "富邦公司治理"),
    ("00881.TW",  "國泰台灣5G+"),
    ("00900.TW",  "富邦特選高股息30"),
    ("00915.TW",  "凱基優選高股息30"),
    ("00934.TW",  "中信成長高股息"),
    ("00936.TW",  "台新臺灣永續高息"),
    ("00896.TW",  "中信綠能及電動車"),
    ("00893.TW",  "國泰智能電動車"),
    ("00902.TW",  "中信電池及儲能"),
    ("00830.TW",  "國泰費城半導體"),
    ("0051.TW",   "元大中型100"),
    ("0052.TW",   "富邦科技"),
    ("0053.TW",   "元大電子"),
    ("0055.TW",   "元大MSCI金融"),
    ("00733.TW",  "富邦台灣中小"),
    ("00850.TW",  "元大臺灣ESG永續"),
    ("00858.TW",  "永豐台灣ESG低碳"),
    ("00907.TW",  "永豐優息存股"),
    ("00905.TW",  "FT臺灣Smart"),
    ("00888.TW",  "永豐台灣ESG"),
]

# ── 美股 ETF 30 檔 ────────────────────────────────────────────────────
US_ETF_LIST = [
    ("SPY",  "SPDR S&P 500 ETF"),
    ("QQQ",  "Invesco Nasdaq-100 ETF"),
    ("VTI",  "Vanguard Total Stock Market ETF"),
    ("VOO",  "Vanguard S&P 500 ETF"),
    ("IVV",  "iShares Core S&P 500 ETF"),
    ("GLD",  "SPDR Gold Shares"),
    ("IAU",  "iShares Gold Trust"),
    ("XLK",  "Technology Select Sector SPDR"),
    ("XLF",  "Financial Select Sector SPDR"),
    ("XLE",  "Energy Select Sector SPDR"),
    ("XLV",  "Health Care Select Sector SPDR"),
    ("XLI",  "Industrial Select Sector SPDR"),
    ("SOXX", "iShares Semiconductor ETF"),
    ("SMH",  "VanEck Semiconductor ETF"),
    ("ARKK", "ARK Innovation ETF"),
    ("TLT",  "iShares 20+ Year Treasury Bond ETF"),
    ("HYG",  "iShares iBoxx High Yield Corp Bond ETF"),
    ("AGG",  "iShares Core US Aggregate Bond ETF"),
    ("EEM",  "iShares MSCI Emerging Markets ETF"),
    ("EFA",  "iShares MSCI EAFE ETF"),
    ("VNQ",  "Vanguard Real Estate ETF"),
    ("DIA",  "SPDR Dow Jones Industrial Average ETF"),
    ("IWM",  "iShares Russell 2000 ETF"),
    ("VEA",  "Vanguard Developed Markets ETF"),
    ("VWO",  "Vanguard Emerging Markets ETF"),
    ("SCHD", "Schwab US Dividend Equity ETF"),
    ("JEPI", "JPMorgan Equity Premium Income ETF"),
    ("JEPQ", "JPMorgan Nasdaq Equity Premium Income ETF"),
    ("NVDL", "GraniteShares 2x Long NVIDIA ETF"),
    ("TQQQ", "ProShares UltraPro QQQ 3x ETF"),
]

# ── 備援靜態數據（Actions 失敗時保留舊檔，此函式不會被呼叫）──────────
FALLBACK = []   # 空陣列 → Actions 失敗時保留上次 commit 的 etf_data.json

# ── 工具函數 ──────────────────────────────────────────────────────────
def calc_ret(series, n):
    if len(series) < n + 1:
        return None
    old, new = float(series.iloc[-(n+1)]), float(series.iloc[-1])
    return round((new - old) / old * 100, 2) if old > 0 else None

def calc_ytd(series, index):
    this_year = datetime.now().year
    prev = series[index.year == this_year - 1]
    if prev.empty:
        return None
    old, new = float(prev.iloc[-1]), float(series.iloc[-1])
    return round((new - old) / old * 100, 2) if old > 0 else None

def fetch_one(symbol, name):
    try:
        hist = yf.Ticker(symbol).history(period="2y")
        if hist.empty or len(hist) < 5:
            return None
        close = hist["Close"]
        idx   = hist.index
        last  = idx[-1]
        date_str = str(last.date()) if hasattr(last, 'date') else str(last)[:10]
        return {
            "symbol":    symbol.replace(".TW", ""),
            "name":      name,
            "price":     round(float(close.iloc[-1]), 2),
            "ret_1d":    calc_ret(close, 1),
            "ret_1w":    calc_ret(close, 5),
            "ret_1m":    calc_ret(close, 21),
            "ret_3m":    calc_ret(close, 63),
            "ret_1y":    calc_ret(close, 252),
            "ret_ytd":   calc_ytd(close, idx),
            "volume":    int(hist["Volume"].iloc[-1]),
            "data_date": date_str,
        }
    except Exception as e:
        print(f"  ✗ {symbol}: {e}", file=sys.stderr)
        return None

def fetch_all(etf_list, market_label):
    results, failed = [], []
    for i, (sym, name) in enumerate(etf_list, 1):
        print(f"  [{i:2d}/{len(etf_list)}] {sym} …", end=" ", flush=True)
        d = fetch_one(sym, name)
        if d:
            d["market"] = market_label
            results.append(d)
            print("✓")
        else:
            failed.append(sym)
    return results, failed

# ── 主程式 ────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="etf_data.json")
    args = ap.parse_args()

    print(f"\n{'='*52}")
    print(f" ETF 數據爬取  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*52}\n")

    all_results, all_failed = [], []

    print("📊 台灣 ETF（30 檔）")
    r, f = fetch_all(TW_ETF_LIST, "TW")
    all_results += r; all_failed += f

    print("\n📊 美股 ETF（30 檔）")
    r, f = fetch_all(US_ETF_LIST, "US")
    all_results += r; all_failed += f

    out = {
        "generated_at":   datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_at_tw": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "count":          len(all_results),
        "use_fallback":   len(all_results) == 0,
        "failed_symbols": all_failed,
        "etfs":           all_results,
    }

    import pathlib
    pathlib.Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 成功：{len(all_results)} 檔，失敗：{len(all_failed)} 檔")
    if all_failed:
        print(f"   失敗清單：{', '.join(all_failed)}")
    print(f"📄 輸出：{args.output}\n")

    # Actions 中若全部失敗則 exit 1，讓 workflow 標記失敗但不 push 壞數據
    if len(all_results) < 5:
        sys.exit(1)

if __name__ == "__main__":
    main()
  
