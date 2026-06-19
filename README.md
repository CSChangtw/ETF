# ETF 獲利排名榜 PWA

台灣 ETF 30 檔 + 美股 ETF 30 檔，每日自動爬取更新，部署於 GitHub Pages。

## 目錄結構

```
etf-ranking/
├── .github/workflows/update_etf.yml  ← Actions 定時任務
├── scripts/fetch_etf_data.py         ← 爬取腳本
├── index.html                        ← PWA 主頁
├── sw.js                             ← Service Worker
├── manifest.json                     ← PWA Manifest
├── icon-192.png / icon-512.png       ← 圖示
├── apple-touch-icon.png / favicon.ico
├── etf_data.json                     ← 數據（Actions 自動更新）
└── README.md
```

## 部署步驟

### Step 1：建立 Repository

```
名稱：etf-ranking（或任意名稱）
Visibility：Public
```

### Step 2：上傳所有檔案到根目錄

將本專案所有檔案直接上傳至 repository 根目錄。

### Step 3：設定 GitHub Pages

Settings → Pages → Source：
- Branch：**main**
- Folder：**`/ (root)`**
- 按 Save

網址：`https://<帳號>.github.io/<repository>/`

### Step 4：手動觸發首次更新

Actions → 📊 ETF 數據每日更新 → Run workflow

### Step 5：手機安裝 PWA

- **Android**：Chrome 右上角 → 加入主畫面
- **iOS**：Safari 分享 → 加入主畫面

## 自動更新時間

| 台灣時間 | 說明 |
|---------|------|
| 每個交易日 15:30 | 台股收盤後 |
| 每個交易日 05:30 | 美股收盤後（次日凌晨）|

## ETF 清單

**台灣（30 檔）**：0050、0056、00878、006208、00919、00929、00944、00946、00945、00891、00692、00881、00900、00915、00934、00936、00896、00893、00902、00830、0051、0052、0053、0055、00733、00850、00858、00907、00905、00888

**美股（30 檔）**：SPY、QQQ、VTI、VOO、IVV、GLD、IAU、XLK、XLF、XLE、XLV、XLI、SOXX、SMH、ARKK、TLT、HYG、AGG、EEM、EFA、VNQ、DIA、IWM、VEA、VWO、SCHD、JEPI、JEPQ、NVDL、TQQQ
