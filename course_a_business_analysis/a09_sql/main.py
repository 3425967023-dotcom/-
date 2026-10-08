"""
A09 SQL 语言基础（用 sqlite3 迁移）
教材定位：《商业数据分析》第 8 章 SQL语言基础与Mysql入门
         （含 MySQL常用函数.pdf、MySQL8.0开窗函数.pdf）

【内涵解读】
教材要求装 MySQL 并导入 csv。实验环境里更轻量的做法：
用 Python 内置的 sqlite3（零安装、可随仓库上传），把同一批数据建成表，
SQL 语法结构与 MySQL 几乎一致，只是函数名略有差异：

  MySQL              SQLite
  -----------------  ---------------------------
  YEAR(d)            strftime('%Y', d)
  LEFT(s, n)         substr(s, 1, n)
  DATEDIFF           julianday(a) - julianday(b)
  IFNULL             COALESCE / IFNULL（同名可用）
  窗口函数 OVER(...)  窗口函数 OVER(...)  —— 语法完全一致

数据：教材第 9 章 KDD 银行行为数据（clients / trans / loans / card）

【实验覆盖的知识点】
  建表与导入 → SELECT/WHERE → GROUP BY/HAVING → 多表 JOIN
  → 子查询 → 窗口函数（ROW_NUMBER / RANK / 累计 SUM OVER）

运行：python course_a_business_analysis/a09_sql/main.py
"""

from __future__ import annotations

import os
import re
import sqlite3
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

import pandas as pd  # noqa: E402

from common.utils import load, save_table, title  # noqa: E402

# 用于把中文标签转成安全的文件名片段
_SLUG = re.compile(r"[^0-9A-Za-z\u4e00-\u9fff]+")
_QUERY_NO = 0

# 表名 → csv 路径
CSV_MAP = {
    "clients": "kdd/clients.csv",
    "trans": "kdd/trans.csv",
    "loans": "kdd/loans.csv",
    "card": "kdd/card.csv",
    "disp": "kdd/disp.csv",
    "district": "kdd/district.csv",
    "accounts": "kdd/accounts.csv",
}


def init_db(conn: sqlite3.Connection) -> None:
    """把 csv 装入数据库。
    等价教材「把 csv 导入 MySQL 的三种方法」（此处是最省事的一种）。"""
    for table, path in CSV_MAP.items():
        df = load(path)
        # 列名统一小写，避免 SQL 里大小写踩坑
        df.columns = [str(c).strip().lower() for c in df.columns]
        # 金额列形如 "$700"，必须先清洗成数值，
        # 否则 SQLite 对它做 SUM/AVG 会静默返回 0（数据类型是文本）
        for col in ("amount", "balance", "payments", "duration"):
            if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
                s = df[col].astype(str)
                for ch in ("$", ","):
                    s = s.str.replace(ch, "", regex=False)   # 用字面量替换，避免正则兼容问题
                df[col] = pd.to_numeric(s, errors="coerce")
        df.to_sql(table, conn, if_exists="replace", index=False)
        print(f"  已建表 {table:10s} {df.shape[0]:>6d} 行 × {df.shape[1]} 列")


def show(conn: sqlite3.Connection, label: str, sql: str) -> pd.DataFrame:
    """执行 SQL、打印结果，并把结果表导出到本实验 output/ 作为实验成果。"""
    global _QUERY_NO
    _QUERY_NO += 1
    out = pd.read_sql(sql, conn)
    print(f"\n【{label}】")
    print(out.to_string(index=False))
    slug = _SLUG.sub("_", label)[:24].strip("_")
    save_table(out, f"A09_q{_QUERY_NO}_{slug}.csv")
    return out


def run_queries(conn: sqlite3.Connection) -> None:
    print("\n--- 1. SELECT / WHERE / ORDER BY 基础查询 ---")
    show(conn, "透支账户（balance < 0）Top 5", """
        SELECT account_id, date, amount, balance
        FROM trans
        WHERE balance < 0
        ORDER BY balance ASC
        LIMIT 5;
    """)

    print("\n--- 2. GROUP BY + HAVING 分组聚合 ---")
    show(conn, "各交易类型统计", """
        SELECT type                       AS 交易类型,
               COUNT(*)                   AS 笔数,
               ROUND(SUM(amount), 0)      AS 总金额,
               ROUND(AVG(amount), 1)      AS 笔均金额,
               ROUND(MAX(amount), 0)      AS 最大单笔
        FROM trans
        GROUP BY type
        HAVING COUNT(*) > 50
        ORDER BY 总金额 DESC;
    """)

    print("\n--- 3. 多表 JOIN ---")
    show(conn, "客户性别 × 持卡类型 交叉统计", """
        SELECT c.sex             AS 性别,
               cd.type           AS 卡类型,
               COUNT(DISTINCT c.client_id) AS 客户数,
               COUNT(cd.card_id) AS 卡片数
        FROM clients c
        JOIN disp d        ON d.client_id = c.client_id
        JOIN card cd       ON cd.disp_id  = d.disp_id
        GROUP BY c.sex, cd.type
        ORDER BY 客户数 DESC;
    """)

    print("\n--- 4. 子查询：找出高于平均金额的贷款 ---")
    show(conn, "大额贷款（amount > 平均）按状态汇总", """
        SELECT status                AS 贷款状态,
               COUNT(*)              AS 笔数,
               ROUND(SUM(amount), 0) AS 总金额
        FROM loans
        WHERE amount > (SELECT AVG(amount) FROM loans)
        GROUP BY status
        ORDER BY 总金额 DESC;
    """)

    print("\n--- 5. 窗口函数：排名 / 累计 / 组内编号 ---")
    show(conn, "各账户交易明细（含组内编号、累计额、金额排名）", """
        SELECT account_id,
               date,
               amount,
               ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY date)  AS 组内序次,
               SUM(amount)  OVER (PARTITION BY account_id ORDER BY date
                                  ROWS BETWEEN UNBOUNDED PRECEDING
                                  AND CURRENT ROW)                     AS 累计金额,
               RANK()       OVER (ORDER BY amount DESC)                   AS 金额排名
        FROM trans
        ORDER BY 金额排名
        LIMIT 15;
    """)

    print("\n--- 6. 用窗口函数做「每账户最大一笔交易」 ---")
    show(conn, "每账户最大单笔交易", """
        SELECT * FROM (
            SELECT account_id, date, amount,
                   ROW_NUMBER() OVER (PARTITION BY account_id
                                      ORDER BY amount DESC) AS rn
            FROM trans
        ) t
        WHERE t.rn = 1
        ORDER BY t.amount DESC
        LIMIT 10;
    """)

    print("\n--- 7. CASE WHEN 分箱统计 ---")
    show(conn, "交易金额分箱", """
        SELECT CASE
                 WHEN amount <  1000 THEN '1. 小额(<1千)'
                 WHEN amount <  5000 THEN '2. 中额(1千~5千)'
                 WHEN amount < 20000 THEN '3. 大额(5千~2万)'
                 ELSE '4. 巨额(>2万)'
               END                  AS 金额分箱,
               COUNT(*)             AS 笔数,
               ROUND(SUM(amount), 0) AS 总金额
        FROM trans
        GROUP BY 金额分箱
        ORDER BY 金额分箱;
    """)


def main() -> None:
    title("A09 SQL 语言基础（sqlite3 迁移）")
    conn = sqlite3.connect(":memory:")      # 内存库；换成 .db 文件即可持久化
    try:
        print("\n--- 0. 建表导入 ---")
        init_db(conn)
        run_queries(conn)
    finally:
        conn.close()
    print("\nSQL 实验完成（7 类查询）。")


if __name__ == "__main__":
    main()
