"""
B05 数据大屏
教材定位：《Excel数据可视化——从图表到数据大屏》第四章 销售看板参考.xlsx
         （含「数据大屏展示」「数据大屏」「销售明细」「成本明细」「统计数据」sheet）

【内涵解读】
Excel 做数据大屏的套路是「单元格铺背景板 + 图表浮在上面 + 手工对齐」；
Python 用「栅格布局（GridSpec）+ 统一主题 + KPI 卡片区 + 多图联动」来替代，
好处是分辨率无关、可批量重绘、可接实时数据。

本文件给出两个版本：
  dashboard.py（本文件）—— matplotlib 静态大屏，可直接截图交作业
  app.py                —— streamlit 交互大屏，可拖动、可筛选、可联动

数据源（教材原表）：
  销售明细  订单日期, 订单单号, 区域, 快递公司, 订单额, 产品单价,
            利润额, 产品类别, 产品名称, 月份_销售
  成本明细  月份_成本, 类别, 成本

运行：python course_b_excel_visualization/b05_dashboard/main.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.gridspec import GridSpec  # noqa: E402

from common.style import BG, NEUTRAL, apply_theme  # noqa: E402
from common.utils import load, load_sheets, report_head, save_fig, title  # noqa: E402

apply_theme()

FE = "第四章 销售看板参考.xlsx"


def kpi_card(ax, value: str, name: str, color: str = "#E6F1FB",
             edge: str = "#B5D4F4") -> None:
    """KPI 卡片：等价 Excel 的「卡片图」，大屏顶部指标区标准做法。"""
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                               facecolor=color, edgecolor=edge, lw=0.8))
    ax.text(0.5, 0.62, value, ha="center", va="center", fontsize=16,
            color="#0C447C", fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.24, name, ha="center", va="center", fontsize=10,
            color="#5F5E5A", transform=ax.transAxes)


def main() -> None:
    title("B05 销售数据可视化大屏（matplotlib 静态版）")

    sheets = load_sheets(FE)
    print("数据文件含表：", list(sheets.keys()))
    df = sheets["销售明细"].copy()
    cost = sheets["成本明细"].copy()
    df["订单日期"] = pd.to_datetime(df["订单日期"], errors="coerce")
    df["月"] = df["订单日期"].dt.to_period("M").astype(str)
    report_head(df, 3, "销售明细")

    # ---------------- KPI ----------------
    gmv = df["订单额"].sum()
    profit = df["利润额"].sum()
    orders = df["订单单号"].nunique()
    aov = gmv / max(orders, 1)
    kpi = [("总订单额", f"¥{gmv / 1e4:,.1f}万"),
           ("总利润", f"¥{profit / 1e4:,.1f}万"),
           ("订单数", f"{orders:,}"),
           ("客单价", f"¥{aov:,.0f}")]
    print("\n【大屏 KPI】", {k: v for k, v in kpi})

    # ---------------- 栅格布局 ----------------
    fig = plt.figure(figsize=(15, 9))
    fig.patch.set_facecolor(BG)
    gs = GridSpec(4, 12, figure=fig, hspace=0.95, wspace=1.6,
                  top=0.88, bottom=0.10, left=0.045, right=0.965)

    fig.suptitle("销售数据可视化大屏", fontsize=20, fontweight="bold",
                 color="#0C447C", y=0.965)
    fig.text(0.5, 0.918, "数据口径：第四章 销售看板参考.xlsx / 销售明细表 ｜ "
                         "制图：Python + Matplotlib",
             ha="center", fontsize=9, color="#888780")

    # ---- 第 1 行：4 个 KPI 卡片 ----
    for i, (name, val) in enumerate(kpi):
        ax = fig.add_subplot(gs[0, i * 3:(i + 1) * 3])
        kpi_card(ax, val, name)

    # ---- 第 2 行：月度趋势 + 区域构成 ----
    ax1 = fig.add_subplot(gs[1, 0:7])
    m = df.groupby("月").agg(订单额=("订单额", "sum"), 利润额=("利润额", "sum"))
    ax1.bar(m.index, m["订单额"], color="#B5D4F4", edgecolor="#185FA5",
            width=0.6, label="订单额")
    ax1.plot(m.index, m["利润额"], marker="o", ms=4, color="#A32D2D", label="利润额")
    ax1.set_title("月度订单额与利润趋势", fontsize=12, loc="left")
    ax1.legend(frameon=False, fontsize=8)
    ax1.tick_params(axis="x", rotation=45, labelsize=8)

    ax2 = fig.add_subplot(gs[1, 7:12])
    r = df.groupby("区域")["订单额"].sum().sort_values(ascending=False)
    ax2.pie(r, labels=r.index, autopct="%1.0f%%",
            colors=plt.cm.Blues(np.linspace(0.35, 0.9, len(r))),
            wedgeprops=dict(width=0.46), textprops=dict(fontsize=8))
    ax2.set_title("区域订单额占比", fontsize=12, loc="left")

    # ---- 第 3 行：产品类别 Top + 快递公司 ----
    ax3 = fig.add_subplot(gs[2, 0:6])
    p = df.groupby("产品类别")["订单额"].sum().sort_values().tail(8)
    ax3.barh(p.index, p.values, color="#9FE1CB", edgecolor="#0F6E56")
    ax3.set_title("产品类别订单额 Top 8", fontsize=12, loc="left")
    ax3.tick_params(labelsize=8)

    ax4 = fig.add_subplot(gs[2, 6:12])
    e = df.groupby("快递公司")["订单单号"].nunique().sort_values()
    ax4.bar(e.index, e.values, color="#EF9F27", edgecolor="#854F0B")
    ax4.set_title("各快递公司承运订单数", fontsize=12, loc="left")
    ax4.tick_params(axis="x", rotation=25, labelsize=8)

    # ---- 第 4 行：成本构成 + 产品利润 Top ----
    ax5 = fig.add_subplot(gs[3, 0:6])
    c = cost.groupby("类别")["成本"].sum().sort_values(ascending=False)
    ax5.bar(c.index, c.values, color=NEUTRAL, edgecolor="#888780")
    ax5.set_title("成本构成", fontsize=12, loc="left")
    ax5.tick_params(axis="x", rotation=25, labelsize=8)

    ax6 = fig.add_subplot(gs[3, 6:12])
    n = df.groupby("产品名称")["利润额"].sum().sort_values().tail(8)
    ax6.barh(n.index, n.values, color="#85B7EB", edgecolor="#185FA5")
    ax6.set_title("产品利润额 Top 8", fontsize=12, loc="left")
    ax6.tick_params(labelsize=8)

    save_fig(fig, "B05_dashboard.png")
    print("\n完成：静态大屏已输出。交互版见同目录 app.py。")


if __name__ == "__main__":
    main()
