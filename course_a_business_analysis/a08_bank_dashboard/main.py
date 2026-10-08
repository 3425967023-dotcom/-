"""
A08 银行理财业务看板 + 渠道归因
教材定位：《商业数据分析》第 5 章 业务数据分析
  · 第5章 PowerBI业务看板案例-银行案例（案例结果.pbix）
  · 第5章 WPS归因分析案例-银行案例（归因分析 - 结果.xlsx）

【内涵解读】
案例 A：银行理财销售看板
  教材给的是「构建 BI 报表帮助客户经理快速了解同类客群的购买倾向」。
  业务背景（源表「业务描述」sheet 原文）：
    「某分支行本月理财产品的销售目标为 2500 万……假设本月共 31 天，
      当前数据为本月 29 日的时点数据（本数据仅包含当月）。」
  → 因此分析必须包含「目标达成预警」：按 29 天日均外推全月，判断能否达标。
  技术主干 = 三张说明表（维度表）翻译编码 + 多维切片。

  销售数据字段：风险编号, 购买目的, 家庭年收入, 品类编号, 年龄, 性别,
                选择本行的原因, 学历编号, 购买金额, 期限, 收益
  维度表：风险偏好说明表 / 品类说明表 / 学历说明表

案例 B：渠道归因
  贷款申请表字段：申请书编号（主键）, 申请日期, 申请渠道, 申请年月
  业务背景：银行上线手机银行 3.0 + 500 台智能自助机，开放自助贷款申请，
  需要判断「申请量增长到底来自哪个渠道」。
  → 用因素分解法把增量拆成「量效应」与「结构效应」。

运行：python course_a_business_analysis/a08_bank_dashboard/main.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from common.utils import load_sheets, report_head, save_fig, save_table, title  # noqa: E402

BANK_FE = "银行案例数据 - 学员用.xlsx"
ATTR_FE = "归因分析 - 结果.xlsx"

TARGET = 25_000_000       # 本月销售目标 2500 万元
DAYS_ELAPSED = 29         # 当前数据为 29 日时点
DAYS_TOTAL = 31           # 本月共 31 天


def _sort_by_leading_number(series: pd.Series) -> list:
    """把「18-30岁」「31-40岁」这类分箱标签按起始数字排序。"""

    def key(x):
        digits = "".join(ch for ch in str(x) if ch.isdigit())
        return int(digits[:2]) if digits else 0
    return sorted(series.unique(), key=key)


# ==================== 案例 A：银行理财看板 ====================
def bank_dashboard() -> pd.DataFrame:
    sheets = load_sheets(BANK_FE)
    print("数据文件含表：", list(sheets.keys()))

    sales = sheets["销售数据"]
    risk = sheets["风险偏好说明表"]      # 风险编号 → 风险说明
    categ = sheets["品类说明表"]         # 品类编号 → 品类名称
    edu = sheets["学历说明表"]           # 学历编号 → 学历名称

    # 维度表翻译：把编码换成业务含义（等价 Power BI 的关系 + 按列显示）
    df = (sales.merge(risk, on="风险编号", how="left")
               .merge(categ, on="品类编号", how="left")
               .merge(edu, on="学历编号", how="left"))
    report_head(df, 3, "翻译维度后的宽表")

    # ---------- 目标达成预警 ----------
    total = df["购买金额"].sum()
    progress = total / TARGET * 100
    run_rate = total / DAYS_ELAPSED * DAYS_TOTAL      # 按当前日均外推全月
    gap = max(TARGET - run_rate, 0)
    print(f"\n【目标达成】累计销售 {total:,.0f} 元，达成 {progress:.1f}%")
    print(f"  已过 {DAYS_ELAPSED}/{DAYS_TOTAL} 天，按当前日均外推全月 {run_rate:,.0f} 元")
    print(f"  → 预计{'达标' if run_rate >= TARGET else '不达标'}，"
          f"缺口 {gap:,.0f} 元，剩余 {DAYS_TOTAL - DAYS_ELAPSED} 天日均需 "
          f"{gap / (DAYS_TOTAL - DAYS_ELAPSED):,.0f} 元")

    # ---------- 多维切片 ----------
    by_age = (df.groupby("年龄")["购买金额"].sum()
                .reindex(_sort_by_leading_number(df["年龄"])))
    by_cat = df.groupby("品类名称")["购买金额"].sum().sort_values(ascending=False)
    by_risk = df.groupby("风险说明")["购买金额"].sum()
    hm = df.pivot_table(index="风险说明", columns="购买目的",
                        values="购买金额", aggfunc="sum", fill_value=0)
    sg = df.groupby(["性别", "学历名称"])["购买金额"].sum().unstack(fill_value=0)
    by_term = df.groupby("期限")["购买金额"].sum()

    print("\n【各年龄段购买金额】")
    print(by_age.to_string())
    print("\n【风险偏好 × 购买目的】")
    print(hm.to_string())

    # ---------- 可视化 ----------
    fig = plt.figure(figsize=(13.5, 8.5))

    # ① 达成进度条
    ax1 = fig.add_subplot(2, 3, 1)
    ax1.barh([0], [TARGET], color="#F1EFE8", edgecolor="#B4B2A9", height=0.5)
    ax1.barh([0], [total], color="#1D9E75" if total >= TARGET else "#EF9F27",
             height=0.5, zorder=3)
    ax1.text(total, 0.42, f"{progress:.1f}%", fontsize=10, ha="center")
    ax1.set_xlim(0, TARGET * 1.05)
    ax1.set_yticks([])
    ax1.set_title("① 目标达成进度", fontsize=11)

    # ② 各年龄段购买金额
    ax2 = fig.add_subplot(2, 3, 2)
    ax2.bar(by_age.index, by_age.values, color="#85B7EB", edgecolor="#185FA5")
    ax2.set_title("② 各年龄段购买金额", fontsize=11)
    ax2.tick_params(axis="x", rotation=25, labelsize=8)
    ax2.set_ylabel("购买金额")

    # ③ 品类构成
    ax3 = fig.add_subplot(2, 3, 3)
    ax3.pie(by_cat, labels=by_cat.index, autopct="%1.1f%%",
            colors=plt.cm.Blues(np.linspace(0.35, 0.85, len(by_cat))),
            wedgeprops=dict(width=0.45), textprops=dict(fontsize=8))
    ax3.set_title("③ 品类构成", fontsize=11)

    # ④ 风险偏好 × 购买目的 热力图
    ax4 = fig.add_subplot(2, 3, 4)
    im = ax4.imshow(hm.values, cmap="Blues", aspect="auto")
    ax4.set_xticks(range(hm.shape[1]))
    ax4.set_xticklabels(hm.columns, rotation=40, ha="right", fontsize=7)
    ax4.set_yticks(range(hm.shape[0]))
    ax4.set_yticklabels(hm.index, fontsize=7)
    ax4.set_title("④ 风险偏好 × 购买目的", fontsize=11)
    ax4.grid(False)
    fig.colorbar(im, ax=ax4, shrink=0.8)

    # ⑤ 性别 × 学历
    ax5 = fig.add_subplot(2, 3, 5)
    sg.plot(kind="bar", stacked=True, ax=ax5, colormap="Greens",
            width=0.68, edgecolor="white")
    ax5.set_title("⑤ 性别 × 学历 购买金额", fontsize=11)
    ax5.legend(frameon=False, fontsize=6)
    ax5.tick_params(axis="x", rotation=0, labelsize=8)
    ax5.set_xlabel("")

    # ⑥ 期限分布
    ax6 = fig.add_subplot(2, 3, 6)
    ax6.bar(by_term.index.astype(str), by_term.values,
            color="#9FE1CB", edgecolor="#0F6E56")
    ax6.set_title("⑥ 产品期限分布", fontsize=11)
    ax6.set_xlabel("期限（年）")
    ax6.tick_params(labelsize=8)

    fig.tight_layout()
    save_fig(fig, "A08_bank_dashboard.png")
    return df


# ==================== 案例 B：渠道归因 ====================
def channel_attribution() -> pd.DataFrame:
    sheets = load_sheets(ATTR_FE)
    df = sheets["贷款申请表"]
    report_head(df, 3, "贷款申请表")

    df["申请日期"] = pd.to_datetime(df["申请日期"], errors="coerce")
    df["申请年月"] = df["申请日期"].dt.to_period("M")

    piv = (df.pivot_table(index="申请年月", columns="申请渠道",
                          values="申请书编号（主键）", aggfunc="count", fill_value=0)
             .sort_index())
    print("\n【各渠道月度申请量】")
    print(piv.to_string())

    if len(piv) < 2:
        print("\n数据不足两期，无法做增量归因分解（教材数据只有单月时属正常）。")
        fig, ax = plt.subplots(figsize=(7.6, 4.2))
        total_by_ch = piv.iloc[-1].sort_values()
        ax.barh(total_by_ch.index, total_by_ch.values,
                color="#85B7EB", edgecolor="#185FA5")
        ax.bar_label(ax.containers[0], fontsize=9)
        ax.set_title("各申请渠道申请量（单期）", fontsize=12)
        ax.set_xlabel("申请量（件）")
        save_fig(fig, "A08_attribution.png")
        return piv

    prev, cur = piv.iloc[-2], piv.iloc[-1]
    tot_prev, tot_cur = prev.sum(), cur.sum()
    delta = tot_cur - tot_prev

    # 因素分解法：
    #   量效应   = 上期结构 × 总量增量      （渠道结构不变时，总量变化的贡献）
    #   结构效应 = 结构变化 × 上期总量      （总量不变时，渠道占比变化的贡献）
    # 两者之和恒等于总增量，可据此校验。
    w_prev, w_cur = prev / tot_prev, cur / tot_cur
    result = pd.DataFrame({
        "上期": prev, "本期": cur, "增量": cur - prev,
        "量效应": (w_prev * delta).round(1),
        "结构效应": ((w_cur - w_prev) * tot_prev).round(1),
    })
    result["贡献占比%"] = (result["增量"] / delta * 100).round(1)
    print("\n【渠道归因分解】")
    print(result.to_string())
    print(f"\n校验：量效应 + 结构效应 = {result['量效应'].sum() + result['结构效应'].sum():.1f}，"
          f"总增量 = {delta}")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 4.2))
    pivot_plot = piv.astype(float)
    pivot_plot.index = pivot_plot.index.astype(str)
    pivot_plot.plot(ax=ax1, marker="o")
    ax1.set_title("① 各渠道申请量趋势", fontsize=12)
    ax1.legend(frameon=False, fontsize=8)
    ax1.set_xlabel("")

    x = np.arange(len(result))
    ax2.bar(x - 0.2, result["量效应"], 0.4, label="量效应", color="#85B7EB")
    ax2.bar(x + 0.2, result["结构效应"], 0.4, label="结构效应", color="#EF9F27")
    ax2.axhline(0, color="#444441", lw=0.8)
    ax2.set_xticks(x)
    ax2.set_xticklabels(result.index, rotation=20, fontsize=8)
    ax2.set_title("② 增量归因：量效应 vs 结构效应", fontsize=12)
    ax2.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    save_fig(fig, "A08_attribution.png")
    save_table(result.reset_index(), "A08_attribution_result.csv")
    return result


def main() -> None:
    title("A08 银行理财业务看板 + 渠道归因")
    bank_dashboard()
    print()
    channel_attribution()
    print("\n完成。")


if __name__ == "__main__":
    main()
