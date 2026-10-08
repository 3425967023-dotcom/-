"""
A11 效应分解方法做预报（时间序列分解）
教材定位：《商业数据分析》第 10 章 使用效应分解方法做预报
         （效应分解法.pbix、AirPassengers.csv、信用卡消费额_含节日/去除节日.xlsx）

【内涵解读】
教材所谓「效应分解」，就是经典的时间序列分解思想：
把一条序列拆成三个效应相乘（或相加），分别预测再合成。

    Y = 趋势 T  ×  季节 S  ×  随机 R        （乘法模型，本教材采用）
    Y = 趋势 T  +  季节 S  +  随机 R        （加法模型）

  趋势 T：用移动平均去掉季节性后剩下的长期方向
  季节 S：各月相对趋势的平均偏离程度（季节因子）
  随机 R：剥离 T 和 S 后剩下的不规则波动

【为什么教材会先取对数】
乘客量这类数据的季节波动幅度随水平一起放大（乘法），
取对数后 log(Y) = logT + logS + logR 变成加法，
这正是 AirPassengers.csv 里为什么有一列 ln_AIR。

【预报方法】
用线性回归外推趋势项，再乘以对应月份的季节因子，
即得到未来 12 期的预测值。

运行：python course_a_business_analysis/a11_time_series/main.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from common.utils import load, report_head, save_fig, save_table, title  # noqa: E402

FE = "AirPassengers.csv"


def decompose(series: pd.Series, period: int = 12):
    """加法/乘法两种分解，返回中间结果。"""
    # 趋势项：居中移动平均（窗口 = 一个完整季节周期）
    trend = series.rolling(period, center=True).mean()

    # ---- 加法模型的季节项：去趋势后的月均偏差，归一化到均值为 0 ----
    detr = series - trend
    s_add = detr.groupby(detr.index.month).mean()
    s_add = s_add - s_add.mean()

    # ---- 乘法模型的季节因子：比值月均，归一化到均值为 1 ----
    ratio = series / trend
    s_mul = ratio.groupby(ratio.index.month).mean()
    s_mul = s_mul / s_mul.mean()

    resid = series - trend - detr.index.month.map(s_add)
    return trend, s_add, s_mul, resid


def main() -> None:
    title("A11 效应分解方法做预报")

    df = load(FE)
    report_head(df, 5, "AirPassengers 原始数据")
    df["DATE"] = pd.to_datetime(df["DATE"])
    df = df.set_index("DATE").sort_index()
    df["AIR"] = pd.to_numeric(df["AIR"], errors="coerce")
    s = df["AIR"].dropna()
    print(f"\n序列长度：{len(s)} 期（{s.index[0]:%Y-%m} ~ {s.index[-1]:%Y-%m}）")

    trend, s_add, s_mul, resid = decompose(s)

    print("\n【乘法季节因子】(>1 表示该月高于趋势)")
    print(s_mul.round(3).to_string())
    peak = s_mul.idxmax()
    trough = s_mul.idxmin()
    print(f"  → 旺季：{peak} 月（因子 {s_mul[peak]:.2f}）；淡季：{trough} 月（因子 {s_mul[trough]:.2f}）")

    # ---------- 趋势项线性拟合 + 外推 ----------
    t = np.arange(len(s))
    mask = trend.notna()
    k, b = np.polyfit(t[mask], trend[mask], 1)      # trend = k*t + b
    print(f"\n【趋势项拟合】趋势 ≈ {k:.3f} × 期数 + {b:.1f}（每期平均增加 {k:.1f} 人）")

    # ---------- 未来 12 期预测 ----------
    horizon = 12
    t_future = np.arange(len(s), len(s) + horizon)
    trend_future = k * t_future + b
    future_index = pd.date_range(s.index[-1] + pd.offsets.MonthBegin(1),
                                 periods=horizon, freq="MS")
    future_season = pd.Series(future_index.month).map(s_mul).values
    forecast = pd.Series(trend_future * future_season, index=future_index, name="预测AIR")

    print("\n【未来 12 期预测】")
    print(forecast.round(1).to_string())

    # 拟合值（历史回看，用于判断模型是否合理）
    fitted = trend * s.index.month.map(s_mul)

    # ---------- 绘图 ----------
    fig = plt.figure(figsize=(12, 9))

    ax1 = fig.add_subplot(3, 1, 1)
    ax1.plot(s.index, s.values, color="#378ADD", label="原始序列")
    ax1.plot(s.index, trend, color="#EF9F27", ls="--", label="趋势项 T（12 期移动平均）")
    ax1.set_title("① 原始序列与趋势项", fontsize=12)
    ax1.legend(frameon=False, fontsize=9)
    ax1.set_ylabel("乘客数")

    ax2 = fig.add_subplot(3, 3, 4)
    ax2.bar(s_mul.index - 1 + 1, s_mul.values - 1,
            color=np.where(s_mul.values >= 1, "#F0997B", "#9FE1CB"),
            edgecolor="white")
    ax2.axhline(0, color="#444441", lw=0.8)
    ax2.set_xticks(range(1, 13))
    ax2.set_title("② 乘法季节因子（减 1 后）", fontsize=11)
    ax2.tick_params(labelsize=8)

    ax3 = fig.add_subplot(3, 3, 5)
    r = resid.dropna()
    ax3.hist(r, bins=18, color="#B5D4F4", edgecolor="white")
    ax3.set_title("③ 残差 R 分布（越接近正态越好）", fontsize=11)
    ax3.tick_params(labelsize=8)

    ax4 = fig.add_subplot(3, 3, 6)
    ax4.plot(s.index, s.values, color="#378ADD", lw=1, label="实际")
    ax4.plot(s.index, fitted, color="#7F77DD", ls=":", lw=1.4, label="拟合")
    ax4.set_title("④ 拟合效果", fontsize=11)
    ax4.legend(frameon=False, fontsize=8)
    ax4.tick_params(labelsize=8)

    ax5 = fig.add_subplot(3, 1, 3)
    ax5.plot(s.index, s.values, color="#378ADD", label="历史实际")
    ax5.plot(s.index, fitted, color="#7F77DD", ls=":", label="历史拟合")
    ax5.plot(forecast.index, forecast.values, marker="o", ms=4, color="#E24B4A",
             label="未来 12 期预测（趋势 × 季节）")
    ax5.axvline(s.index[-1], color="#888780", ls="--", lw=0.8)
    ax5.set_title("⑤ 效应分解法预报结果", fontsize=12)
    ax5.legend(frameon=False, fontsize=9)
    ax5.set_ylabel("乘客数")

    fig.tight_layout()
    save_fig(fig, "A11_decompose_forecast.png")

    # 校验：拟合优度（用实际 vs 拟合，忽略首尾缺失段）
    pair = pd.concat([s.rename("实际"), fitted.rename("拟合")], axis=1).dropna()
    ss_res = ((pair["实际"] - pair["拟合"]) ** 2).sum()
    ss_tot = ((pair["实际"] - pair["实际"].mean()) ** 2).sum()
    print(f"\n【模型校验】R² = {1 - ss_res / ss_tot:.4f}，"
          f"平均绝对百分比误差 MAPE = "
          f"{(abs(pair['实际'] - pair['拟合']) / pair['实际']).mean():.2%}")

    # Series.reset_index 的参数是 name（不是 names），这里显式命名导出列
    fc = forecast.round(1).rename_axis("月份").reset_index(name="预测AIR")
    save_table(fc, "A11_forecast.csv")
    print("\n说明：若允许使用第三方库，statsmodels 一行即可得到同样的分解——")
    print("  from statsmodels.tsa.seasonal import seasonal_decompose")
    print("  seasonal_decompose(s, model='multiplicative', period=12)")


if __name__ == "__main__":
    main()
