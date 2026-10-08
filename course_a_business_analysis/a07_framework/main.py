"""
A07 商业数据分析框架：三个完整案例
教材定位：《商业数据分析》第 3 章 商业数据分析框架（案例1/2/3）

【内涵解读】
第 3 章是「框架」章，三个案例对应三种典型分析目标，
是把第 1、2 章的范式串成完整分析链的实战：

  案例1 收入趋势分析    时间维度：趋势 + 同比/环比 + 分省下钻
  案例2 财务费用分析    成本结构：总费用 → 三大期间费用 → 管理费用（三层下钻）
  案例3 电商精准营销    用户维度：人群画像 + 品类偏好 + 支付方式

【迁移要点】
教材的「下钻」在 pandas 里就是「换一个 groupby 的粒度」；
教材的「切片器」在代码里就是「先做布尔筛选，再聚合」。

运行：python course_a_business_analysis/framework.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from common.style import NEGATIVE, POSITIVE  # noqa: E402
from common.utils import load, load_sheets, report_head, save_fig, save_table, title  # noqa: E402

D = ""


# ==================== 案例 1：收入趋势分析 ====================
def case1_income_trend() -> None:
    """字段：订单年份, 订单月份, 销售省份, 销售额"""
    df = load(D + "案例1：收入趋势分析原始数据.xlsx")
    report_head(df, 3, "案例1 原始数据")

    ts = df.groupby(["订单年份", "订单月份"], as_index=False)["销售额"].sum()
    ts["日期"] = pd.to_datetime(dict(year=ts["订单年份"],
                                     month=ts["订单月份"], day=1))
    ts = ts.sort_values("日期")
    ts["同比%"] = ts["销售额"].pct_change(12) * 100    # 12 期前 = 去年同期
    ts["环比%"] = ts["销售额"].pct_change() * 100
    ts["MA3"] = ts["销售额"].rolling(3).mean()         # 三月移动平均

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6.4), sharex=True,
                                   gridspec_kw=dict(height_ratios=[3, 1]))
    ax1.plot(ts["日期"], ts["销售额"], marker="o", ms=3, color="#378ADD", label="销售额")
    ax1.plot(ts["日期"], ts["MA3"], ls="--", color="#EF9F27", label="3 月移动平均")
    ax1.set_title("案例1 · 收入趋势分析", fontsize=12)
    ax1.set_ylabel("销售额")
    ax1.legend(frameon=False, fontsize=9)

    yoy = ts["同比%"].fillna(0)
    ax2.bar(ts["日期"], yoy, width=20, color=np.where(yoy >= 0, POSITIVE, NEGATIVE))
    ax2.axhline(0, color="#444441", lw=0.8)
    ax2.set_ylabel("同比 %")
    fig.tight_layout()
    save_fig(fig, "A07_case1_income.png")

    prov = df.pivot_table(index="销售省份", columns="订单年份",
                          values="销售额", aggfunc="sum", fill_value=0)
    prov["合计"] = prov.sum(axis=1)
    prov = prov.sort_values("合计", ascending=False)
    print("\n案例1 · 分省年度收入（Top 10）：")
    print(prov.head(10).to_string())
    save_table(prov.reset_index(), "A07_case1_province.csv")


# ==================== 案例 2：财务费用分析 ====================
def case2_expense() -> None:
    """三个 sheet 构成三层下钻：总费用 → 三大期间费用 → 管理费用明细"""
    total = load(D + "案例2：财务费用分析-原始数据.xlsx", sheet="总费用数据")
    period = load(D + "案例2：财务费用分析-原始数据.xlsx", sheet="财务三大期间费用数据")
    admin = load(D + "案例2：财务费用分析-原始数据.xlsx", sheet="管理费用数据")
    admin = admin.rename(columns={"份": "月份"})        # 教材该列名写作「份」

    for d in (total, period, admin):
        d["日期"] = pd.to_datetime(dict(year=d["年份"], month=d["月份"], day=1))

    fig = plt.figure(figsize=(12.5, 8))

    ax1 = fig.add_subplot(2, 2, 1)
    ax1.plot(total["日期"], total["金额"], marker="o", color="#378ADD")
    ax1.set_title("① 总费用趋势（第一层）", fontsize=11)
    ax1.tick_params(axis="x", rotation=45, labelsize=8)
    ax1.set_ylabel("费用金额")

    ax2 = fig.add_subplot(2, 2, 2)
    p = period.pivot_table(index="日期", columns="期间费用项",
                           values="金额", aggfunc="sum")
    p.plot(kind="bar", stacked=True, ax=ax2, colormap="Blues",
           width=0.75, edgecolor="white")
    ax2.set_title("② 三大期间费用构成（第二层下钻）", fontsize=11)
    ax2.tick_params(axis="x", rotation=45, labelsize=8)
    ax2.legend(frameon=False, fontsize=8)
    ax2.set_xlabel("")

    ax3 = fig.add_subplot(2, 2, 3)
    a = admin.pivot_table(index="日期", columns="管理费用项",
                          values="金额", aggfunc="sum")
    a.plot(ax=ax3, marker="o", ms=3)
    ax3.set_title("③ 管理费用明细趋势（第三层下钻）", fontsize=11)
    ax3.tick_params(axis="x", rotation=45, labelsize=8)
    ax3.legend(frameon=False, fontsize=7)
    ax3.set_xlabel("")

    # ④ 结构变化归因：不用绝对值变化，而用「占比的变化量」做堆积
    ax4 = fig.add_subplot(2, 2, 4)
    share = p.div(p.sum(axis=1), axis=0) * 100
    share.diff().plot(kind="bar", stacked=True, ax=ax4,
                      colormap="coolwarm", width=0.75, edgecolor="white")
    ax4.axhline(0, color="#444441", lw=0.8)
    ax4.set_title("④ 费用结构变动贡献（占比环比变化）", fontsize=11)
    ax4.tick_params(axis="x", rotation=45, labelsize=8)
    ax4.legend(frameon=False, fontsize=7)
    ax4.set_xlabel("")

    fig.tight_layout()
    save_fig(fig, "A07_case2_expense.png")

    print("\n案例2 · 三大期间费用（前 6 期）：")
    print(p.head(6).to_string())
    print("\n案例2 · 期间费用占比（%）：")
    print(share.round(1).head(6).to_string())


# ==================== 案例 3：电商平台精准营销 ====================
def case3_ecommerce() -> None:
    """字段：客户ID, 性别, 年龄, 品类, 数量, 支付方式, 订单月份, 订单年份"""
    df = load(D + "案例3：电商平台的精准营销-原始数据.xlsx")
    report_head(df, 3, "案例3 原始数据")
    df["日期"] = pd.to_datetime(dict(year=df["订单年份"],
                                     month=df["订单月份"], day=1))

    # ① 人群画像：年龄分箱（等价 Power BI 的「分组」）
    bins = [0, 18, 25, 35, 45, 60, 200]
    labels = ["≤18", "19-25", "26-35", "36-45", "46-60", ">60"]
    df["年龄段"] = pd.cut(df["年龄"], bins=bins, labels=labels)
    age_gender = pd.crosstab(df["年龄段"], df["性别"])
    age_gender_pct = pd.crosstab(df["年龄段"], df["性别"], normalize="columns") * 100

    # ② 品类偏好：各品类订单量
    pref = df["品类"].value_counts()

    # ③ 支付方式：订单数与平均购买数量
    pay = df.groupby("支付方式").agg(订单数=("客户ID", "count"),
                                     平均数量=("数量", "mean")).round(2)

    print("\n案例3 · 年龄 × 性别 人数：")
    print(age_gender.to_string())
    print("\n案例3 · 支付方式：")
    print(pay.to_string())

    fig = plt.figure(figsize=(12.5, 8))
    ax1 = fig.add_subplot(2, 2, 1)
    age_gender.plot(kind="bar", ax=ax1, color=["#D4537E", "#378ADD"],
                    width=0.75, edgecolor="white")
    ax1.set_title("① 年龄 × 性别 客群结构", fontsize=11)
    ax1.legend(frameon=False, fontsize=8)
    ax1.tick_params(axis="x", rotation=0, labelsize=8)
    ax1.set_xlabel("")

    ax2 = fig.add_subplot(2, 2, 2)
    pref.head(10)[::-1].plot(kind="barh", ax=ax2, color="#9FE1CB", edgecolor="#0F6E56")
    ax2.set_title("② 品类订单量 Top 10", fontsize=11)
    ax2.tick_params(labelsize=8)
    ax2.set_ylabel("")

    ax3 = fig.add_subplot(2, 2, 3)
    df.groupby("日期")["数量"].sum().plot(ax=ax3, marker="o", color="#7F77DD")
    ax3.set_title("③ 月度销量趋势", fontsize=11)
    ax3.tick_params(labelsize=8)

    ax4 = fig.add_subplot(2, 2, 4)
    pay["订单数"].plot(kind="bar", ax=ax4, color="#EF9F27", edgecolor="#854F0B")
    ax4.set_title("④ 各支付方式订单数", fontsize=11)
    ax4.tick_params(axis="x", rotation=20, labelsize=8)
    ax4.set_xlabel("")

    fig.tight_layout()
    save_fig(fig, "A07_case3_ecommerce.png")

    # 营销策略落点：找出「人数最多 + 品类偏好集中」的客群
    top_seg = df.groupby(["年龄段", "品类"], observed=True).size().sort_values(ascending=False)
    print("\n案例3 · 客群 × 品类 组合 Top 8（精准营销投放优先级）：")
    print(top_seg.head(8).to_string())
    save_table(top_seg.reset_index(name="订单数"), "A07_case3_segments.csv")


def main() -> None:
    title("A07 商业数据分析框架：三个完整案例")
    case1_income_trend()
    case2_expense()
    case3_ecommerce()
    print("\n三个案例完成，共输出 3 张综合图 + 3 张明细表。")


if __name__ == "__main__":
    main()
