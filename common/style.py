"""
common/style.py —— 图表修饰规范

对应《Excel数据可视化——从图表到数据大屏》课件第 11~13 页的修饰三要素：
  1) 合理配色（颜色不超过 3 个）
  2) 正确字体（无衬线、全图统一）
  3) 图表元素修饰（删默认标题、加三级文本、去多余边框）

deco() 把教材强调的「一级标题 = 主题 / 二级标题 = 结论 / 备注 = 数据来源」
三级文本体系固化成代码。
"""

from __future__ import annotations

import matplotlib.pyplot as plt

# 课件规定的主题色（3 色以内）+ 中性灰
THEME = ["#185FA5", "#EF9F27", "#0F6E56"]
ENTHESIS = ["#378ADD", "#EF9F27", "#1D9E75"]
POSITIVE = "#E24B4A"   # 中式报表惯例：正向/增长用红
NEGATIVE = "#1D9E75"   # 负向/下降用绿
NEUTRAL = "#B4B2A9"
BG = "#FFFFFF"


def apply_theme() -> None:
    """全局主题：字体、背景、网格、边框。
    等价 Excel 的「图表样式 / 页面主题」。"""
    plt.rcParams.update({
        "font.sans-serif": ["Microsoft YaHei", "SimHei", "DejaVu Sans"],
        "axes.unicode_minus": False,
        "figure.facecolor": BG,
        "savefig.facecolor": BG,
        "axes.facecolor": "none",      # 绘图区无填充，靠边框区分（课件第 12 页）
        "axes.edgecolor": "#B4B2A9",
        "axes.linewidth": 0.8,
        "axes.grid": True,
        "grid.color": "#B4B2A9",
        "grid.alpha": 0.2,
        "grid.linestyle": "--",
        "xtick.color": "#5F5E5A",
        "ytick.color": "#5F5E5A",
        "axes.labelcolor": "#444441",
        "axes.titlesize": 12,
    })


def clean_axes(ax, keep=("left", "bottom")) -> None:
    """删除非必要边框（课件第 19 页「删除非必要元素」）。"""
    for side in ("top", "right", "bottom", "left"):
        ax.spines[side].set_visible(side in keep)


def deco(ax, title=None, subtitle=None, note=None) -> None:
    """三级文本体系（课件「添加必要元素」一节）。

    title    一级标题：图表主题，一句话说清「这张图在讲什么」
    subtitle 二级标题：对数据的分析结论
    note     备注：时间范围 / 数据来源
    """
    ax.set_title("")
    if title:
        ax.text(0, 1.18, title, transform=ax.transAxes,
                fontsize=13, fontweight="bold", color="#2C2C2A", va="bottom")
    if subtitle:
        ax.text(0, 1.06, subtitle, transform=ax.transAxes,
                fontsize=10, color="#5F5E5A", va="bottom")
    if note:
        ax.text(0, -0.22, note, transform=ax.transAxes,
                fontsize=8, color="#888780", va="top")
