"""
B04 动态图表
教材定位：《Excel数据可视化——从图表到数据大屏》第三章 动态图表.xlsm

【内涵解读】
Excel 做动态图表靠「控件（滑块/下拉）+ 定义名称 + 辅助列」，复杂案例还要写 VBA。
Python 有两条更直接的路径：

  路径 A：matplotlib 动画（FuncAnimation）
          逐帧修改图形对象的数据，导出 gif / mp4。
          等价 Excel 里 VBA 逐帧刷新柱形高度。

  路径 B：plotly 交互图
          一行 animation_frame 就得到带播放按钮的动态图。
          等价 Excel 的「切片器切换」，且能拖动、能缩放、能悬停看数值。

运行：python course_b_excel_visualization/b04_dynamic/main.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.animation import FuncAnimation, PillowWriter  # noqa: E402

from common.style import clean_axes, apply_theme  # noqa: E402
from common.utils import out_dir, save_html, title  # noqa: E402

apply_theme()


def animated_bar() -> None:
    """动态柱形图：数据逐帧增长。"""
    regions = [f"区域{i + 1}" for i in range(8)]
    frames = 40
    rng = np.random.default_rng(1)
    target = rng.integers(120, 480, len(regions))

    fig, ax = plt.subplots(figsize=(8, 4.2))
    bars = ax.bar(regions, [0] * len(regions), color="#85B7EB",
                  edgecolor="#185FA5", width=0.6)
    labels = [ax.text(i, 5, "", ha="center", fontsize=9) for i in range(len(regions))]
    ax.set_ylim(0, 540)
    ax.set_ylabel("销量")
    ax.set_title("动态柱形图：数据逐帧增长", fontsize=12)
    clean_axes(ax)

    def update(f):
        prog = (f + 1) / frames
        for b, t, tx in zip(bars, target, labels):
            v = t * prog
            b.set_height(v)
            tx.set_y(v + 10)
            tx.set_text(f"{v:.0f}")
        return list(bars) + labels

    ani = FuncAnimation(fig, update, frames=frames, interval=60, blit=False)
    out = os.path.join(out_dir(), "B04_animated_bar.gif")
    ani.save(out, writer=PillowWriter(fps=16))
    plt.close(fig)
    print("  [动图] output/B04_animated_bar.gif")


def animated_line() -> None:
    """动态折线图：逐点画出的「描线」效果。"""
    rng = np.random.default_rng(9)
    x = np.arange(60)
    y = 100 + np.cumsum(rng.normal(2, 6, 60))

    fig, ax = plt.subplots(figsize=(8.4, 4))
    ax.set_xlim(0, 60)
    ax.set_ylim(y.min() - 20, y.max() + 20)
    (line,) = ax.plot([], [], color="#378ADD", lw=1.8)
    (dot,) = ax.plot([], [], "o", color="#A32D2D", ms=5)
    label = ax.text(0.02, 0.92, "", transform=ax.transAxes, fontsize=10, color="#0C447C")
    ax.set_title("动态折线图：逐点描线", fontsize=12)
    ax.set_xlabel("时间")
    ax.set_ylabel("指标值")
    clean_axes(ax)

    def update(f):
        line.set_data(x[: f + 1], y[: f + 1])
        dot.set_data([x[f]], [y[f]])
        label.set_text(f"第 {f + 1} 期：{y[f]:.0f}")
        return line, dot, label

    ani = FuncAnimation(fig, update, frames=len(x), interval=60, blit=False)
    out = os.path.join(out_dir(), "B04_animated_line.gif")
    ani.save(out, writer=PillowWriter(fps=18))
    plt.close(fig)
    print("  [动图] output/B04_animated_line.gif")


def plotly_dynamic() -> None:
    """plotly 带播放按钮的动态图（等价 Excel 切片器切换）。"""
    import pandas as pd
    import plotly.express as px

    rng = np.random.default_rng(5)
    rows = []
    for year in range(2018, 2025):
        for region in ["华东", "华北", "华南", "西部"]:
            rows.append(dict(年份=year, 区域=region,
                             销售额=int(rng.integers(200, 900))))
    df = pd.DataFrame(rows)

    fig = px.bar(df, x="区域", y="销售额", color="区域",
                 animation_frame="年份", range_y=[0, 1000],
                 title="动态柱形图：按年份播放（等价 Excel 切片器）")
    fig.update_layout(font_family="Microsoft YaHei")
    save_html(fig, "B04_plotly_dynamic.html")


def main() -> None:
    title("B04 动态图表")
    animated_bar()
    animated_line()
    plotly_dynamic()
    print("\n完成：2 个 gif 动图 + 1 个可交互 html。")


if __name__ == "__main__":
    main()
