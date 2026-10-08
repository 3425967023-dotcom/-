"""
B02 图表修饰三要素：配色 / 字体 / 图表元素
教材定位：《Excel数据可视化——从图表到数据大屏》课件第 11~19 页

【内涵解读】
课件把图表修饰归纳为三个方向，并给出可执行规则：

  ① 合理配色：图形颜色不超过 3 个；字体颜色与图形保持一致；
     背景优先「无填充 + 边框」；对比关系优先用位置体现，其次用对比色。
  ② 正确字体：无衬线优先（黑体/微软雅黑），一个图表只用一个字体。
  ③ 元素修饰：先删默认非必要元素（默认标题、多余图例、网格线），
     再添加三级文本（一级标题=主题 / 二级标题=结论 / 备注=数据来源），
     最后修饰颜色、间隙宽度、数据标记。

本实验把这三点固化成代码：
  common/style.py 里的 apply_theme() 管全局字体与背景（对应 ①②）
  本文件的 deco() 管三级文本体系（对应 ③）

运行：python course_b_excel_visualization/b02_styling/main.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from common.style import NEUTRAL, THEME, apply_theme, clean_axes, deco  # noqa: E402
from common.utils import save_fig, title  # noqa: E402

apply_theme()


def before_after() -> None:
    """对比演示：未修饰 vs 按课件规范修饰。"""
    brands = ["品牌A", "品牌B", "品牌C", "品牌D"]
    values = [46.2, 28.5, 15.8, 9.5]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.6))

    # ---- 左：未修饰（Excel 默认样式） ----
    ax1.bar(brands, values)
    ax1.set_title("未修饰")
    ax1.grid(True)

    # ---- 右：按课件规范修饰 ----
    bars = ax2.bar(brands, values, width=0.55,
                   color=[THEME[0], THEME[0], THEME[0], NEUTRAL],
                   edgecolor="white", linewidth=1)
    ax2.bar_label(bars, fmt="%.1f%%", fontsize=10, padding=2)
    clean_axes(ax2)                                  # 删掉上/右边框
    ax2.grid(False)                                  # 删掉网格线
    ax2.set_yticks([])                               # 删掉纵坐标轴（有数据标签即可）
    deco(ax2,
         title="品牌A 份额领先，前三品牌合计超九成",
         subtitle="单位：%；配色只保留 1 个主题色 + 1 个灰，突出前三项",
         note="数据来源：内部销售系统 ｜ 制图：Python + Matplotlib")

    fig.tight_layout()
    save_fig(fig, "B02_before_after.png")


def color_rules() -> None:
    """配色规则的三种典型应用：突出、对比、序列。"""
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))

    labels = list("ABCDEFGH")
    vals = np.array([32, 45, 21, 39, 28, 52, 33, 41])

    # ① 突出：只给重点项上色，其余留灰
    colors = [THEME[0] if v == vals.max() else NEUTRAL for v in vals]
    axes[0].bar(labels, vals, color=colors, width=0.62)
    axes[0].set_title("① 突出：最大项高亮", fontsize=11)

    # ② 对比：两组用位置（分组柱形）而非颜色堆叠
    x = np.arange(4)
    axes[1].bar(x - 0.19, [320, 460, 210, 390], 0.38, color=THEME[0], label="本期")
    axes[1].bar(x + 0.19, [280, 410, 250, 350], 0.38, color=NEUTRAL, label="上期")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(list("ABCD"))
    axes[1].legend(frameon=False, fontsize=9)
    axes[1].set_title("② 对比：位置优先于颜色", fontsize=11)

    # ③ 序列：同一色系的深浅渐变表达大小
    axes[2].bar(labels, vals,
                color=plt.cm.Blues(np.linspace(0.3, 0.9, len(labels))), width=0.62)
    axes[2].set_title("③ 序列：同色系深浅", fontsize=11)

    for ax in axes:
        clean_axes(ax)
        ax.tick_params(labelsize=8)
    fig.tight_layout()
    save_fig(fig, "B02_color_rules.png")


def font_and_elements() -> None:
    """字体分级 + 元素修饰（间隙宽度、数据标记）。"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.4))

    # 字重分级：标题 14 bold / 副标题 10 / 刻度 9 / 备注 8
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    ax1.plot(quarters, [120, 156, 148, 190], marker="o", color=THEME[1], lw=2)
    ax1.tick_params(labelsize=9)
    deco(ax1, title="季度销售额稳步上行", subtitle="字体全图统一为微软雅黑；标题加粗、正文常规")

    # 间隙宽度：太小显拥挤，太大显松散（课件第 19 页）
    x = np.arange(3)
    base = [40, 60, 50]
    ax2.bar(x - 0.25, base, 0.18, label="间隙 0.18（偏窄）", color="#B5D4F4")
    ax2.bar(x, base, 0.32, label="间隙 0.32（适中）", color=THEME[0])
    ax2.bar(x + 0.25, base, 0.5, label="间隙 0.50（偏宽）", color="#85B7EB")
    ax2.set_xticks(x)
    ax2.set_xticklabels(list("ABC"))
    ax2.legend(frameon=False, fontsize=8)
    ax2.tick_params(labelsize=9)
    deco(ax2, title="柱形间隙宽度的选择", subtitle="类别数越少，间隙应越大；反之越小")

    for ax in (ax1, ax2):
        clean_axes(ax)
    fig.tight_layout()
    save_fig(fig, "B02_font_elements.png")


def main() -> None:
    title("B02 图表修饰三要素")
    before_after()
    color_rules()
    font_and_elements()
    print("\n完成：修饰前后对比 + 配色规则 + 字体元素，共 3 张。")


if __name__ == "__main__":
    main()
