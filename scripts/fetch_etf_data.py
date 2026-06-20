#!/usr/bin/env python3
"""
ETF 獲利排名數據爬取腳本
台股 ETF 全部（83 檔）+ 其他交易活絡 ETF 30 檔
輸出：etf_data.json
"""

import argparse, json, sys, pathlib
from datetime import datetime

try:
    import yfinance as yf
    import pandas as pd
except ImportError:
    print("pip install yfinance pandas"); sys.exit(1)

# ══════════════════════════════════════════════════════════
#  台股 ETF 全部 83 檔（2026-06 etfinfo.tw）
# ══════════════════════════════════════════════════════════
TW_ETF = [
    # 主動式股票 ETF
    ("00400A", "國泰動能高息"),
    ("00401A", "摩根台灣鑫收"),
    ("00403A", "統一升級50"),
    ("00404A", "聯博動能50"),
    ("00405A", "富邦台灣龍耀"),
    ("00406A", "中信台灣收益"),
    ("00981A", "統一台股增長"),
    ("00982A", "凱基台灣優選"),
    ("00983A", "群益台灣核心"),
    ("00984A", "元大台灣成長"),
    ("00985A", "永豐台灣優質"),
    ("00986A", "富邦台灣精選"),
    ("00987A", "台新優勢成長"),
    ("00988A", "國泰台灣芯"),
    ("00989A", "中信台灣尖牙"),
    ("00990A", "兆豐台灣優息"),
    ("00991A", "日盛台灣動能"),
    ("00992A", "群益台灣新動能"),
    ("009816","凱基台灣TOP50"),
    # 寬基指數
    ("0050",  "元大台灣50"),
    ("0051",  "元大中型100"),
    ("0052",  "富邦科技"),
    ("0053",  "元大電子"),
    ("0055",  "元大MSCI金融"),
    ("006201","元大富櫃50"),
    ("006208","富邦台50"),
    ("00733", "富邦台灣中小"),
    ("00850", "元大臺灣ESG永續"),
    ("00905", "FT臺灣Smart"),
    # 高股息
    ("0056",  "元大高股息"),
    ("00692", "富邦公司治理"),
    ("00701", "國泰股利精選30"),
    ("00730", "富邦臺灣優質高息"),
    ("00878", "國泰永續高股息"),
    ("00900", "富邦特選高股息30"),
    ("00907", "永豐優息存股"),
    ("00915", "凱基優選高股息30"),
    ("00919", "群益台灣精選高息"),
    ("00929", "復華台灣科技優息"),
    ("00934", "中信成長高股息"),
    ("00936", "台新永續高息中小"),
    ("00940", "元大台灣價值高息"),
    ("00943", "兆豐電子高息等權"),
    ("009802","富邦旗艦50"),
    # 科技/半導體/AI
    ("00830", "國泰費城半導體"),
    ("00881", "國泰台灣5G+"),
    ("00891", "中信關鍵半導體"),
    ("00893", "國泰智能電動車"),
    ("00896", "中信綠能及電動車"),
    ("00902", "中信電池及儲能"),
    ("00904", "新光台灣半導體30"),
    ("00913", "兆豐台灣晶圓製造"),
    ("00928", "中信上櫃ESG30"),
    ("00939", "統一台灣高息動能"),
    ("00944", "群益半導體收益"),
    ("00945", "國泰AI+Robo"),
    ("00946", "元大AI晶片半導體"),
    ("00947", "台新臺灣IC設計動能"),
    # ESG/主題
    ("00858", "永豐台灣ESG低碳"),
    ("00888", "永豐台灣ESG"),
    ("00910", "第一金太空衛星"),
    ("00916", "國泰全球品牌50"),
    ("00917", "中信特選金融"),
    ("00918", "大華優利高填息30"),
    ("00920", "富邦未來車"),
    ("00921", "兆豐台灣核心"),
    ("00922", "國泰台灣領袖50"),
    ("00923", "群益台ESG低碳50"),
    ("00924", "群益台灣工業菁英"),
    ("00925", "元大台灣高息低波"),
    ("00926", "凱基台灣IA"),
    ("00927", "永豐ESG低碳高息"),
    ("00930", "永豐台灣ESG優質"),
    ("00931", "永豐優質高息成長"),
    ("00932", "兆豐永續高息等權"),
    ("00933", "國泰數位支付服務"),
    ("00935", "野村臺灣創新科技50"),
    ("00938", "永豐ESG高息成長"),
    ("00942", "台新台灣永續金融"),
    ("00948", "元大台灣半導體AI"),
]

# ══════════════════════════════════════════════════════════
#  其他型交易活絡 ETF 30 檔（海外股票/債券/商品/槓桿）
# ══════════════════════════════════════════════════════════
OTHER_ETF = [
    # 美股指數
    ("00646", "元大S&P500"),
    ("00757", "統一FANG+"),
    ("00662", "富邦NASDAQ"),
    ("00670L","富邦NASDAQ正2"),
    ("00631L","元大台灣50正2"),
    ("00632R","元大台灣50反1"),
    ("006205","富邦上証180"),
    # 黃金/商品
    ("00635U","元大S&P黃金"),
    ("00682U","富邦石油"),
    ("00699U","街口S&P黃豆"),
    # 債券（成交量前20）
    ("00679B","元大美債20年"),
    ("00720B","元大投資級公司債"),
    ("00724B","群益投資級金融債"),
    ("00725B","國泰投資級公司債"),
    ("00751B","元大AAA至A公司債"),
    ("00761B","元大美債7-10"),
    ("00764B","群益25年美債"),
    ("00772B","中信高評等公司債"),
    ("00779B","凱基優選債15+"),
    ("00793B","富邦美債20年"),
    ("00795B","新光投等債15+"),
    ("00796B","元大10年IG債"),
    ("00799B","群益15年IG科技債"),
    ("00849B","國泰20年美債"),
    ("00864B","中信優先金融債"),
    ("00869B","元大投資級科技債"),
    ("00870B","統一美債1到3"),
    ("00876B","中信美國公債20年"),
    ("00933B","國泰20年美債月配"),
    ("00696B","富邦美國政府債1-3"),
]

# ══════════════════════════════════════════════════════════
#  報酬率計算
# ══════════════════════════════════════════════════════════
def calc_ret(s, n):
    if len(s) < n+1: return None
    o, v = float(s.iloc[-(n+1)]), float(s.iloc[-1])
    return round((v-o)/o*100, 2) if o>0 else None

def calc_ytd(s, idx):
    y = datetime.now().year
    prev = s[idx.year == y-1]
    if prev.empty: return None
    o, v = float(prev.iloc[-1]), float(s.iloc[-1])
    return round((v-o)/o*100, 2) if o>0 else None

def fetch_one(sym_raw, name, market):
    sym = sym_raw + ".TW"
    try:
        hist = yf.Ticker(sym).history(period="2y")
        if hist.empty or len(hist) < 5: return None
        c = hist["Close"]; idx = hist.index
        last = idx[-1]
        date_str = str(last.date()) if hasattr(last,'date') else str(last)[:10]
        return {
            "symbol":    sym_raw,
            "name":      name,
            "price":     round(float(c.iloc[-1]), 2),
            "market":    market,
            "ret_1d":    calc_ret(c, 1),
            "ret_1w":    calc_ret(c, 5),
            "ret_1m":    calc_ret(c, 21),
            "ret_3m":    calc_ret(c, 63),
            "ret_1y":    calc_ret(c, 252),
            "ret_ytd":   calc_ytd(c, idx),
            "volume":    int(hist["Volume"].iloc[-1]),
            "data_date": date_str,
        }
    except Exception as e:
        print(f"  ✗ {sym}: {e}", file=sys.stderr)
        return None

def fetch_batch(etf_list, market):
    results, failed = [], []
    for i, (sym, name) in enumerate(etf_list, 1):
        print(f"  [{i:3d}/{len(etf_list)}] {sym:8s} {name} ...", end=" ", flush=True)
        d = fetch_one(sym, name, market)
        if d: results.append(d); print("✓")
        else: failed.append(sym)
    return results, failed

# ══════════════════════════════════════════════════════════
#  主程式
# ══════════════════════════════════════════════════════════
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="etf_data.json")
    args = ap.parse_args()

    print(f"\n{'='*56}")
    print(f" ETF 數據爬取  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f" 台股 {len(TW_ETF)} 檔 + 其他型 {len(OTHER_ETF)} 檔")
    print(f"{'='*56}\n")

    all_results, all_failed = [], []

    print(f"📊 台股 ETF（{len(TW_ETF)} 檔）")
    r, f = fetch_batch(TW_ETF, "TW")
    all_results += r; all_failed += f

    print(f"\n📊 其他型交易活絡 ETF（{len(OTHER_ETF)} 檔）")
    r, f = fetch_batch(OTHER_ETF, "OTHER")
    all_results += r; all_failed += f

    out = {
        "generated_at":    datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_at_tw": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "count":           len(all_results),
        "use_fallback":    len(all_results) == 0,
        "failed_symbols":  all_failed,
        "etfs":            all_results,
    }
    pathlib.Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 成功 {len(all_results)} 檔，失敗 {len(all_failed)} 檔")
    if all_failed:
        print(f"   失敗：{', '.join(all_failed)}")
    print(f"📄 輸出：{args.output}\n")
    if len(all_results) < 10: sys.exit(1)

if __name__ == "__main__":
    main()
