"""
A06 服装零售销售分析看板（多表维度建模实战）
教材定位：《商业数据分析》第 2 章-5 PowerBI 基本操作 / 案例2（【报表】-服装零售分析.pbix）

【内涵解读】
这是教材里表数量最多的案例（12 张表），完整的维度建模实战。
核心是把「订单 → 明细 → SKU → 款号」这条链走通，把商品属性（成本、大类）
展开到事实表上，再挂「店铺 / 员工 / 会员」做对比与目标达成分析。

表结构与角色：
  零售单 / 零售单明细      事实表（订单头 + 明细）
  SKU表 / 款号表           商品维度（两级：SKU → 款号 → 成本）
  店铺表 / 员工表         门店与人员维度
  店铺月目标表             目标表（用于达成率）
  vip表                    会员维度
  属性表 / 颜色表 / 尺码表  商品属性维度

【迁移关键点】
多表 join 的顺序有讲究：必须从细粒度表（明细）出发挂表头，再挂维度。
反过来会因「一对多」把行数吹大（笛卡尔积），这是维度建模最常踩的坑。

运行：python course_a_business_analysis/a06_retail_dashboard/main.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from common.style import NEGATIVE, POSITIVE  # noqa: E402
from common.utils import load_sheets, report_head, save_fig, save_table, title  # noqa: E402

FE = "服装零售-原始数据.xlsx"


def build_model(sheets: dict) -> pd.DataFrame:
    """按「明细 → 订单头 → 商品属性 → 门店」的顺序逐跳挂接。"""
    orders = sheets["零售单"]
    detail = sheets["零售单明细"]
    orders["订单日期"] = pd.to_datetime(orders["订单日期"])

    # 第 1 跳：明细（细粒度）挂订单头；丢掉同名列避免 merge 后出现 _x/_y
    head = orders.drop(columns=["数量", "零售金额", "成交金额"])
    fact = detail.merge(head, on="订单id", how="left", suffixes=("", "_订单"))

    # 第 2 跳：沿 SKU → 款号 拿到成本
    # 明细里的「商品id」实际就是 SKU 表的「SKUid」
    sku = sheets["SKU表"].merge(sheets["款号表"][["款号id", "成本"]],
                                on="款号id", how="left")
    fact = fact.merge(sku.rename(columns={"SKUid": "商品id"}), on="商品id", how="left")

    # 第 3 跳：挂门店维度
    store = sheets["店铺表"][["店铺id", "店铺名称", "商圈", "店铺面积"]]
    fact = fact.merge(store, on="店铺id", how="left")

    # 第 4 跳：挂员工维度（取员工姓名）
    fact = fact.merge(sheets["员工表"][["员工id", "员工姓名"]], on="员工id", how="left")

    fact["年月"] = fact["订单日期"].dt.strftime("%Y%m")
    # 成本 = 单件成本 × 数量；成交金额来自明细表
    fact["毛利"] = fact["成交金额"] - fact["成本"].fillna(0) * fact["数量"]
    return fact


def main() -> None:
    title("A06 服装零售销售分析看板")

    sheets = load_sheets(FE)
    print("数据文件含表：", list(sheets.keys()))

    fact = build_model(sheets)
    cols = ["订单id", "订单日期", "店铺名称", "商圈", "员工姓名",
            "商品id", "数量", "折扣率", "标准价", "成交金额", "成本", "毛利"]
    report_head(fact[[c for c in cols if c in fact.columns]], 5, "建模后的事实表")

    # ---------- KPI 卡片（等价 Power BI 的「卡片」视觉对象） ----------
    order_cnt = fact["订单id"].nunique()
    kpi = {
        "总成交金额": fact["成交金额"].sum(),
        "总零售金额": fact["零售金额"].sum() if "零售金额" in fact else np.nan,
        "总销量": fact["数量"].sum(),
        "订单数": order_cnt,
        "客单价": fact["成交金额"].sum() / order_cnt,
        "连带率": fact["数量"].sum() / order_cnt,
        "毛利率": fact["毛利"].sum() / fact["成交金额"].sum(),
    }
    print("\n【看板 KPI】")
    for k, v in kpi.items():
        print(f"  {k:8s}: {v:,.2f}")

    # ---------- 可视化 ----------
    fig = plt.figure(figsize=(13, 8))

    # ① 店铺成交金额排行
    ax1 = fig.add_subplot(2, 2, 1)
    s = fact.groupby("店铺名称")["成交金额"].sum().sort_values().tail(12)
    ax1.barh(s.index, s.values, color="#85B7EB", edgecolor="#185FA5")
    ax1.set_title("① 各店铺成交金额", fontsize=12)
    ax1.tick_params(labelsize=8)

    # ② 月度成交金额趋势
    ax2 = fig.add_subplot(2, 2, 2)
    m = fact.groupby("年月")["成交金额"].sum()
    ax2.plot(m.index, m.values, marker="o", color="#378ADD")
    ax2.set_title("② 月度成交金额趋势", fontsize=12)
    ax2.tick_params(axis="x", rotation=60, labelsize=8)
    ax2.set_ylabel("成交金额")

    # ③ 商圈构成
    ax3 = fig.add_subplot(2, 2, 3)
    c = fact.groupby("商圈")["成交金额"].sum()
    ax3.pie(c, labels=c.index, autopct="%1.1f%%",
            colors=plt.cm.Blues(np.linspace(0.35, 0.85, len(c))),
            wedgeprops=dict(width=0.45), textprops=dict(fontsize=8))
    ax3.set_title("③ 商圈成交占比", fontsize=12)

    # ④ 店铺目标达成率 ← 等价 DAX DIVIDE(实际, 目标)
    ax4 = fig.add_subplot(2, 2, 4)
    target = sheets["店铺月目标表"].groupby("店铺id")["基础目标"].sum().rename("目标")
    actual = fact.groupby("店铺id")["成交金额"].sum().rename("实际")
    cmp_df = pd.concat([target, actual], axis=1).fillna(0).reset_index()
    cmp_df["达成率"] = cmp_df["实际"] / cmp_df["目标"].replace(0, np.nan) * 100
    name_map = sheets["店铺表"].set_index("店铺id")["店铺名称"]
    cmp_df["店铺"] = cmp_df["店铺id"].map(name_map)
    cmp_df = cmp_df.dropna(subset=["达成率"]).sort_values("达成率").tail(12)
    # 达标为绿、未达标为红（中式报表惯例：好=绿，差=红；注意与涨跌配色语义不同）
    colors = [NEGATIVE if r >= 100 else POSITIVE for r in cmp_df["达成率"]]
    ax4.barh(cmp_df["店铺"], cmp_df["达成率"], color=colors, edgecolor="white")
    ax4.axvline(100, ls="--", color="#444441", lw=0.9)
    ax4.set_title("④ 店铺基础目标达成率（%，虚线=100%）", fontsize=12)
    ax4.tick_params(labelsize=8)

    fig.tight_layout()
    save_fig(fig, "A06_retail_dashboard.png")

    # 导出店铺级汇总，便于核对与二次分析
    store_summary = (fact.groupby("店铺名称")
                         .agg(成交金额=("成交金额", "sum"),
                              销量=("数量", "sum"),
                              订单数=("订单id", "nunique"),
                              毛利率=("毛利", "sum")))
    store_summary["客单价"] = (store_summary["成交金额"] / store_summary["订单数"]).round(1)
    save_table(store_summary.reset_index(), "A06_store_summary.csv")
    print("\n看板完成。")


if __name__ == "__main__":
    main()
