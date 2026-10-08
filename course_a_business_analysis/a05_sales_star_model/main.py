"""
A05 分省销售分析：星型模型 + DAX 度量值
教材定位：《商业数据分析》第 2 章-5 PowerBI 基本操作 / 案例1（分省销售分析.pbix）

【内涵解读】
这是教材里最接近真实项目的一个案例：5 个 csv 恰好构成标准的
「1 张事实表 + 4 张维度表」结构。

  订单表.csv         OrderID, EmployeeID, ShipProvince, OrderDate    （事实表头）
  订单表明细表.csv   订单ID, 产口ID*, 销售金额, 销售成本              （事实表明细）
  商品表.csv         ProductID, ProductName, CategoryID              （商品维度）
  商品类型表.csv     CategoryID, CategoryName, Description           （品类维度）
  雇员表.csv         EmployeeID, FullName, Age, gender, City, store  （雇员维度）

  * 教材原表列名写作「产口ID」（错别字），代码按原样读取后再 rename。

教材要做的三件事 → 本实验的等价动作：
  1) 建立表间关系       → merge 逐跳挂接维度表
  2) 写 DAX 度量值      → groupby / pivot_table / rank
  3) 出矩阵与图表       → matplotlib

运行：python course_a_business_analysis/a05_sales_star_model/main.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from common.utils import load, report_head, save_fig, title  # noqa: E402

D = ""


def build_model() -> pd.DataFrame:
    """构建星型模型：事实表(订单 × 明细) 为中心，逐跳挂接维度表。"""
    orders = load(D + "订单表.csv")                 # 实测为 GBK 编码，load 已自动兜底
    detail = load(D + "订单表明细表.csv")           # 实测为 GBK 编码
    products = load(D + "商品表.csv")
    categories = load(D + "商品类型表.csv")
    employees = load(D + "雇员表.csv")

    # 统一主外键列名（教材原表把「产品ID」写成了「产口ID」）
    detail = detail.rename(columns={"订单ID": "OrderID", "产口ID": "ProductID"})
    orders["OrderDate"] = pd.to_datetime(orders["OrderDate"])

    # 事实表：订单头 + 订单明细（明细粒度更细，是分析的基本粒度）
    fact = detail.merge(orders, on="OrderID", how="left")
    fact["毛利"] = fact["销售金额"] - fact["销售成本"]

    # 维度表：商品 → 品类（两级），雇员
    dim_product = products.merge(categories, on="CategoryID", how="left")
    fact = fact.merge(dim_product, on="ProductID", how="left")
    fact = fact.merge(employees, on="EmployeeID", how="left")
    return fact


def main() -> None:
    title("A05 分省销售分析：星型模型 + 度量值")

    fact = build_model()
    report_head(fact[["OrderID", "OrderDate", "ShipProvince", "ProductName",
                      "CategoryName", "FullName", "销售金额", "销售成本", "毛利"]],
                5, "建模后的分析宽表")

    # ---------- 度量值 A：总销售额 / 总毛利 / 毛利率 ----------
    # 等价 DAX：SUM(销售金额) / DIVIDE(SUM(毛利), SUM(销售金额))
    total_sales = fact["销售金额"].sum()
    total_profit = fact["毛利"].sum()
    print(f"\n【度量值 A】总销售额 {total_sales:,.0f} 元 | 总毛利 {total_profit:,.0f} 元 "
          f"| 毛利率 {total_profit / total_sales:.2%}")

    # ---------- 度量值 B：分省销售额 + 排名 ----------
    # 等价 DAX：SUMMARIZE + RANKX(ALL(省), SUM(销售金额))
    prov = (fact.groupby("ShipProvince")
                .agg(销售额=("销售金额", "sum"),
                     毛利=("毛利", "sum"),
                     订单数=("OrderID", "nunique"))
                .assign(销售额排名=lambda d: d["销售额"].rank(ascending=False).astype(int))
                .assign(毛利率=lambda d: (d["毛利"] / d["销售额"] * 100).round(2))
                .sort_values("销售额", ascending=False))
    print("\n【度量值 B】分省销售：")
    print(prov.to_string())

    # ---------- 度量值 C：省份 × 品类 交叉表 ----------
    cross = fact.pivot_table(index="ShipProvince", columns="CategoryName",
                             values="销售金额", aggfunc="sum", fill_value=0)
    # 度量值 D：各省销售额占比 ← 等价 DAX DIVIDE(SUM(x), CALCULATE(SUM(x), ALL(省)))
    cross["合计"] = cross.sum(axis=1)
    cross["占比%"] = (cross["合计"] / cross["合计"].sum() * 100).round(2)
    print("\n【度量值 C+D】省份 × 品类交叉表：")
    print(cross.to_string())

    # ---------- 度量值 E：月度销售额与同比 ----------
    # 等价 DAX：SAMEPERIODLASTYEAR + 时间智能
    fact["年"] = fact["OrderDate"].dt.year
    fact["月"] = fact["OrderDate"].dt.month
    monthly = fact.groupby(["年", "月"])["销售金额"].sum().unstack(0)
    yoy = monthly.pct_change() * 100
    print("\n【度量值 E】月度同比（%）：")
    print(yoy.round(1).to_string())

    # ---------- 度量值 F：雇员业绩排行 ----------
    emp = (fact.groupby(["FullName", "City"])
               .agg(销售额=("销售金额", "sum"), 订单数=("OrderID", "nunique"))
               .sort_values("销售额", ascending=False))
    print("\n【度量值 F】雇员业绩 Top 10：")
    print(emp.head(10).to_string())

    # ---------------- 可视化 ----------------
    fig = plt.figure(figsize=(13, 8))

    ax1 = fig.add_subplot(2, 2, 1)
    top = prov["销售额"].head(10)[::-1]
    ax1.barh(top.index, top.values, color="#85B7EB", edgecolor="#185FA5")
    ax1.bar_label(ax1.containers[0], fmt="%.0f", fontsize=8)
    ax1.set_title("① 分省销售额 Top 10", fontsize=12)

    ax2 = fig.add_subplot(2, 2, 2)
    cat = fact.groupby("CategoryName")["销售金额"].sum().sort_values()
    ax2.barh(cat.index, cat.values, color="#9FE1CB", edgecolor="#0F6E56")
    ax2.set_title("② 各品类销售额", fontsize=12)

    ax3 = fig.add_subplot(2, 2, 3)
    cats = list(cross.columns[:-2])
    for c in cats[:5]:
        ax3.plot(monthly.index, fact.loc[fact["CategoryName"] == c]
                 .groupby("月")["销售金额"].sum(), marker="o", ms=3, label=c)
    ax3.set_xlabel("月份")
    ax3.set_ylabel("销售额")
    ax3.set_title("③ 主要品类月度走势（下钻到品类）", fontsize=12)
    ax3.legend(frameon=False, fontsize=8)

    ax4 = fig.add_subplot(2, 2, 4)
    top_emp = emp.head(8)[::-1].reset_index()
    labels = top_emp["FullName"] + "（" + top_emp["City"] + "）"
    ax4.barh(labels, top_emp["销售额"], color="#EF9F27", edgecolor="#854F0B")
    ax4.set_title("④ 雇员业绩 Top 8", fontsize=12)
    ax4.tick_params(labelsize=8)

    fig.tight_layout()
    save_fig(fig, "A05_sales_dashboard.png")
    print("\n分析完成。")


if __name__ == "__main__":
    main()
