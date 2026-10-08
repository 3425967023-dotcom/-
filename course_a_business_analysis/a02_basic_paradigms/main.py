"""
A02 六大基础分析范式
教材定位：《商业数据分析》第 2 章-1 分析的基础范式（data-无答案 6 个文件）

【内涵解读】
教材把商业分析的底层动作归纳为六个可复用「范式」——
范式 = 一套固定的「算哪些指标 + 怎么呈现」的套路：

  1. 波士顿矩阵 BCG   业务单元按「增长率 × 相对份额」分四象限
  2. RFM 模型         按最近消费(R)、频次(F)、金额(M) 给客户打分分层
  3. 用户忠诚度模型   按活跃度与消费频次把会员分成 高/中/低/流失
  4. 同期群分析       Cohort：按注册月分组，看后续各月留存率
  5. 漏斗图           逐环节转化率，定位流失最严重的环节
  6. 相关分析         两变量的相关强度与线性关系

【迁移要点】
每个范式的核心都是「先确定要算的 2~3 个指标，再用一张图呈现」。
识别清楚指标定义，代码就是 groupby + 可视化。

运行：python course_a_business_analysis/a02_basic_paradigms/main.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from common.style import NEUTRAL  # noqa: E402
from common.utils import load, save_fig, save_table, title  # noqa: E402

BASE = ""


def _score(s: pd.Series, ascending: bool = True) -> pd.Series:
    """稳健的 1~5 分位打分。

    教材用 Excel 的 PERCENTRANK 打分；pandas 直接用 qcut。
    但 qcut 在数值大量重复时会抛 "Bin edges must be unique"，
    所以标准做法是先 rank(method="first") 打散并列值，再 qcut。
    ascending=True 表示值越大越优（F/M），False 表示越小越优（R）。
    """
    q = pd.qcut(s.rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    return q if ascending else 6 - q


# ==================== 1. 波士顿矩阵 ====================
def bcg() -> None:
    df = load(BASE + "1-1波士顿矩阵.xlsx", sheet="销售表")
    df["销售日期"] = pd.to_datetime(df["销售日期"])
    df["销售额"] = df["单价"] * df["销量"]
    df["月"] = df["销售日期"].dt.to_period("M")

    ms = df.groupby(["品牌", "月"])["销量"].sum().unstack(fill_value=0)
    print("品牌 × 月 销量：")
    print(ms.to_string())

    # 纵轴：销售增长率（首月 → 末月）
    growth = (ms.iloc[:, -1] - ms.iloc[:, 0]) / ms.iloc[:, 0].replace(0, np.nan) * 100
    # 横轴：相对市场份额 = 本品牌份额 ÷ 最大竞争者份额
    total = ms.sum(axis=1)
    share = total / total.sum() * 100
    rel = share / max(share.drop(share.idxmax()).max(), 1e-9)

    fig, ax = plt.subplots(figsize=(7, 5.2))
    ax.scatter(rel, growth, s=total / total.max() * 900, alpha=0.55,
               color="#378ADD", edgecolor="#185FA5", zorder=3)
    for b in rel.index:
        ax.annotate(b, (rel[b], growth[b]), ha="center", va="center",
                    fontsize=10, zorder=4)
    ax.axvline(1, ls="--", lw=0.8, color="#888780")
    ax.axhline(growth.mean(), ls="--", lw=0.8, color="#888780")
    ax.text(0.98, 0.97, "金牛", transform=ax.transAxes, ha="right", va="top", fontsize=10)
    ax.text(1.02, 0.97, "明星", transform=ax.transAxes, ha="left", va="top", fontsize=10)
    ax.text(0.98, 0.03, "瘦狗", transform=ax.transAxes, ha="right", va="bottom", fontsize=10)
    ax.text(1.02, 0.03, "问题", transform=ax.transAxes, ha="left", va="bottom", fontsize=10)
    ax.set_xlabel("相对市场份额（本品牌 ÷ 最大竞争者）")
    ax.set_ylabel("销量增长率（%）")
    ax.set_title("① 波士顿矩阵：气泡大小 = 总销量", fontsize=12)
    save_fig(fig, "A02_01_bcg.png")


# ==================== 2. RFM 模型 ====================
def rfm() -> pd.DataFrame:
    df = load(BASE + "1-2RFM模型.xlsx", sheet="原始数据")
    df["会员创建日期"] = pd.to_datetime(df["会员创建日期"])
    df["销售日期"] = pd.to_datetime(df["销售日期"])
    snap = df["销售日期"].max() + pd.Timedelta(days=1)   # 观察截止日

    g = df.groupby("用户编号").agg(
        R=("销售日期", lambda s: (snap - s.max()).days),  # 最近一次消费距今
        F=("流水号", "count"),                            # 消费频次
        M=("销售金额", "sum"),                            # 消费金额
    )
    g["R_s"] = _score(g["R"], ascending=False)            # R 越小越优
    g["F_s"] = _score(g["F"], ascending=True)
    g["M_s"] = _score(g["M"], ascending=True)
    g["RFM"] = g["R_s"].astype(str) + g["F_s"].astype(str) + g["M_s"].astype(str)

    def segment(r) -> str:
        if r.R_s >= 4 and r.F_s >= 4 and r.M_s >= 4:
            return "重要价值客户"
        if r.R_s >= 4 and r.F_s < 4:
            return "重要发展客户"
        if r.R_s < 4 and r.F_s >= 4:
            return "重要保持客户"
        if r.R_s < 4 and r.F_s < 4 and r.M_s >= 4:
            return "重要挽留客户"
        return "一般客户"

    g["客户类型"] = g.apply(segment, axis=1)
    print("\n客户分层结果：")
    print(g["客户类型"].value_counts().to_string())

    fig, ax = plt.subplots(figsize=(7, 5))
    colors = {"重要价值客户": "#E24B4A", "重要发展客户": "#EF9F27",
              "重要保持客户": "#378ADD", "重要挽留客户": "#7F77DD",
              "一般客户": NEUTRAL}
    for t, sub in g.groupby("客户类型"):
        ax.scatter(sub["F"], sub["M"], s=22, alpha=0.75,
                   label=f"{t}（{len(sub)}）", color=colors.get(t, "#888780"))
    ax.set_yscale("log")
    ax.set_xlabel("F · 消费频次")
    ax.set_ylabel("M · 消费金额（对数轴）")
    ax.set_title("② RFM 客户分层", fontsize=12)
    ax.legend(fontsize=8, frameon=False)
    save_fig(fig, "A02_02_rfm.png")
    return g


# ==================== 3. 用户忠诚度模型 ====================
def loyalty() -> None:
    df = load(BASE + "1-3用户忠诚度模型.xlsx", sheet="销售流水表")
    df["消费日期"] = pd.to_datetime(df["消费日期"])
    snap = df["消费日期"].max() + pd.Timedelta(days=1)

    g = df.groupby("会员编号").agg(
        最近消费=("消费日期", "max"),
        首购=("消费日期", "min"),
        次数=("订单编号", "count"),
        金额=("消费金额", "sum"),
    )
    g["生命周期天数"] = (g["最近消费"] - g["首购"]).dt.days + 1
    g["R"] = (snap - g["最近消费"]).dt.days
    g["月均频次"] = g["次数"] / (g["生命周期天数"] / 30).clip(lower=1)

    # 规则分层：最近消费越近 + 频次越高 → 忠诚度越高
    g["忠诚度"] = np.select(
        [(g["R"] <= 30) & (g["次数"] >= 3),
         (g["R"] <= 90) & (g["次数"] >= 2),
         (g["R"] <= 180)],
        ["高忠诚", "中忠诚", "低忠诚"],
        default="流失",
    )
    print("\n忠诚度分层：")
    print(g["忠诚度"].value_counts().to_string())

    order = ["高忠诚", "中忠诚", "低忠诚", "流失"]
    cnt = g["忠诚度"].value_counts().reindex(order).fillna(0)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
    bars = ax1.bar(cnt.index, cnt.values, width=0.55,
                   color="#9FE1CB", edgecolor="#0F6E56")
    ax1.bar_label(bars, fontsize=10)
    ax1.set_title("③-1 用户忠诚度分层分布", fontsize=12)
    ax1.set_ylabel("会员数")

    ax2.scatter(g["次数"], g["R"], s=18, alpha=0.5, color="#7F77DD")
    ax2.set_xlabel("消费次数")
    ax2.set_ylabel("最近消费距今（天）")
    ax2.invert_yaxis()
    ax2.set_title("③-2 频次 × 最近消费（越靠右上越活跃）", fontsize=12)
    save_fig(fig, "A02_03_loyalty.png")


# ==================== 4. 同期群分析 ====================
def cohort() -> None:
    """同期群分析 Cohort。

    注意：教材数据只覆盖 2020-07 一个月（注册日期 7/1~7/9），
    按「月」分组只会得到 1 个同期群、只能算出首月留存，矩阵退化成 1×1。
    因此这里把同期群粒度下钻到「周」，才能看到 0~4 周的留存衰减曲线。
    """
    df = load(BASE + "1-4同期群分析.xlsx", sheet="用户登录明细")
    df["注册日期"] = pd.to_datetime(df["注册日期"])
    df["登录时点"] = pd.to_datetime(df["登录时点"])

    # 同期群编号 = 注册所在周（周一为周起点）
    df["cohort"] = df["注册日期"].dt.to_period("W-SUN")
    # offset = 登录时点距注册日的整数周数
    df["offset"] = ((df["登录时点"] - df["注册日期"]).dt.days // 7).clip(lower=0)

    size = df.groupby("cohort")["用户编号"].nunique()          # 各期新增用户数
    mat = df.groupby(["cohort", "offset"])["用户编号"].nunique().unstack()
    ret = (mat.div(size, axis=0) * 100).round(1)               # 留存率矩阵
    print("\n各同期群新增用户数：")
    print(size.to_string())
    print("\n同期群留存率矩阵（%，按注册周分组）：")
    print(ret.to_string())

    labels = [f"第{i + 1}周" for i in range(len(ret.index))]
    fig, ax = plt.subplots(figsize=(9, 4.4))
    im = ax.imshow(ret.values, cmap="Blues", aspect="auto", vmin=0, vmax=100)
    ax.set_xticks(range(ret.shape[1]))
    ax.set_xticklabels([f"第 {int(c)} 周" for c in ret.columns])
    ax.set_yticks(range(ret.shape[0]))
    ax.set_yticklabels([f"{lab}\n({c})" for lab, c in zip(labels, ret.index)])
    for i in range(ret.shape[0]):
        for j in range(ret.shape[1]):
            v = ret.values[i, j]
            if pd.notna(v):
                ax.text(j, i, f"{v:.0f}%", ha="center", va="center", fontsize=9,
                        color="white" if v > 55 else "#2C2C2A")
    ax.set_xlabel("注册后第 N 周")
    ax.set_ylabel("同期群（注册周）")
    ax.set_title("④ 同期群留存率矩阵", fontsize=12)
    ax.grid(False)
    fig.colorbar(im, ax=ax, shrink=0.85, label="留存率 %")
    save_fig(fig, "A02_04_cohort.png")


# ==================== 5. 漏斗图 ====================
def funnel() -> None:
    """教材 2-1漏斗图.xlsx 是「成品图表文件」，数据嵌在图表对象里，
    read_excel 读不到数据区。此处用等价结构（阶段 → 人数）演示；
    若需用教材真实数据，从 Excel 图表的「选择数据源」把数值导出成两列即可。"""
    stages = ["曝光", "点击", "加购", "下单", "支付"]
    values = [10000, 4200, 1800, 900, 640]

    fig, ax = plt.subplots(figsize=(7, 4.4))
    ymax = max(values)
    for i, (s, v) in enumerate(zip(stages, values)):
        left = (ymax - v) / 2
        ax.barh(-i, v, left=left, height=0.62,
                color=plt.cm.Blues(0.32 + 0.14 * i), edgecolor="white", linewidth=1)
        rate = v / values[0] * 100
        step = "" if i == 0 else f"（环比 {v / values[i - 1] * 100:.1f}%）"
        ax.text(ymax * 1.03, -i, f"{s}  {v:,}   整体 {rate:.1f}% {step}",
                va="center", fontsize=9)
    ax.set_xlim(0, ymax * 1.02)
    ax.set_ylim(-len(stages) + 0.5, 0.75)
    ax.axis("off")
    ax.set_title("⑤ 转化漏斗：各环节流失诊断", fontsize=12)
    save_fig(fig, "A02_05_funnel.png")


# ==================== 6. 相关分析 ====================
def correlation() -> None:
    df = load(BASE + "3-1相关分析.xlsx", sheet="原始数据")
    r = df["x"].corr(df["y"])                    # 皮尔逊相关系数
    k, b = np.polyfit(df["x"], df["y"], 1)       # 一元线性回归 y = kx + b
    yhat = k * df["x"] + b
    r2 = 1 - ((df["y"] - yhat) ** 2).sum() / ((df["y"] - df["y"].mean()) ** 2).sum()
    print(f"\n相关系数 r = {r:.4f}，拟合优度 R² = {r2:.4f}，斜率 = {k:.4f}")

    fig, ax = plt.subplots(figsize=(7, 4.8))
    ax.scatter(df["x"], df["y"], s=26, alpha=0.6, color="#7F77DD", label="观测值")
    xs = np.linspace(df["x"].min(), df["x"].max(), 100)
    ax.plot(xs, k * xs + b, color="#A32D2D", lw=1.6,
            label=f"回归线 y={k:.2f}x+{b:.1f}")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(f"⑥ 相关分析：r = {r:.3f}，R² = {r2:.3f}", fontsize=12)
    ax.legend(frameon=False, fontsize=9)
    save_fig(fig, "A02_06_correlation.png")


def main() -> None:
    title("A02 六大基础分析范式")
    bcg()
    g = rfm()
    save_table(g.reset_index(), "A02_rfm_result.csv")
    loyalty()
    cohort()
    funnel()
    correlation()
    print("\n六个范式全部完成，共输出 8 张图。")


if __name__ == "__main__":
    main()
