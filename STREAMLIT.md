# Streamlit 完整版操作說明

Windows 可雙擊 start-streamlit.cmd；免安裝版請開啟 index.html。

## 安裝與執行

建議安裝 Python 3.11 或更新版本，解壓縮後在本資料夾開啟終端機。

Windows PowerShell：

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

macOS / Linux：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1
```

瀏覽器開啟 http://localhost:8501。停止服務請在終端機按 Ctrl+C。

## 操作

1. 在左側填案件名稱、客戶、數量及共用尺寸（mm）。尺寸供壓鑄、拋光、表面處理共同使用。
2. 原料可用重量、公斤價與損耗率計算，也可改用手動費用；損耗率填 `5` 代表 5%。公式為 `(重量 / 1000) × 公斤價 × (1 + 損耗率 / 100)`。
3. 壓鑄預設手動輸入。切換基準表時，可修改示範數字為內部核定標準並勾選確認。規則以三邊最大值配對最小適用上限，穴數必須完全相同。費率已是每件價格，不再除以穴數。找不到符合規則時必須改用手動費用。
4. 加工、拋光、表面處理選擇種類或等級，並手動輸入每件費用。沒有公司標準時不推測價格；下拉選單只記錄製程。無此製程請選「不適用／不計費」。
5. 在其他費用表格底部新增包裝、檢驗等項目，選取列可刪除。每列包含名稱及每件金額，整批運費須先除以數量。輸入後按 Enter 或移出欄位觸發更新。
6. 查看六類費用、佔比、每件總價及整批總價。所有必要費用填妥後，點「匯出報價明細 (CSV)」。檔案包含案件資料、使用中的參數、基準表、其他費用逐筆明細、六類彙總、佔比與總額。

## 計價約定

- 全部以新臺幣、每件成本計算；報價數量僅影響整批合計，不自動套用數量折扣。
- 每項費用四捨五入至小數第 2 位後加總，採 Decimal 避免二進位浮點累加誤差。零總額時佔比為 0%。
- 空白費用不等於 0 元。未填完僅顯示已填小計，停用 CSV 匯出；確認免費可明確填 0。
- 初步報價不含稅、利潤與未列入的模具費。所需費用可自行攤提後加入其他項目。
- 壓鑄數字僅為示範，不代表真實供應商費率；正式使用前請以公司標準替換 app.py 內的預設表。表格編輯只在目前工作階段生效。
- CSV 使用 UTF-8 BOM，方便 Excel 顯示繁體中文；文字開頭的公式符號會加單引號，避免被試算表當成公式執行。
- 資料未儲存至資料庫。頁面重新載入、工作階段中斷可能清除輸入，請及時匯出；CSV 不提供重新匯入功能。

## 程式結構與驗證

- `app.py`：Streamlit 介面、輸入狀態、彙總、下載。
- `costing.py`：原料公式、壓鑄查表、Decimal 金額與 CSV 編碼。
- `test_costing.py`：公式、級距、零值、四捨五入及 CSV 測試。
- `requirements.txt`：所需套件。

執行測試：`.\.venv\Scripts\python.exe -m unittest -v`。

Streamlit 官方文件：
- https://docs.streamlit.io/develop/api-reference/data/st.data_editor
- https://docs.streamlit.io/develop/api-reference/widgets/st.download_button

