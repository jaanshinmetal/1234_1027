from datetime import datetime, timezone, timedelta
from decimal import Decimal

import streamlit as st

from costing import csv_bytes, die_cost, material_cost, money, summarize

st.set_page_config(page_title="鋅合金快速報價", page_icon="⚙️", layout="wide")
st.title("鋅合金產品快速報價")
st.caption("內部初估工具 · 新臺幣 NT$ · 所有製程費用均以每件計算")
st.info("初步報價為六類成本加總，未含稅、利潤及未列入的模具費。運輸等整批費用請先除以件數，再填入每件費用。")

params = []
missing = []
details = []


def record(section, name, value, unit=""):
    params.append(["參數", section, name, value, unit])
    return value


def amount(label, key, value=None):
    return st.number_input(label, min_value=0.0, max_value=1_000_000_000.0,
                           value=value, step=0.01, format="%.2f", key=key)


def resolve(section, mode, automatic=None):
    record(section, "計價方式", mode)
    if mode == "不適用／不計費":
        return Decimal("0.00")
    if mode == "手動輸入":
        value = amount("手動費用 (NT$/件)", section + "_manual")
        record(section, "手動費用", "未填" if value is None else value, "NT$/件")
    else:
        value = automatic
    if value is None:
        missing.append(section)
        st.warning("尚未取得費用，請填寫參數或切換手動輸入。")
        return Decimal("0.00")
    result = money(value)
    st.caption(f"此製程：NT$ {result:,.2f}／件")
    return result


with st.sidebar:
    st.header("案件資料")
    project = st.text_input("案件名稱", "新產品試算")
    customer = st.text_input("客戶名稱（選填）")
    quantity = st.number_input("報價數量（件）", min_value=1, max_value=1_000_000_000, value=1000)
    st.divider()
    st.subheader("共用物件尺寸")
    st.caption("供壓鑄、拋光與表面處理使用。")
    dimensions = [st.number_input(f"{label} (mm)", min_value=0.0, max_value=100000.0,
                                 value=None, step=1.0, key=label) for label in ("長", "寬", "高")]
    for label, value in zip(("長", "寬", "高"), dimensions):
        record("共用尺寸", label, "未填" if value is None else value, "mm")
    st.caption("尺寸缺漏時仍可使用手動費用。輸入後按 Enter 或移出欄位，即會重新計算。")

left, right = st.columns(2)
with left:
    with st.container(border=True):
        st.subheader("01 原料")
        mode = st.radio("計價方式", ["公式計算", "手動輸入", "不適用／不計費"], key="raw_mode", horizontal=True)
        raw = None
        if mode == "公式計算":
            price = amount("每公斤價格 (NT$/kg)", "price")
            weight = st.number_input("成品重量 (g)", min_value=0.0, max_value=1_000_000.0, value=None, step=1.0)
            loss = st.number_input("預估損耗率 (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.5)
            for name, value, unit in [("每公斤價格", price, "NT$/kg"), ("成品重量", weight, "g"), ("損耗率", loss, "%")]:
                record("原料", name, "未填" if value is None else value, unit)
            if price is not None and weight is not None:
                raw = material_cost(weight, price, loss)
            st.caption("重量 ÷ 1000 × 每公斤價格 × (1 + 損耗率 ÷ 100)")
        raw = resolve("原料", mode, raw)

    with st.container(border=True):
        st.subheader("03 加工")
        record("加工", "種類", st.selectbox("加工種類", ["攻牙", "鑽孔", "CNC 銑削", "其他"]))
        mode = st.radio("計價方式", ["手動輸入", "不適用／不計費"], key="mach_mode", horizontal=True)
        machining = resolve("加工", mode)

    with st.container(border=True):
        st.subheader("05 表面處理")
        record("表面處理", "種類", st.selectbox("表面處理種類", ["電鍍電著", "烤漆", "陽極（須確認適用製程）", "其他"]))
        st.caption("使用左側共用尺寸；選項僅供記錄，適用製程與費用由內部確認。")
        mode = st.radio("計價方式", ["手動輸入", "不適用／不計費"], key="surface_mode", horizontal=True)
        surface = resolve("表面處理", mode)

with right:
    with st.container(border=True):
        st.subheader("02 壓鑄")
        cavities = record("壓鑄", "模具穴數", st.number_input("模具穴數（Cavity）", min_value=1, max_value=128, value=1))
        mode = st.radio("計價方式", ["手動輸入", "基準表計算", "不適用／不計費"], key="die_mode", horizontal=True)
        die = None
        if mode == "基準表計算":
            st.warning("以下數字是功能示範，並非市場行情。請改為公司核定費率後勾選確認。")
            rules = st.data_editor([
                {"最大邊長上限 (mm)": limit, "穴數": cav, "每件壓鑄費 (NT$)": rate}
                for limit, cav, rate in [(50.0, 1, 4.0), (50.0, 2, 2.8), (100.0, 1, 7.0), (100.0, 2, 4.8), (200.0, 1, 12.0), (200.0, 2, 8.0)]
            ], hide_index=True, key="rules", column_config={
                "最大邊長上限 (mm)": st.column_config.NumberColumn(min_value=0.01, required=True),
                "穴數": st.column_config.NumberColumn(min_value=1, step=1, required=True),
                "每件壓鑄費 (NT$)": st.column_config.NumberColumn(min_value=0.0, required=True, format="%.2f"),
            })
            confirmed = st.checkbox("我已確認目前基準表可用於此案件")
            st.caption("以最大邊長 ≤ 上限，配對相同穴數，取最小符合級距。表內費用已是每件費用，不再除以穴數。超出級距或找不到穴數時請手動填寫。")
            for index, rule in enumerate(rules, 1):
                for name, value in rule.items():
                    record("壓鑄基準表", f"第 {index} 列／{name}", value)
            record("壓鑄", "基準表已確認", "是" if confirmed else "否")
            if confirmed and all(value is not None for value in dimensions):
                die = die_cost(dimensions, cavities, rules)
        die = resolve("壓鑄", mode, die)

    with st.container(border=True):
        st.subheader("04 拋光")
        record("拋光", "等級", st.selectbox("拋光等級", ["粗拋光", "細拋光"]))
        st.caption("使用左側共用尺寸；費用依內部標準手動填寫。")
        mode = st.radio("計價方式", ["手動輸入", "不適用／不計費"], key="polish_mode", horizontal=True)
        polish = resolve("拋光", mode)

st.subheader("06 其他費用")
st.caption("在表格底部新增項目；選取列後可刪除。空白列不計入，有名稱的項目必須填入金額（可填 0）。")
extras = st.data_editor([{"項目名稱": "", "費用金額 (NT$/件)": None}],
    num_rows="dynamic", hide_index=True, key="extras", column_config={
        "項目名稱": st.column_config.TextColumn(),
        "費用金額 (NT$/件)": st.column_config.NumberColumn(min_value=0.0, max_value=1_000_000_000.0, format="%.2f"),
    })
other = Decimal("0.00")
for index, row in enumerate(extras, 1):
    name = (row.get("項目名稱") or "").strip()
    value = row.get("費用金額 (NT$/件)")
    if not name and value is None:
        continue
    if not name or value is None:
        missing.append(f"其他費用第 {index} 列（名稱或金額未填）")
        continue
    value = money(value)
    other += value
    details.append(["其他明細", "其他", name, str(value), "NT$/件"])

st.divider()
st.subheader("即時總結算")
items = [("原料", raw), ("壓鑄", die), ("加工", machining), ("拋光", polish), ("表面處理", surface), ("其他", other)]
total, summary = summarize(items)
if missing:
    st.warning("待填項目：" + "、".join(missing) + "。以下僅為已填費用小計；完成後即可匯出。")
st.dataframe(summary, hide_index=True, use_container_width=True, column_config={
    "金額 (NT$/件)": st.column_config.NumberColumn(format="%.2f"),
    "佔比 (%)": st.column_config.NumberColumn(format="%.2f%%"),
})
c1, c2 = st.columns(2)
c1.metric("已填費用小計" if missing else "初步報價總金額 (NT$/件)", f"NT$ {total:,.2f}")
c2.metric(f"{quantity:,} 件合計（未稅）", f"NT$ {total * quantity:,.2f}")
st.caption("各項費用先四捨五入至小數第 2 位，再加總。佔比因四捨五入可能不等於 100%；總額為 0 時佔比顯示 0%。")

now = datetime.now(timezone(timedelta(hours=8)))
rows = [["資料類別", "製程／分類", "欄位／項目", "數值", "單位／說明"],
        ["案件", "基本資料", "案件名稱", project, ""],
        ["案件", "基本資料", "客戶名稱", customer, ""],
        ["案件", "基本資料", "報價數量", quantity, "件"],
        ["案件", "基本資料", "匯出時間", now.isoformat(timespec="seconds"), "UTC+08:00"],
        ["案件", "計價範圍", "報價性質", "內部初估；未稅、未含利潤與未列入模具費", "所有製程按每件計價"]]
rows.extend(params)
rows.extend(details)
for entry, (name, value) in zip(summary, items):
    rows.append(["費用彙總", name, "每件費用", str(value), "NT$/件"])
    rows.append(["費用彙總", name, "佔比", f'{entry["佔比 (%)"]:.2f}', "%"])
rows.extend([["合計", "總額", "每件初步報價", str(total), "NT$/件"],
             ["合計", "總額", "整批初步報價", str(total * quantity), "NT$"]])
st.download_button("匯出報價明細 (CSV)", data=csv_bytes(rows),
                   file_name=f"quotation_{now:%Y%m%d_%H%M%S}.csv", mime="text/csv", disabled=bool(missing), type="primary")
