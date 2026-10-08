"""
A12 指标体系构建与管理（结构化建模）
教材定位：《商业数据分析》第 7 章 指标体系构建方法 + 第 13 章 指标体系管理
         （指标体系设计模板.xlsx、基础数据标准编制模板.xlsx、指标数据标准编制模板.xlsx）

【内涵解读】
第 7、13 章是方法论章，没有数值型案例，产出物是「模板」。
迁移方式是：把指标体系从一张 Excel 模板，变成**可校验的数据结构**（指标字典）。

这恰恰是数据治理里指标管理的标准做法：指标一旦成为代码，
就能做自动化校验（编号唯一、依赖闭环、口径完整、责任人明确）。

【指标分层口径】（教材第 7 章）
  原子指标：不可再分的基础度量（如 销售金额、订单数）
  派生指标：由原子指标经四则运算得到（如 客单价 = 销售金额 / 订单数）
  复合指标：由多个派生指标再组合（如 目标达成率）

运行：python course_a_business_analysis/a12_indicator_system/main.py
"""

from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

import pandas as pd  # noqa: E402

from common.utils import save_table, title  # noqa: E402

# 指标体系定义（对应教材「指标体系设计模板.xlsx」的字段结构）
INDICATORS = [
    dict(指标编号="M001", 指标名称="销售金额", 指标类型="原子指标",
         业务口径="已完成支付订单的实付金额合计", 计算方式="SUM(订单实付金额)",
         数据来源="订单表", 统计周期="日/月/年", 责任人="电商组"),
    dict(指标编号="M002", 指标名称="订单数", 指标类型="原子指标",
         业务口径="已完成支付的订单数量", 计算方式="COUNT(DISTINCT 订单号)",
         数据来源="订单表", 统计周期="日/月/年", 责任人="电商组"),
    dict(指标编号="M003", 指标名称="客单价", 指标类型="派生指标",
         业务口径="销售金额 ÷ 订单数", 计算方式="M001 / M002",
         数据来源="—", 统计周期="日/月/年", 责任人="电商组"),
    dict(指标编号="M004", 指标名称="毛利率", 指标类型="派生指标",
         业务口径="(销售金额 - 销售成本) ÷ 销售金额",
         计算方式="(M001 - 销售成本) / M001",
         数据来源="订单明细表", 统计周期="月/年", 责任人="财务组"),
    dict(指标编号="M005", 指标名称="目标达成率", 指标类型="复合指标",
         业务口径="销售金额 ÷ 销售目标", 计算方式="M001 / 目标值",
         数据来源="目标表", 统计周期="月", 责任人="运营组"),
    dict(指标编号="M006", 指标名称="连带率", 指标类型="派生指标",
         业务口径="销售件数 ÷ 订单数", 计算方式="销售件数 / M002",
         数据来源="订单明细表", 统计周期="日/月", 责任人="零售组"),
]


def validate(ind: pd.DataFrame) -> pd.DataFrame:
    """指标口径校验（对应教材第 13 章「指标数据标准」的合规要求）：
       1) 指标编号唯一
       2) 业务口径、数据来源、责任人非空
       3) 派生/复合指标引用的指标编号必须已定义（依赖闭环）
    """
    problems: list[str] = []
    ids = set(ind["指标编号"])

    if len(ids) != len(ind):
        dup = ind["指标编号"][ind["指标编号"].duplicated()].tolist()
        problems.append(f"存在重复的指标编号：{dup}")

    for _, r in ind.iterrows():
        for col in ["业务口径", "数据来源", "责任人", "统计周期"]:
            if pd.isna(r[col]) or str(r[col]).strip() == "":
                problems.append(f"{r['指标编号']} 的「{col}」为空")
        # 计算方式里引用到的 Mxxx 必须已定义
        for ref in re.findall(r"M\d{3}", str(r["计算方式"])):
            if ref not in ids:
                problems.append(f"{r['指标编号']} 引用了未定义的指标 {ref}")
        # 派生/复合指标不应被标为原子指标
        if r["指标类型"] == "原子指标" and re.search(r"M\d{3}", str(r["计算方式"])):
            problems.append(f"{r['指标编号']} 标为原子指标却引用了其他指标")

    return pd.DataFrame({"校验项": ["全部通过"] if not problems else problems})


def main() -> None:
    title("A12 指标体系构建与管理（结构化建模）")

    ind = pd.DataFrame(INDICATORS)
    print("\n【指标字典】")
    print(ind[["指标编号", "指标名称", "指标类型", "计算方式", "责任人"]].to_string(index=False))

    print("\n【指标分层统计】")
    print(ind["指标类型"].value_counts().to_string())

    report = validate(ind)
    print("\n【口径校验】")
    print(report.to_string(index=False))

    save_table(ind, "A12_indicator_dictionary.csv")
    save_table(report, "A12_indicator_validation.csv")

    print("\n结论：指标体系落地为代码后，可随数据版本一起纳管，")
    print("      任何口径变更都能在提交记录里追溯，这是数据治理的关键一步。")


if __name__ == "__main__":
    main()
