"""
A04 Power Query ETL 迁移为 pandas
教材定位：《商业数据分析》第 2 章-5 PowerBI 基本操作 / ETL练习文件

【内涵解读】
Power Query 的五类高频操作，逐一映射到 pandas：

  Power Query 操作              pandas 等价写法
  -------------------------    ------------------------------------
  拆分列（按分隔符）            Series.str.split(",", expand=True)
  数据清洗（去空/去重/修整）     dropna / drop_duplicates / str.strip
  横向合并（合并查询 = JOIN）    DataFrame.merge(how="inner/left/outer")
  纵向合并（追加查询）           pd.concat(ignore_index=True)
  类型转换                      pd.to_datetime / astype

【教材实测数据情况】
  拆分列示例数据.xlsx      Sheet2：订单号列是「逗号分隔的多个订单号」，数量列写作「8件」
  数据清洗示例数据.xlsx    sheet1：第 1 行是标题「电商订单明细表」，表头在第 2 行；
                                   存在实付金额=0 且商品id为空 的无效订单
  BI横向合并练习文件.xlsx  课程表 / 学生表 / 选课表 三张表，正好做 JOIN
  纵向合并演示-*.xlsx      字段名一致 / 不一致 两种情形的追加

运行：python course_a_business_analysis/etl.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from common.utils import load, load_sheets, report_head, save_table, title  # noqa: E402

D = ""


# ---------------- 1. 拆分列 ----------------
def split_column() -> pd.DataFrame:
    """等价 Power Query「拆分列 → 按分隔符 → 每次出现」。"""
    df = load(D + "拆分列示例数据.xlsx", sheet="Sheet2")
    report_head(df, 3, "拆分前")

    # 订单号：「M06...,M06...,M06...」→ 拆成多列
    id_cols = df["订单号"].astype(str).str.split(",", expand=True)
    id_cols.columns = [f"订单号{i + 1}" for i in range(id_cols.shape[1])]

    # 数量：「8件」「10本」→ 拆出数字与单位
    qty = df["数量"].astype(str).str.extract(r"(?P<数量>\d+)(?P<单位>.*)")

    out = pd.concat([df, id_cols, qty], axis=1)
    print(f"\n拆分结果：订单号拆成 {id_cols.shape[1]} 列，数量拆成 数量 + 单位")
    report_head(out, 3, "拆分后")
    return out


# ---------------- 2. 数据清洗 ----------------
def clean() -> pd.DataFrame:
    """等价 Power Query 的「删除重复项 / 删除空行 / 修整(Trim) / 清除」等一组清洗动作。"""
    # 注意：该表第 1 行是标题「电商订单明细表」，真正的表头在第 2 行
    raw = load(D + "数据清洗示例数据.xlsx", sheet="sheet1", header=None)
    raw = raw.iloc[1:].reset_index(drop=True)          # 丢掉标题行
    raw.columns = [str(c).strip() for c in raw.iloc[0]]  # 用第 2 行做表头
    df = raw.iloc[1:].reset_index(drop=True)
    report_head(df, 3, "清洗前")

    before = len(df)
    df = df.drop_duplicates()                            # 删除重复行
    df = df.dropna(how="all")                            # 删除全空行

    # 无效订单：实付金额为 0 且 商品id 为空（教材演示数据里的脏数据）
    for c in ["实付金额", "下单数量"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    invalid = df["商品id"].isna() | (df["实付金额"].fillna(0) <= 0)
    df = df.loc[~invalid].copy()

    # 文本规范：去首尾空格，清除零宽空格与不换行空格
    # 这两类字符是 Excel → Power BI 导入后「看起来一样却匹配不上」的头号元凶。
    # 注意：pandas 3.0 的字符串列默认为新的 str 扩展类型（底层 pyarrow），
    # 直接传正则 r"[\u200b\xa0]" 会被 RE2 拒绝（Invalid escape sequence: \u），
    # 所以这里用字面量字符 + regex=False，跨版本都安全。
    for c in df.columns:
        if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object:
            s = df[c].astype(str).str.strip()
            s = s.str.replace("\u200b", "", regex=False)      # 零宽空格
            s = s.str.replace("\xa0", " ", regex=False)       # 不换行空格
            s = s.mask(s.isin(["nan", "None", "NaT", ""]), np.nan)
            df[c] = s.astype(object)

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    print(f"\n清洗完成：{before} 行 → {len(df)} 行（删除 {before - len(df)} 行无效/重复数据）")
    report_head(df[["订单号", "order_date", "实付金额", "下单城市", "下单数量", "商品名称"]],
                3, "清洗后关键列")
    return df


# ---------------- 3. 横向合并（JOIN） ----------------
def merge_tables() -> pd.DataFrame:
    """等价 Power Query「合并查询」，四种联接方式与 how 参数一一对应。"""
    sheets = load_sheets(D + "BI横向合并练习文件.xlsx")
    course = sheets["课程表"]     # 课程号, 课程名, 学分
    student = sheets["学生表"]    # 学号, 姓名, 性别, 出生日期, 系别, 手机号
    choice = sheets["选课表"]     # 学号, 课程号, 成绩
    print("\n三张表：", {k: v.shape for k, v in sheets.items()})

    # 出生日期在源表里是 Excel 序列号（如 33270），需按 1900 日期系统转换
    student["出生日期"] = pd.to_datetime(student["出生日期"], unit="D",
                                         origin="1899-12-30", errors="coerce")

    inner = choice.merge(student, on="学号", how="inner").merge(course, on="课程号", how="inner")
    left_join = choice.merge(course, on="课程号", how="left")
    full = choice.merge(student, on="学号", how="outer")
    print(f"内连接（只保留能匹配上的）{inner.shape}")
    print(f"左连接（保留左表全部）    {left_join.shape}")
    print(f"完全外部连接              {full.shape}")

    report_head(inner[["学号", "姓名", "系别", "课程名", "学分", "成绩"]], 5, "内连接结果")
    return inner


# ---------------- 4. 纵向合并（APPEND） ----------------
def append_tables() -> None:
    """等价 Power Query「追加查询」。"""
    # 情形 A：字段名完全一致 → 直接堆叠
    s = load_sheets(D + "纵向合并演示-各字段名称一致.xlsx")
    same = pd.concat([s["第一季度"], s["第二季度"]], ignore_index=True)
    same["季度"] = ["Q1"] * len(s["第一季度"]) + ["Q2"] * len(s["第二季度"])
    report_head(same, 3, "情形A-字段一致，直接 concat")

    # 情形 B：字段名不一致（第二季度把「销售额」写成「金额」）
    s2 = load_sheets(D + "纵向合并演示-字段名称不一致.xlsx")
    a, b = s2["第一季度"], s2["第二季度"]
    print("\n情形B 列名对照：")
    print("  第一季度：", list(a.columns))
    print("  第二季度：", list(b.columns))

    # Power Query 靠手工对齐列；pandas 靠 rename 按位置对齐
    mapping = dict(zip(b.columns, a.columns))
    b_aligned = b.rename(columns=mapping)
    both = pd.concat([a, b_aligned], ignore_index=True)
    both["季度"] = ["Q1"] * len(a) + ["Q2"] * len(b)
    report_head(both, 5, "情形B-对齐列名后 concat")

    # 门店名不一致（A1 vs A）也顺手规范掉，这是追加查询的常见后续动作
    both["门店"] = both["门店"].str.replace(r"\d+$", "", regex=True).str.strip()
    save_table(both, "A04_append_result.csv")


def main() -> None:
    title("A04 Power Query ETL 迁移")
    split_column()
    clean()
    merge_tables()
    append_tables()
    print("\nETL 四类操作全部完成。")


if __name__ == "__main__":
    main()
