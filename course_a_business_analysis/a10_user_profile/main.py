"""
A10 用户标签体系与用户画像
教材定位：《商业数据分析》第 9 章 用户标签体系与用户画像专题

【内涵解读】
用户画像 = 「标签体系」+「画像输出」：
  标签体系：把原始行为沉淀成可枚举、可复用的标签
            （人口属性标签 / 交易活跃度标签 / 资产与负债标签 / 持卡标签）
  画像输出：用一组标签去描述一个客群，支撑运营决策

教材给的 KDD 银行行为数据是八表结构：
  clients(客户) → disp(账户归属) → accounts / card / loans / order / trans
  district(地区) 提供地理维度

【本实验的标签设计】（对应教材「标签体系参考」文件夹的分类思路）
  人口属性：性别、年龄段
  活跃度  ：按交易笔数分 低频/中频/高频/超高频
  价值    ：按交易总额分位分 普通/优质/高价值
  负债    ：按是否有未结清贷款分 有负债/无负债
  持卡    ：持卡数量

【数据说明】
第 9 章 data 目录下的 csv 已是清洗后的版本：日期为 ISO 格式、
性别为「男/女」、金额形如 "$700"（需去符号转数值）。

运行：python course_a_business_analysis/a10_user_profile/main.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from common.utils import load, report_head, save_fig, save_table, title  # noqa: E402

D = "kdd/"


def _to_money(s: pd.Series) -> pd.Series:
    """把 '$700' 这类带符号金额转成数值。用字面量替换避免正则兼容问题。"""
    out = s.astype(str)
    for ch in ("$", ","):
        out = out.str.replace(ch, "", regex=False)
    return pd.to_numeric(out, errors="coerce")


def build_tags() -> pd.DataFrame:
    clients = load(D + "clients.csv")
    trans = load(D + "trans.csv")
    loans = load(D + "loans.csv")
    card = load(D + "card.csv")
    disp = load(D + "disp.csv")          # client_id ↔ account_id 的桥梁
    accounts = load(D + "accounts.csv")

    # ---- 基础清洗 ----
    trans["date"] = pd.to_datetime(trans["date"], errors="coerce")
    trans["amount"] = _to_money(trans["amount"])
    trans["balance"] = _to_money(trans["balance"])
    loans["date"] = pd.to_datetime(loans["date"], errors="coerce")
    loans["amount"] = _to_money(loans["amount"])
    accounts["date"] = pd.to_datetime(accounts["date"], errors="coerce")
    # 开户日期用于计算账龄，可反映客户忠诚度
    accounts["开户日期"] = accounts["date"]
    accounts["账龄月"] = ((pd.Timestamp("1999-01-01") - accounts["开户日期"]).dt.days / 30).round(1)

    # ---- 标签 1：人口属性标签 ----
    clients["birth_date"] = pd.to_datetime(clients["birth_date"], errors="coerce")
    clients["年龄"] = (pd.Timestamp("1999-01-01") - clients["birth_date"]).dt.days // 365
    clients["年龄段"] = pd.cut(clients["年龄"], [0, 25, 35, 45, 55, 200],
                              labels=["≤25", "26-35", "36-45", "46-55", ">55"])
    clients = clients.rename(columns={"sex": "性别"})

    # ---- 标签 2：交易活跃度 / 价值标签 ----
    # 先把交易按账户汇总，再通过 disp 归到客户（一个客户可能有多个账户）
    acct = trans.groupby("account_id").agg(
        交易笔数=("trans_id", "count"),
        交易总额=("amount", "sum"),
        交易均值=("amount", "mean"),
        首次交易=("date", "min"),
        最近交易=("date", "max"),
    ).reset_index()

    acct["活跃度标签"] = pd.cut(acct["交易笔数"], [0, 5, 20, 60, np.inf],
                              labels=["低频", "中频", "高频", "超高频"])
    # 用分位切分价值标签（比绝对值更稳健，不受量纲影响）
    acct["价值标签"] = pd.cut(acct["交易总额"].rank(pct=True), [0, 0.5, 0.8, 1.0],
                             labels=["普通", "优质", "高价值"])

    # 账户 → 客户
    acct_c = acct.merge(disp[["client_id", "account_id"]], on="account_id", how="left")
    cus_acct = acct_c.groupby("client_id").agg(
        交易笔数=("交易笔数", "sum"),
        交易总额=("交易总额", "sum"),
        账户数=("account_id", "nunique"),
        活跃度标签=("活跃度标签", lambda s: s.mode().iat[0] if not s.mode().empty else None),
        价值标签=("价值标签", lambda s: s.mode().iat[0] if not s.mode().empty else None),
    ).reset_index()

    # ---- 标签 3：负债标签 ----
    # KDD 里 status：A/C = 合同未结束（视为有负债），B/D = 已结清
    loans["未结清"] = loans["status"].isin(["A", "C"]).astype(int)
    loan_by_acct = loans.groupby("account_id").agg(
        贷款笔数=("loan_id", "count"),
        未结清笔数=("未结清", "sum"),
    ).reset_index()
    loan_by_acct["负债标签"] = np.where(loan_by_acct["未结清笔数"] > 0, "有负债", "无负债")
    loan_c = (loan_by_acct.merge(disp[["client_id", "account_id"]], on="account_id",
                                 how="left")
                          .groupby("client_id")
                          .agg(贷款笔数=("贷款笔数", "sum"),
                               未结清笔数=("未结清笔数", "sum"))
                          .reset_index())

    # ---- 标签 4：持卡标签 ----
    card_tag = (card.merge(disp[["disp_id", "client_id"]], on="disp_id", how="left")
                    .groupby("client_id").size().rename("持卡数").reset_index())

    # ---- 标签 5：账龄标签（账户维度 → 客户维度）----
    age_tag = (accounts[["account_id", "账龄月"]]
               .merge(disp[["client_id", "account_id"]], on="account_id", how="left")
               .groupby("client_id")["账龄月"].max().rename("最长账龄月").reset_index())

    # ==================== 标签宽表（画像底表） ====================
    profile = (clients.rename(columns={"client_id": "client_id"})
                      .merge(cus_acct, on="client_id", how="left")
                      .merge(loan_c, on="client_id", how="left")
                      .merge(card_tag, on="client_id", how="left")
                      .merge(age_tag, on="client_id", how="left"))
    # 缺失值填充：没有交易/贷款/持卡记录的客户会被 merge 成 NaN
    profile["贷款笔数"] = profile["贷款笔数"].fillna(0)
    profile["未结清笔数"] = profile["未结清笔数"].fillna(0)
    profile["持卡数"] = profile["持卡数"].fillna(0)
    profile["负债标签"] = np.where(profile["未结清笔数"] > 0, "有负债", "无负债")
    profile["活跃度标签"] = profile["活跃度标签"].fillna("无交易")
    profile["价值标签"] = profile["价值标签"].fillna("未消费")

    report_head(profile, 5, "用户画像标签宽表")
    return profile


def main() -> None:
    title("A10 用户标签体系与用户画像")
    profile = build_tags()
    print(f"\n画像底表规模：{profile.shape[0]} 人 × {profile.shape[1]} 个字段")

    # ---------- 画像输出：客群结构 ----------
    print("\n【标签分布】")
    for col in ["年龄段", "活跃度标签", "价值标签", "负债标签"]:
        vc = profile[col].value_counts()
        print(f"  {col}：{dict(vc)}")

    fig = plt.figure(figsize=(13, 8))

    ax1 = fig.add_subplot(2, 3, 1)
    pd.crosstab(profile["年龄段"], profile["性别"]).plot(
        kind="bar", ax=ax1, color=["#D4537E", "#378ADD"], width=0.75, edgecolor="white")
    ax1.set_title("① 年龄 × 性别 客群结构", fontsize=11)
    ax1.legend(frameon=False, fontsize=8)
    ax1.tick_params(axis="x", rotation=0, labelsize=8)
    ax1.set_xlabel("")

    ax2 = fig.add_subplot(2, 3, 2)
    ax2.bar(profile["活跃度标签"].value_counts().index,
            profile["活跃度标签"].value_counts().values,
            color="#9FE1CB", edgecolor="#0F6E56")
    ax2.set_title("② 活跃度标签分布", fontsize=11)
    ax2.tick_params(axis="x", rotation=20, labelsize=8)

    ax3 = fig.add_subplot(2, 3, 3)
    ax3.bar(profile["价值标签"].value_counts().index,
            profile["价值标签"].value_counts().values,
            color="#EF9F27", edgecolor="#854F0B")
    ax3.set_title("③ 价值标签分布", fontsize=11)
    ax3.tick_params(axis="x", rotation=20, labelsize=8)

    ax4 = fig.add_subplot(2, 3, 4)
    ct = pd.crosstab(profile["年龄段"], profile["价值标签"], normalize="index") * 100
    ct.plot(kind="bar", stacked=True, ax=ax4, colormap="Blues", width=0.75,
            edgecolor="white")
    ax4.set_title("④ 各年龄段价值标签构成（%）", fontsize=11)
    ax4.legend(frameon=False, fontsize=7)
    ax4.tick_params(axis="x", rotation=0, labelsize=8)
    ax4.set_xlabel("")

    ax5 = fig.add_subplot(2, 3, 5)
    pd.crosstab(profile["活跃度标签"], profile["负债标签"]).plot(
        kind="bar", ax=ax5, color=["#F0997B", "#B4B2A9"], width=0.75, edgecolor="white")
    ax5.set_title("⑤ 活跃度 × 负债标签", fontsize=11)
    ax5.legend(frameon=False, fontsize=8)
    ax5.tick_params(axis="x", rotation=20, labelsize=8)
    ax5.set_xlabel("")

    ax6 = fig.add_subplot(2, 3, 6)
    ax6.hist(profile["交易总额"].dropna(), bins=40, color="#B5D4F4", edgecolor="white")
    ax6.axvline(profile["交易总额"].median(), color="#A32D2D", ls="--",
                label=f"中位数 {profile['交易总额'].median():,.0f}")
    ax6.set_title("⑥ 客户交易总额分布", fontsize=11)
    ax6.legend(frameon=False, fontsize=8)

    fig.tight_layout()
    save_fig(fig, "A10_user_profile.png")

    save_table(profile, "A10_user_profile_tags.csv")

    # ---------- 画像应用：挑出高价值运营名单 ----------
    target = profile[(profile["价值标签"] == "高价值")
                     & (profile["活跃度标签"].isin(["高频", "超高频"]))]
    print(f"\n【画像应用】高价值 + 高频客户共 {len(target)} 人，"
          f"平均交易总额 {target['交易总额'].mean():,.0f} 元")
    print("  这部分客群是「重要价值客户」，应优先做交叉销售与专属权益。")
    save_table(target, "A10_high_value_customers.csv")
    print("\n完成。")


if __name__ == "__main__":
    main()
