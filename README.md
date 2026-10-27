# 鋅合金產品快速報價計算器

給鋅合金產品業務使用的初步成本報價工具，支援六類成本、即時計算與繁體中文 CSV 匯出。

## 下載即可用（推薦）

1. 點選 **[下載完整 ZIP](https://github.com/jaanshinmetal/1234_1027/archive/refs/heads/main.zip)**，或 **Code → Download ZIP**。
2. **先解壓縮整個資料夾**。
3. 雙擊 **index.html**，用 Chrome、Edge、Firefox 或 Safari 開啟。Windows 也可雙擊 **start.cmd**。

**不需要 Python、不需要安裝套件、不需要帳號；下載完成後可離線使用。** 請下載後開啟，GitHub 原始碼預覽頁不會執行程式。輸入留在目前瀏覽器頁面，CSV 存在本機；關閉或重新載入頁面會清除輸入。

## 兩個版本

| 版本 | 開啟方式 | 需求 | 壓鑄費 |
| --- | --- | --- | --- |
| 免安裝離線版 | index.html 或 start.cmd | 現代瀏覽器 | 手動輸入；尺寸與穴數作為案件紀錄 |
| Python / Streamlit 完整版 | start-streamlit.cmd | Python 3.11+；第一次安裝需連網 | 手動輸入或尺寸級距／穴數基準表 |

Streamlit 版保留完整 Python 原始碼。第一次雙擊 start-streamlit.cmd 會建立專用 .venv 並安裝套件，之後直接啟動。若未安裝 Python，可使用免安裝版，或先至 [Python 官方網站](https://www.python.org/downloads/windows/) 安裝 Python 3.11 以上。macOS / Linux 請見 [STREAMLIT.md](STREAMLIT.md)。

## 使用流程

1. 填寫案件／客戶、產品與數量。
2. 原料填每公斤價、重量與損耗率；也可手動覆寫，包含明確的 0 元。
3. 填共用尺寸、模具穴數、製程種類與每件費用。無該製程請填 0。拋光、表面處理沿用共用尺寸。
4. 新增其他費用，填名稱與每件金額，按 × 可刪除。
5. 查看六類費用、佔比、每件總價與整批金額，按「匯出報價明細（CSV）」下載。

## 計價規則

- 固定新臺幣 NT$。每件原料費 = (重量 g / 1000) × 每公斤價 × (1 + 損耗率 / 100)。
- 所有費用均為每件；整批運費須先除以數量。
- 各項先四捨五入至小數第 2 位再加總；整批金額 = 每件總額 × 數量。
- 離線版使用 BigInt 分數計算，Python 版使用 Decimal，避免浮點金額累加誤差。
- 必要費用未填或數值無效時無法匯出。總額為 0 時佔比為 0%；取位可能使佔比加總不等於 100%。
- **初步報價為成本加總，未稅、未含利潤與未列入模具費。** Streamlit 壓鑄表為示範資料，須替換成公司核定費率並確認後使用。
- CSV 包含案件、參數、費用、佔比、其他費用逐筆明細與總額；UTF-8 BOM 支援 Excel 中文。可疑公式文字加單引號保護。

## 原始碼與驗證

- index.html：無外部依賴的免安裝版，CSS 與 JavaScript 內嵌。
- app.py、costing.py：Streamlit 介面與計算邏輯。
- test_costing.py：計算及 CSV 測試，執行 python -m unittest -v。
- start.cmd：Windows 免安裝入口。
- start-streamlit.cmd：Windows Streamlit 安裝／啟動入口。
- requirements.txt：套件需求。
- 報價小工具.html、ORIGINAL_README.md 與原有 AI 提示詞／CSV：保留的原始資料，新使用者請開啟 index.html。

本工具不包含帳號管理、雲端同步或自動儲存。請及時匯出所需資料。
