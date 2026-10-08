"""
B05 交互式数据大屏（streamlit 版）

教材定位：《Excel数据可视化——从图表到数据大屏》第四章「数据大屏」

【与 Excel 的对应关系】
  Excel 切片器          → st.multiselect （侧边栏筛选）
  Excel 卡片图          → st.metric（带环比的小卡片）
  图表随筛选联动重绘     → streamlit 每次交互自动重跑脚本（数据流式响应）

【运行方式】
  pip install streamlit plotly
  streamlit run course_b_excel_visualization/b05_dashboard/app.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

import pandas as pd  # noqa: E402
import plotly.express as px  # noqa: E402
import streamlit as st  # noqa: E402

from common.utils import init_exp, load_sheets  # noqa: E402

init_exp(__file__)  # streamlit 启动时 argv[0] 不是本脚本，需显式指定实验目录

st.set_page_config(page_title="销售数据可视化大屏", layout="wide")
st.title("销售数据可视化大屏")
st.caption("数据口径：第四章 销售看板参考.xlsx / 销售明细表")

# ---------------- 数据 ----------------
df = load_sheets("第四章 销售看板参考.xlsx")["销售明细"].copy()
df["订单日期"] = pd.to_datetime(df["订单日期"], errors="coerce")

# ---------------- 侧边栏：切片器 ----------------
with st.sidebar:
    st.header("筛选器")
    regions = st.multiselect("区域", sorted(df["区域"].dropna().unique()),
                             default=sorted(df["区域"].dropna().unique()))
    cats = st.multiselect("产品类别", sorted(df["产品类别"].dropna().unique()),
                          default=sorted(df["产品类别"].dropna().unique()))
    dmin, dmax = df["订单日期"].min(), df["订单日期"].max()
    dr = st.date_input("日期范围", (dmin, dmax))

# ---------------- 筛选 ----------------
d = df[df["区域"].isin(regions) & df["产品类别"].isin(cats)]
if isinstance(dr, (tuple, list)) and len(dr) == 2:
    d = d[d["订单日期"].between(pd.Timestamp(dr[0]), pd.Timestamp(dr[1]))]

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("总订单额", f"¥{d['订单额'].sum() / 1e4:,.1f} 万")
kpi2.metric("总利润", f"¥{d['利润额'].sum() / 1e4:,.1f} 万")
orders = d["订单单号"].nunique()
kpi3.metric("订单数", f"{orders:,}")
kpi4.metric("客单价", f"¥{d['订单额'].sum() / max(orders, 1):,.0f}")

st.divider()

c1, c2 = st.columns([1.4, 1])
with c1:
    t = d.groupby(d["订单日期"].dt.to_period("M").astype(str), as_index=False) \
         .agg(订单额=("订单额", "sum"), 利润额=("利润额", "sum"))
    fig = px.bar(t, x="订单日期", y="订单额", title="月度订单额")
    fig.add_scatter(x=t["订单日期"], y=t["利润额"], mode="lines+markers",
                    name="利润额")
    fig.update_layout(font_family="Microsoft YaHei", height=380)
    st.plotly_chart(fig, use_container_width=True)
with c2:
    r = d.groupby("区域", as_index=False)["订单额"].sum()
    fig = px.pie(r, names="区域", values="订单额", hole=0.45, title="区域订单额占比")
    fig.update_layout(font_family="Microsoft YaHei", height=380)
    st.plotly_chart(fig, use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    p = d.groupby("产品类别", as_index=False)["订单额"].sum() \
         .sort_values("订单额").tail(10)
    fig = px.bar(p, x="订单额", y="产品类别", orientation="h",
                 title="产品类别订单额 Top 10")
    fig.update_layout(font_family="Microsoft YaHei", height=360)
    st.plotly_chart(fig, use_container_width=True)
with c4:
    n = d.groupby("产品名称", as_index=False)["利润额"].sum() \
         .sort_values("利润额").tail(10)
    fig = px.bar(n, x="利润额", y="产品名称", orientation="h",
                 title="产品利润额 Top 10")
    fig.update_layout(font_family="Microsoft YaHei", height=360)
    st.plotly_chart(fig, use_container_width=True)

with st.expander("查看明细数据"):
    st.dataframe(d.head(200), use_container_width=True)
