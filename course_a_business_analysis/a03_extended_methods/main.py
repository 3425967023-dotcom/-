"""
A03 六类引申分析方法（趋势 / 对比 / 构成 / 分布 / 关系 / 桑基）
教材定位：《商业数据分析》第 2 章-2 由基础分析范式引申出的分析方法

【内涵解读】
六大基础范式解决「算得对」，六类分析方法解决「看得懂」。
教材给每类方法配了图表形态，迁移时必须「数据 + 图形语义」一起迁：
  趋势 → 折线 + 移动平均 + 同比标注
  对比 → 分组柱形 + 增长率标注
  构成 → 堆积柱形 + 环形图（部分与整体）
  分布 → 直方图 + 箱线图（集中趋势与异常值）
  关系 → 散点 + 回归线；分类 × 连续 → 分组箱线
  桑基 → 分流结构（matplotlib 无原生桑基，改用 plotly）

【关于教材数据】
`2、由基础分析范式引申出的分析方法/data-无答案/` 下的 6 个 xlsx 中，
有 5 个是「成品图表文件」——表头直接是图表标题（如「近 10 年订单量波动趋势图」），
数值嵌在图表对象里，普通 read_excel 读不到数据区。
所以前 5 类用等价结构数据重建，第 6 类（6桑吉图.xlsx）数据规范，直接读教材原表。

运行：python course_a_business_analysis/a03_extended_methods/main.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from common.style import NEGATIVE, POSITIVE  # noqa: E402
from common.utils import load, save_fig, save_html, title  # noqa: E402


# ---------------- 1. 趋势分析 ----------------
def trend() -> None:
    years = np.arange(2014, 2024)
    orders = np.array([820, 910, 1080, 1190, 1350, 1420, 1560, 1490, 1720, 1950])
    df = pd.DataFrame({"年份": years, "订单量": orders})
    df["三年移动平均"] = df["订单量"].rolling(3, center=True).mean()
    df["同比"] = df["订单量"].pct_change() * 100      # 逐年同比

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6.2), sharex=True,
                                   gridspec_kw=dict(height_ratios=[3, 1]))
    ax1.plot(df["年份"], df["订单量"], marker="o", color="#378ADD", label="订单量")
    ax1.plot(df["年份"], df["三年移动平均"], ls="--", color="#EF9F27",
             label="3 年移动平均")
    for x, y, r in zip(df["年份"], df["订单量"], df["同比"]):
        if pd.notna(r):
            ax1.annotate(f"{r:+.1f}%", (x, y), textcoords="offset points",
                         xytext=(0, 9), ha="center", fontsize=7.5, color="#5F5E5A")
    ax1.set_ylim(0, df["订单量"].max() * 1.22)
    ax1.set_title("① 趋势分析：近 10 年订单量波动", fontsize=12)
    ax1.set_ylabel("订单量")
    ax1.legend(frameon=False, fontsize=9)

    bars = ax2.bar(df["年份"], df["同比"].fillna(0), width=0.55,
                   color=np.where(df["同比"].fillna(0) >= 0, POSITIVE, NEGATIVE))
    ax2.axhline(0, color="#444441", lw=0.8)
    ax2.bar_label(bars, labels=["" if pd.isna(v) else f"{v:.0f}%"
                                for v in df["同比"]], fontsize=7)
    ax2.set_ylabel("同比 %")
    fig.tight_layout()
    save_fig(fig, "A03_01_trend.png")


# ---------------- 2. 对比分析 ----------------
def compare() -> None:
    df = pd.DataFrame({"产品": ["A", "B", "C", "D"],
                       "本期": [1240, 980, 1520, 760],
                       "上期": [1100, 1020, 1180, 810]})
    df["增长率"] = (df["本期"] / df["上期"] - 1) * 100

    x = np.arange(len(df))
    w = 0.36
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.bar(x - w / 2, df["上期"], w, label="上期", color="#B4B2A9")
    b2 = ax.bar(x + w / 2, df["本期"], w, label="本期", color="#378ADD")
    ax.bar_label(b2, labels=[f"{v:+.1f}%" for v in df["增长率"]], fontsize=9,
                 color="#5F5E5A")
    ax.set_xticks(x)
    ax.set_xticklabels(df["产品"])
    ax.set_ylim(0, df[["本期", "上期"]].max().max() * 1.18)
    ax.set_title("② 对比分析：本期 vs 上期订单量", fontsize=12)
    ax.set_ylabel("订单量")
    ax.legend(frameon=False, fontsize=9)
    save_fig(fig, "A03_02_compare.png")


# ---------------- 3. 构成分析 ----------------
def composition() -> None:
    df = pd.DataFrame({"季度": ["Q1", "Q2", "Q3", "Q4"],
                       "华东": [320, 380, 410, 460],
                       "华北": [210, 240, 260, 280],
                       "华南": [180, 200, 230, 250],
                       "西部": [120, 130, 150, 170]})
    d = df.set_index("季度")
    # 份额（构成分析的核心：把绝对值转成占比）
    share = d.div(d.sum(axis=1), axis=0) * 100

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(13, 4), width_ratios=[1.4, 1.4, 1])
    d.plot(kind="bar", stacked=True, ax=ax1, colormap="Blues", width=0.68,
           edgecolor="white")
    ax1.set_title("③-1 绝对值堆积", fontsize=11)
    ax1.legend(frameon=False, fontsize=7)
    ax1.tick_params(axis="x", rotation=0, labelsize=8)

    share.plot(kind="bar", stacked=True, ax=ax2, colormap="Blues", width=0.68,
               edgecolor="white")
    ax2.set_title("③-2 百分比堆积（构成变化更清楚）", fontsize=11)
    ax2.legend(frameon=False, fontsize=7)
    ax2.tick_params(axis="x", rotation=0, labelsize=8)
    ax2.set_ylabel("%")

    ax3.pie(d.sum(), labels=d.columns, autopct="%1.1f%%",
            colors=plt.cm.Blues(np.linspace(0.35, 0.85, 4)),
            wedgeprops=dict(width=0.42), textprops=dict(fontsize=8))
    ax3.set_title("③-3 全年区域占比", fontsize=11)
    fig.tight_layout()
    save_fig(fig, "A03_03_composition.png")


# ---------------- 4. 分布分析 ----------------
def distribution() -> None:
    rng = np.random.default_rng(42)
    data = np.concatenate([rng.normal(3200, 900, 600), rng.normal(6800, 1400, 250)])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.2), width_ratios=[2, 1])
    ax1.hist(data, bins=45, color="#9FE1CB", edgecolor="white")
    ax1.axvline(data.mean(), color="#A32D2D", ls="--", label=f"均值 {data.mean():.0f}")
    ax1.axvline(np.median(data), color="#EF9F27", ls=":",
                label=f"中位数 {np.median(data):.0f}")
    ax1.set_title("④-1 分布分析：客户消费金额直方图", fontsize=11)
    ax1.set_xlabel("消费金额（元）")
    ax1.set_ylabel("频次")
    ax1.legend(frameon=False, fontsize=9)

    bp = ax2.boxplot(data, widths=0.45, patch_artist=True)
    for patch in bp["boxes"]:
        patch.set_facecolor("#B5D4F4")
        patch.set_edgecolor("#185FA5")
    ax2.set_title("④-2 箱线图：异常值识别", fontsize=11)
    ax2.set_xticks([])
    ax2.set_ylabel("消费金额（元）")
    fig.tight_layout()
    save_fig(fig, "A03_04_distribution.png")


# ---------------- 5. 关系分析 ----------------
def relation() -> None:
    rng = np.random.default_rng(7)
    price = rng.normal(50, 12, 200)
    sales = 2.1 * price + rng.normal(0, 18, 200)
    grp = pd.Series(rng.choice(["高", "中", "低"], 200), name="分层")
    d = pd.DataFrame({"价格": price, "销量": sales, "分层": grp})

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.2))
    ax1.scatter(d["价格"], d["销量"], s=16, alpha=0.55, color="#7F77DD")
    k, b = np.polyfit(d["价格"], d["销量"], 1)
    xs = np.linspace(d["价格"].min(), d["价格"].max(), 50)
    ax1.plot(xs, k * xs + b, color="#A32D2D", lw=1.5)
    ax1.set_xlabel("价格")
    ax1.set_ylabel("销量")
    ax1.set_title(f"⑤-1 连续 × 连续：r = {d['价格'].corr(d['销量']):.2f}", fontsize=11)

    groups = [d.loc[d["分层"] == g, "销量"].values for g in ["低", "中", "高"]]
    # 注意：matplotlib 3.11 起 boxplot 的 labels 参数已移除，改用 set_xticklabels
    bp = ax2.boxplot(groups, widths=0.5, patch_artist=True)
    ax2.set_xticks([1, 2, 3])
    ax2.set_xticklabels(["低", "中", "高"])
    for patch, c in zip(bp["boxes"], ["#9FE1CB", "#5DCAA5", "#1D9E75"]):
        patch.set_facecolor(c)
        patch.set_edgecolor("#0F6E56")
    ax2.set_title("⑤-2 分类 × 连续：分层销量分布", fontsize=11)
    ax2.set_ylabel("销量")
    fig.tight_layout()
    save_fig(fig, "A03_05_relation.png")


# ---------------- 6. 桑基图（用教材原表） ----------------
def sankey() -> None:
    import plotly.graph_objects as go

    df = load("6桑吉图.xlsx", sheet="Sheet1")
    print("\n桑基图原始数据：")
    print(df.head().to_string())

    labels = pd.unique(pd.concat([df["来源"], df["目标"]], ignore_index=True))
    idx = {l: i for i, l in enumerate(labels)}
    fig = go.Figure(go.Sankey(
        node=dict(label=list(labels), pad=16, thickness=16, color="#85B7EB"),
        link=dict(source=[idx[s] for s in df["来源"]],
                  target=[idx[t] for t in df["目标"]],
                  value=df["流量"]),
    ))
    fig.update_layout(title_text="⑥ 桑基图：流量去向与分流结构",
                      font_size=12, font_family="Microsoft YaHei")
    save_html(fig, "A03_06_sankey.html")


def main() -> None:
    title("A03 六类引申分析方法")
    trend()
    compare()
    composition()
    distribution()
    relation()
    sankey()
    print("\n六类方法完成：5 张 png + 1 张可交互 html。")


if __name__ == "__main__":
    main()
