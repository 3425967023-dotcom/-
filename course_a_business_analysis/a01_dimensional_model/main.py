"""
A01 维度建模（星型模型）
教材定位：《商业数据分析》第 1 章 数据分析思维 ——「维度模型演示」文件夹

【内涵解读】
教材用 Power BI 演示维度模型：把数据拆成
  · 事实表：记录「发生了什么」，只存外键 + 度量值（可加总的数字）
  · 维度表：描述「谁 / 在哪 / 何时」，存属性（可用来切片、分组的文字）
教材特别注明「不建议用 Power BI 操作关系型数据模型」，
原因是关系模型要做多跳 JOIN，而维度模型只需一跳，查询与理解成本都低得多。

【迁移要点】
Power BI 的「建立关系 → 拖字段 → 矩阵自动筛选」
  等价于 pandas 的「merge 维度表 → groupby / pivot_table」。
本实验只用 pandas 的 4 个动作完成：
  1) 事实表丢掉重复属性列
  2) merge 维度表（一跳关联）
  3) 按维度切片聚合（pivot_table）
  4) 计算份额（手工实现 DAX 的 ALL() 筛选上下文）

运行：python course_a_business_analysis/a01_dimensional_model/main.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from common.utils import load, report_head, save_fig, save_table, title  # noqa: E402

# 教材数据集：1 张事实表 + 5 张维度表（典型星型模型）
FE = "商场销售数据表.xlsx"


def build_star_schema():
    """构建星型模型，返回事实表与维度表集合。"""
    fact = load(FE, sheet="产品销售数据表")
    # 原表列名有前导空格（如 ' 销售单价'），统一去掉
    fact.columns = [c.strip() for c in fact.columns]
    fact["订单日期"] = pd.to_datetime(fact["订单日期"])

    dim_date = load(FE, sheet="日期表")          # 日期维度
    dim_city = load(FE, sheet="商铺城市", dtype={"城市编码": str})  # 地理维度
    dim_product = load(FE, sheet="产品信息表")   # 产品维度
    dim_brand = load(FE, sheet="品牌")           # 品牌维度

    # 产品维度再挂一层品牌维度 → 形成「雪花」结构
    dim_product = dim_product.merge(dim_brand, on="品牌名称", how="left")
    return fact, dim_date, dim_city, dim_product


def main() -> None:
    title("A01 维度建模：星型模型聚合")

    fact, dim_date, dim_city, dim_product = build_star_schema()
    report_head(fact, 3, "事实表（产品销售数据表）")
    report_head(dim_product, 3, "产品维度（已挂接品牌维度）")

    # ---- 第 1 步：事实表丢掉与维度表重复的属性列 ----
    # 这一步是「星型」与「宽表」的本质区别：属性不留在事实表
    dup_cols = ["品牌名称", "产品名称", "产品类别", "销售单价"]
    fact_core = fact.drop(columns=[c for c in dup_cols if c in fact.columns])

    # ---- 第 2 步：一跳关联 ----
    # 注意：事实表里产品编号是小写（a001），维度表里是大写（A001），
    # 直接 merge 会全部匹配不上、品牌变成 NaN，必须先统一大小写。
    fact_core["产品编号"] = fact_core["产品编号"].astype(str).str.strip().str.upper()
    dim_product["产品编号"] = dim_product["产品编号"].astype(str).str.strip().str.upper()
    fact_core["商铺城市"] = fact_core["商铺城市"].astype(str).str.strip()
    dim_city["商铺城市"] = dim_city["商铺城市"].astype(str).str.strip()

    df = fact_core.merge(dim_product, on="产品编号", how="left")
    df = df.merge(dim_city, on="商铺城市", how="left")
    unmatched = df["品牌名称"].isna().sum()
    if unmatched:
        print(f"[提示] 有 {unmatched} 行未匹配到产品维度，请检查主外键")

    df["年度"] = df["订单日期"].dt.year
    df["季度"] = df["订单日期"].dt.quarter
    df["月份"] = df["订单日期"].dt.month

    # ---- 第 3 步：度量值 1 —— 各品牌 × 年度销售额 ----
    # 等价 DAX：SUM(销售额) + 矩阵（行 = 品牌，列 = 年度）
    piv = df.pivot_table(index="品牌名称", columns="年度",
                         values="销售额", aggfunc="sum", fill_value=0)
    print("\n度量值 1 · 各品牌年度销售额：")
    print(piv.to_string())

    # ---- 第 4 步：度量值 2 —— 品牌份额 ----
    # 等价 DAX：DIVIDE(SUM(x), CALCULATE(SUM(x), ALL(品牌)))
    # 关键：pivot.sum(axis=0) 就是「去掉品牌分组、对整列求和」，
    #      这正是 DAX 中 ALL() 移除筛选上下文的手工实现。
    share = (piv.div(piv.sum(axis=0), axis=1) * 100).round(2)
    print("\n度量值 2 · 品牌份额(%)（ALL() 筛选上下文的等价实现）：")
    print(share.to_string())

    # ---- 额外度量值：城市 × 季度，用于判断季节性 ----
    city_q = df.pivot_table(index="商铺城市", columns="季度",
                            values="销售额", aggfunc="sum")
    print("\n附加度量值 · 城市 × 季度销售额：")
    print(city_q.to_string())

    # ---- 可视化 ----
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.2), width_ratios=[1.1, 1])
    piv.plot(kind="bar", ax=ax1, width=0.8, colormap="Blues", edgecolor="white")
    ax1.set_title("各品牌年度销售额（星型模型聚合）", fontsize=12)
    ax1.set_xlabel("品牌")
    ax1.set_ylabel("销售额（元）")
    ax1.legend(title="年度", frameon=False, fontsize=8)
    ax1.tick_params(axis="x", rotation=0, labelsize=9)

    city_q.plot(kind="bar", ax=ax2, width=0.75, colormap="Greens", edgecolor="white")
    ax2.set_title("各城市季度销售额", fontsize=12)
    ax2.set_xlabel("商铺城市")
    ax2.set_ylabel("销售额（元）")
    ax2.legend(title="季度", frameon=False, fontsize=8)
    ax2.tick_params(axis="x", rotation=20, labelsize=9)

    fig.tight_layout()
    save_fig(fig, "A01_star_schema_sales.png")

    # 导出宽表，作为后续实验的输入（等价 Power BI 的「发布数据集」）
    save_table(df, "A01_wide_table.csv")

    print(f"\n结论：星型模型下 6 张表被合并为 1 张分析宽表（{df.shape[0]} 行 × {df.shape[1]} 列），"
          f"此后所有分析都只需基于它做 groupby。")


if __name__ == "__main__":
    main()
