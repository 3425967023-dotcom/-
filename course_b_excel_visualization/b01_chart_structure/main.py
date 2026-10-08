"""
B01 图表数据结构 → 图表类型选择
教材定位：《Excel数据可视化——从图表到数据大屏》课件第 7 页
         「图表数据的基本结构」

【内涵解读】
课件给出最核心的一张表——「系列值数量 × 轴标签数量」决定该用哪种图。
这是选图的第一性原理，迁移到 Python 就是「DataFrame 的形状 → 用哪个 plot 方法」。

  系列值 | 轴标签 | 教材例子        | 适合图表          | Python 写法
  -------|--------|-----------------|-------------------|--------------------------------
    1    |   1    | 各商品销量      | 柱形/条形/折线/饼 | Series.plot(kind="bar"/"line"/"pie")
    1    |   0    | 总销量          | 卡片图            | ax.text() 大数字（大屏常用）
    1    |   2    | 各部门性别人数  | 簇状/堆积柱形     | pivot_table().plot(kind="bar", stacked=)
    2    |   1    | 销量 + 销售额   | 组合图(次坐标轴)  | ax.bar() + ax.twinx().plot()

另：课件第 8~9 页给出「五大关系 → 图表」的对应：
  构成 → 饼图/堆积柱形；趋势 → 折线图；比较 → 柱形/条形；
  分布 → 直方图/箱线图；联系 → 散点图/气泡图/桑基图。

运行：python course_b_excel_visualization/b01_chart_structure/main.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from common.style import apply_theme  # noqa: E402
from common.utils import save_fig, title  # noqa: E402

apply_theme()


def structured_demo() -> None:
    fig = plt.figure(figsize=(13.5, 7.6))

    # ---- 结构 1×1：系列值 1 + 轴标签 1 → 柱形 / 折线 / 环形 ----
    s = pd.Series([320, 460, 210, 390, 280], index=list("ABCDE"), name="销量")

    ax = fig.add_subplot(2, 3, 1)
    ax.bar(s.index, s.values, color="#85B7EB", edgecolor="#185FA5", width=0.6)
    ax.bar_label(ax.containers[0], fontsize=8)
    ax.set_title("1×1 柱形图", fontsize=11)
    ax.tick_params(axis="x", rotation=0, labelsize=8)

    ax = fig.add_subplot(2, 3, 2)
    ax.plot(s.index, s.values, marker="o", color="#378ADD")
    ax.set_title("1×1 折线图", fontsize=11)
    ax.tick_params(labelsize=8)

    ax = fig.add_subplot(2, 3, 3)
    ax.pie(s, labels=s.index, autopct="%1.0f%%",
           colors=plt.cm.Blues(np.linspace(0.3, 0.9, len(s))),
           wedgeprops=dict(width=0.5), textprops=dict(fontsize=8))
    ax.set_title("1×1 环形图", fontsize=11)

    # ---- 结构 1×0：系列值 1 + 轴标签 0 → 卡片图（大屏 KPI 区） ----
    ax = fig.add_subplot(2, 3, 4)
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0.08, 0.10), 0.84, 0.80, transform=ax.transAxes,
                               facecolor="#E6F1FB", edgecolor="#B5D4F4", lw=0.8))
    ax.text(0.5, 0.62, f"{s.sum():,.0f}", ha="center", va="center",
            fontsize=32, color="#0C447C", fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.30, "总销量", ha="center", va="center",
            fontsize=12, color="#5F5E5A", transform=ax.transAxes)
    ax.set_title("1×0 卡片图（数据大屏常用）", fontsize=11)

    # ---- 结构 1×2：系列值 1 + 轴标签 2 → 簇状 / 堆积柱形 ----
    d2 = pd.DataFrame({"Q1": [120, 90, 160], "Q2": [140, 110, 150]},
                      index=["冰箱", "电视", "洗衣机"])

    ax = fig.add_subplot(2, 3, 5)
    d2.plot(kind="bar", ax=ax, color=["#85B7EB", "#185FA5"], width=0.72, edgecolor="white")
    ax.set_title("1×2 簇状柱形图", fontsize=11)
    ax.legend(frameon=False, fontsize=8)
    ax.tick_params(axis="x", rotation=0, labelsize=8)
    ax.set_xlabel("")

    ax = fig.add_subplot(2, 3, 6)
    d2.plot(kind="bar", stacked=True, ax=ax, color=["#9FE1CB", "#0F6E56"],
            width=0.72, edgecolor="white")
    ax.set_title("1×2 堆积柱形图", fontsize=11)
    ax.legend(frameon=False, fontsize=8)
    ax.tick_params(axis="x", rotation=0, labelsize=8)
    ax.set_xlabel("")

    fig.tight_layout()
    save_fig(fig, "B01_chart_structure.png")


def five_relations() -> None:
    """课件第 8~9 页：五大关系 → 五种图表。"""
    rng = np.random.default_rng(11)
    fig = plt.figure(figsize=(13.5, 7.6))

    # 构成
    ax = fig.add_subplot(2, 3, 1)
    comp = pd.Series([38, 26, 21, 15], index=["A", "B", "C", "D"])
    ax.pie(comp, labels=comp.index, autopct="%1.0f%%",
           colors=plt.cm.Blues(np.linspace(0.3, 0.9, 4)),
           wedgeprops=dict(width=0.45), textprops=dict(fontsize=8))
    ax.set_title("构成 · 环形图", fontsize=11)

    # 趋势
    ax = fig.add_subplot(2, 3, 2)
    x = np.arange(12)
    ax.plot(x, 100 + 8 * x + rng.normal(0, 6, 12), marker="o", ms=3, color="#378ADD")
    ax.set_title("趋势 · 折线图", fontsize=11)
    ax.tick_params(labelsize=8)

    # 比较
    ax = fig.add_subplot(2, 3, 3)
    cats = ["甲", "乙", "丙", "丁", "戊"]
    ax.barh(cats, [42, 61, 55, 78, 33], color="#85B7EB", edgecolor="#185FA5")
    ax.set_title("比较 · 条形图", fontsize=11)
    ax.tick_params(labelsize=8)

    # 分布
    ax = fig.add_subplot(2, 3, 4)
    ax.hist(rng.normal(100, 18, 500), bins=28, color="#9FE1CB", edgecolor="white")
    ax.set_title("分布 · 直方图", fontsize=11)
    ax.tick_params(labelsize=8)

    # 联系
    ax = fig.add_subplot(2, 3, 5)
    xx = rng.normal(50, 12, 180)
    ax.scatter(xx, 2 * xx + rng.normal(0, 16, 180), s=14, alpha=0.55, color="#7F77DD")
    ax.set_title("联系 · 散点图", fontsize=11)
    ax.tick_params(labelsize=8)

    # 帕累托图（分布 + 累计占比，课件第 9 页提到）
    ax = fig.add_subplot(2, 3, 6)
    items = [f"项{i + 1}" for i in range(8)]
    vals = np.array([420, 330, 210, 160, 120, 80, 50, 30])
    order = np.argsort(-vals)
    vals_s = vals[order]
    cum = vals_s.cumsum() / vals_s.sum() * 100
    ax.bar(range(8), vals_s, color="#B5D4F4", edgecolor="#185FA5")
    ax2 = ax.twinx()
    ax2.plot(range(8), cum, marker="o", ms=3, color="#A32D2D")
    ax2.axhline(80, ls="--", color="#888780", lw=0.8)
    ax2.set_ylim(0, 105)
    ax2.set_ylabel("累计占比 %", fontsize=8)
    ax.set_xticks(range(8))
    ax.set_xticklabels([items[i] for i in order], fontsize=8)
    ax.set_title("帕累托图（80/20 法则）", fontsize=11)

    fig.tight_layout()
    save_fig(fig, "B01_five_relations.png")


def main() -> None:
    title("B01 图表数据结构与类型选择")
    structured_demo()
    five_relations()
    print("\n完成：结构决策表 + 五大关系对照表各 1 张。")


if __name__ == "__main__":
    main()
