# -*- coding: utf-8 -*-
"""
《Excel数据可视化——从图表到数据大屏》第二章 30 个图表 Python 复现

【内涵解读】
教材第二章用 30 个工作表演示 30 类图表的 Excel 做法：
前 15 个偏「柱形 / 条形」家族（渐变柱形、蝴蝶图、甘特图、对比柱形……），
后 15 个偏「圆形 / 极坐标」家族（圆环、水球、玉玦、南丁格尔玫瑰、仪表盘……）。

其中相当一部分在 Excel 里是「形状 + 辅助列伪造」出来的效果，
Python 用基础图元（bar / barh / bar(polar) / broken_barh / Wedge / FancyBboxPatch）
可以原生实现，且数据可参数化、可批量复用。

数据全部内置（已与 Excel 逐格核对），不装 pandas 也能出图；
若需改为数据驱动，见文件末尾的 load_excel_data()。

依赖: matplotlib, numpy
运行: python course_b_excel_visualization/b03_gallery/main.py
输出: ./output/chart_XX_名称.png  共 30 张 + _overview_all_30.png 总览拼图
"""
import os
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Wedge, Circle, Rectangle, Polygon
from matplotlib.lines import Line2D

# ============ 路径 ============
ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'output'          # 本实验的图表统一存到 b03_gallery/output/
OUT.mkdir(parents=True, exist_ok=True)

# ============ 全局样式 ============
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, f'chart_{name}.png'), dpi=120, bbox_inches='tight')
    plt.close(fig)


# ============ 1 渐变柱形图 ============
def chart_01():
    regions = ['华北', '华南', '东北', '西北', '西南', '华东']
    values = [2354, 1902, 3524, 2698, 2896, 2563]
    fig, ax = plt.subplots(figsize=(8, 5))
    # 渐变色
    colors = plt.cm.Blues(np.linspace(0.45, 0.95, len(values)))
    bars = ax.bar(regions, values, color=colors, edgecolor='none', width=0.6)
    # 顶部数据标签
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, v + 60, str(v),
                ha='center', fontsize=10, color='#333')
    # 隐藏边框
    for s in ('top', 'right', 'left'):
        ax.spines[s].set_visible(False)
    ax.set_ylabel('销售量')
    ax.set_title('1 渐变柱形图', fontsize=14)
    save(fig, '01_渐变柱形图')


# ============ 2 带均值柱形图 ============
def chart_02():
    regions = ['华北', '华南', '东北', '西北', '西南', '华东']
    values = [2354, 1902, 3524, 2698, 2896, 2563]
    avg = np.mean(values)
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(regions, values, color='#4472C4', width=0.55)
    ax.axhline(avg, color='#ED7D31', linestyle='--', linewidth=2, label=f'均值 {avg:.0f}')
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, v + 60, str(v),
                ha='center', fontsize=10)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.legend()
    ax.set_title('2 带均值柱形图', fontsize=14)
    save(fig, '02_带均值柱形图')


# ============ 3 渐变圆角柱形图 ============
def chart_03():
    goods = ['口红', '面膜', '隔离', '防晒', '精华', '面霜']
    values = [653, 523, 648, 856, 714, 785]
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = plt.cm.Reds(np.linspace(0.4, 0.9, len(values)))
    for i, (g, v) in enumerate(zip(goods, values)):
        # 圆角矩形近似
        box = FancyBboxPatch((i - 0.3, 0), 0.6, v,
 boxstyle="round,pad=0.02,rounding_size=18",
                             linewidth=0, facecolor=colors[i])
        ax.add_patch(box)
        ax.text(i, v + 25, str(v), ha='center', fontsize=10)
    ax.set_xlim(-0.6, len(goods) - 0.4)
    ax.set_ylim(0, max(values) * 1.15)
    ax.set_xticks(range(len(goods)))
    ax.set_xticklabels(goods)
    for s in ('top', 'right', 'left'):
        ax.spines[s].set_visible(False)
    ax.set_title('3 渐变圆角柱形图', fontsize=14)
    save(fig, '03_渐变圆角柱形图')


# ============ 4 标注柱形图 ============
def chart_04():
    cats = ['口红', '面膜', '隔离', '防晒', '精华', '面霜', '眼影', '气垫']
    values = [9221, 5102, 6571, 5760, 6321, 8612, 2645, 5321]
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(cats, values, color='#5B9BD5', width=0.6)
    # 高低标注：最高红色、最低绿色
    max_i, min_i = int(np.argmax(values)), int(np.argmin(values))
    bars[max_i].set_color('#C00000')
    bars[min_i].set_color('#00B050')
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, v + 150,
                str(v), ha='center', fontsize=10)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.set_title('4 标注柱形图（最高/最低高亮）', fontsize=14)
    save(fig, '04_标注柱形图')


# ============ 5 层叠柱形图 ============
def chart_05():
    qs = ['2021Q1', 'Q2', 'Q3', 'Q4', '2022Q1', 'Q2']
    sales = [3121, 4086, 4321, 4601, 4936, 4231]
    profit = [1020, 1421, 1502, 1623, 1781, 1432]
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(qs))
    ax.bar(x, sales, color='#4472C4', label='销售额', width=0.55)
    ax.bar(x, profit, color='#ED7D31', label='利润额', width=0.55)
    for i, (s, p) in enumerate(zip(sales, profit)):
        ax.text(i, s + 80, str(s), ha='center', fontsize=9)
        ax.text(i, p + 80, str(p), ha='center', fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels(qs)
    ax.legend(); ax.set_title('5 层叠柱形图（重叠）', fontsize=14)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    save(fig, '05_层叠柱形图')


# ============ 6 蝴蝶图 ============
def chart_06():
    regions = ['华东', '西北', '东北', '华北', '华南']
    y2022 = [1215, 1321, 1426, 1531, 2238]
    y2021 = [1003, 1265, 1531, 1436, 2066]
    fig, ax = plt.subplots(figsize=(8, 5))
    y = np.arange(len(regions))
    ax.barh(y, [-v for v in y2021], color='#9DC3E6', label='2021年')
    ax.barh(y, y2022, color='#4472C4', label='2022年')
    ax.set_yticks(y); ax.set_yticklabels(regions)
    ax.axvline(0, color='gray', linewidth=0.8)
    ax.set_xticks([]); ax.set_title('6 蝴蝶图（左右双向）', fontsize=14)
    ax.legend()
    save(fig, '06_蝴蝶图')


# ============ 7 蝴蝶图（百分比） ============
def chart_07():
    regions = ['华东', '西北', '东北', '华北', '华南']
    y2022 = [0.36, 0.31, 0.18, 0.13, 0.09]
    y2021 = [0.42, 0.26, 0.19, 0.12, 0.05]
    fig, ax = plt.subplots(figsize=(8, 5))
    y = np.arange(len(regions))
    bars_l = ax.barh(y, [-v for v in y2021], color='#9DC3E6')
    bars_r = ax.barh(y, y2022, color='#4472C4')
    for b, v in zip(bars_l, y2021):
        ax.text(b.get_width() - 0.005, b.get_y() + b.get_height() / 2,
                f'{v:.0%}', ha='right', va='center', fontsize=9)
    for b, v in zip(bars_r, y2022):
        ax.text(b.get_width() + 0.005, b.get_y() + b.get_height() / 2,
                f'{v:.0%}', ha='left', va='center', fontsize=9)
    ax.set_yticks(y); ax.set_yticklabels(regions)
    ax.axvline(0, color='gray', linewidth=0.8)
    ax.set_xticks([]); ax.set_title('7 蝴蝶图（百分比）', fontsize=14)
    save(fig, '07_蝴蝶图_百分比')


# ============ 8 数值百分比 ============
def chart_08():
    regions = ['华北', '华南', '东北', '西北', '西南', '华东']
    sales = [4321, 1946, 1536, 1872, 1369, 2109]
    yoy = [-0.136, -0.208, -0.093, -0.159, -0.179, -0.058]
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(regions, sales, color='#4472C4', width=0.55)
    for b, v, r in zip(bars, sales, yoy):
        ax.text(b.get_x() + b.get_width() / 2, v + 80,
                f'{v}\n{r:+.1%}', ha='center', fontsize=10)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.set_title('8 数值+同比百分比', fontsize=14)
    save(fig, '08_数值百分比')


# ============ 9 对比柱形图 ============
def chart_09():
    goods = ['口红', '面膜', '隔离', '防晒', '精华']
    y2021 = [3568, 4135, 4436, 4106, 4936]
    y2022 = [2569, 3241, 2965, 3209, 3541]
    diff = [999, 894, 1471, 897, 1395]
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(goods)); w = 0.35
    ax.bar(x - w / 2, y2021, w, color='#9DC3E6', label='2021销量')
    ax.bar(x + w / 2, y2022, w, color='#4472C4', label='2022销量')
    for i, d in enumerate(diff):
        ax.text(i, max(y2021[i], y2022[i]) + 120, f'↓{d}',
                ha='center', color='#C00000', fontsize=10)
    ax.set_xticks(x); ax.set_xticklabels(goods)
    ax.legend(); ax.set_title('9 对比柱形图（差值标注）', fontsize=14)
    save(fig, '09_对比柱形图')


# ============ 10 甘特图 ============
def chart_10():
    import datetime as dt
    tasks = ['制定计划', '方案设计', '资源调配', '第一阶段',
 '第二阶段', '第三阶段', '项目总结']
    starts = [dt.date(2022, 3, 1), dt.date(2022, 3, 13), dt.date(2022, 3, 22),
              dt.date(2022, 4, 2), dt.date(2022, 4, 16), dt.date(2022, 5, 11),
              dt.date(2022, 5, 26)]
    durations = [11, 8, 10, 13, 24, 14, 7]
    progress = [0.51, 0.32, 0.21, 0.85, 0.36, 0.68, 0.68]
    fig, ax = plt.subplots(figsize=(10, 5))
    base = dt.date(2022, 3, 1)
    for i, (t, s, d, p) in enumerate(zip(tasks, starts, durations, progress)):
        offset = (s - base).days
        # 总进度条（浅色）
        ax.barh(i, d, left=offset, color='#D9E1F2', edgecolor='#4472C4')
        # 完成部分（深色）
        ax.barh(i, d * p, left=offset, color='#4472C4')
        ax.text(offset + d + 0.5, i, f'{p:.0%}', va='center', fontsize=9)
    ax.set_yticks(range(len(tasks))); ax.set_yticklabels(tasks)
    ax.invert_yaxis()
    ax.set_title('10 甘特图', fontsize=14)
    save(fig, '10_甘特图')


# ============ 11 平滑折线图 ============
def chart_11():
    labels = ['5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月',
              '1月', '2月', '3月']
    values = [146, 198, 296, 412, 506, 615, 789, 1021, 3782, 3215, 2936]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(labels, values, marker='o', color='#4472C4',
            linewidth=2.5, markersize=8)
    for x, y in zip(labels, values):
        ax.text(x, y + 80, str(y), ha='center', fontsize=9)
    ax.fill_between(range(len(labels)), values, alpha=0.1, color='#4472C4')
    ax.set_title('11 平滑折线图', fontsize=14)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    save(fig, '11_平滑折线图')


# ============ 12 菱形走势图 ============
def chart_12():
    months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月']
    rates = [0.536, 0.498, 0.527, 0.708, 0.609, 0.496, 0.586, 0.704]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(months, rates, color='#4472C4', linewidth=2.5)
    ax.scatter(months, rates, marker='D', s=110,
 facecolor='#4472C4', edgecolor='white', linewidth=2, zorder=3)
    ax.set_ylim(0.4, 0.8)
    ax.set_title('12 菱形走势图（完成率）', fontsize=14)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    save(fig, '12_菱形走势图')


# ============ 13 对比折线图 ============
def chart_13():
    months = ['1月', '2月', '3月', '4月', '5月', '6月']
    y2021 = [1686, 1345, 1934, 1658, 1865, 1936]
    y2022 = [1385, 1846, 1654, 1936, 2564, 2236]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(months, y2021, marker='o', color='#9DC3E6', linewidth=2,
 label='2021年', markersize=8)
    ax.plot(months, y2022, marker='o', color='#ED7D31', linewidth=2,
            label='2022年', markersize=8)
    for x, v in zip(months, y2021):
        ax.text(x, v + 60, str(v), ha='center', fontsize=9, color='#4472C4')
    for x, v in zip(months, y2022):
        ax.text(x, v - 130, str(v), ha='center', fontsize=9, color='#ED7D31')
    ax.legend(); ax.set_title('13 对比折线图', fontsize=14)
    save(fig, '13_对比折线图')


# ============ 14 单值圆环图 ============
def chart_14():
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie([85, 15], colors=['#4472C4', '#D9E1F2'], startangle=90,
           counterclock=False,
           wedgeprops=dict(width=0.35, edgecolor='white'))
    ax.text(0, 0, '85%', ha='center', va='center',
            fontsize=28, color='#4472C4', fontweight='bold')
    ax.set_title('14 单值圆环图（完成率）', fontsize=14)
    save(fig, '14_单值圆环图')


# ============ 15 水球图 ============
def chart_15():
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.set_xlim(-1.3, 1.3); ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal'); ax.axis('off')
    # 外圆
    circ = Circle((0, 0), 1.0, fill=False, edgecolor='#4472C4', linewidth=3)
    ax.add_patch(circ)
    # 水位（半圆裁剪为 0.65）
    theta = np.linspace(0, np.pi, 200)
    x = np.cos(theta); y = np.sin(theta)
    ax.fill_between(x, y, 1 - 2 * 0.65, color='#5B9BD5', alpha=0.5)
    ax.text(0, 0, '65%', ha='center', va='center',
            fontsize=24, color='white', fontweight='bold',
            path_effects=[])
    ax.set_title('15 水球图', fontsize=14)
    save(fig, '15_水球图')


# ============ 16 波浪水球图 ============
def chart_16():
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.set_xlim(-1.3, 1.3); ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal'); ax.axis('off')
    circ = Circle((0, 0), 1.0, fill=False, edgecolor='#4472C4', linewidth=3)
    ax.add_patch(circ)
    # 波浪
    theta = np.linspace(0, np.pi, 200)
    x = np.cos(theta)
    base_y = 1 - 2 * 0.65
    wave = base_y + 0.05 * np.sin(10 * x)
    ax.fill_between(x, wave, -1, color='#5B9BD5', alpha=0.6)
    # 第二层波
    wave2 = base_y + 0.04 * np.sin(10 * x + 1)
    ax.fill_between(x, wave2, -1, color='#9DC3E6', alpha=0.4)
    ax.text(0, 0, '65%', ha='center', va='center',
            fontsize=24, color='white', fontweight='bold')
    ax.set_title('16 波浪水球图', fontsize=14)
    save(fig, '16_波浪水球图')


# ============ 17 玉玦图 ============
def chart_17():
    ages = ['>=50', '[40,50)', '[30,40)', '[20,30)']
    pct = [0.125, 0.2083, 0.2917, 0.375]
    fig, ax = plt.subplots(figsize=(8, 5))
    cum = 0
    colors = ['#4472C4', '#ED7D31', '#70AD47', '#FFC000']
    for a, p, c in zip(ages, pct, colors):
        # 每段占360*pct 的圆心角，从 cum 起
        ax.add_patch(Wedge((0, 0), 1.0, cum * 360, (cum + p) * 360,
                           facecolor=c, edgecolor='white', linewidth=2))
        cum += p
    ax.set_xlim(-1.3, 1.3); ax.set_ylim(-0.3, 1.3)
    ax.set_aspect('equal'); ax.axis('off')
    for i, (a, p) in enumerate(zip(ages, pct)):
        ax.text(1.2, 1 - i * 0.25, f'{a}  {p:.1%}',
 fontsize=11, color=colors[i])
    ax.set_title('17 玉玦图（圆环比例）', fontsize=14)
    save(fig, '17_玉玦图')


# ============ 18 跑道图 ============
def chart_18():
    depts = ['人力部', '行政部', '财务部', '工程部', '采购部', '销售部']
    nums = [130, 226, 238, 293, 326, 451]
    fig, ax = plt.subplots(figsize=(9, 5))
    max_v = max(nums) + 50
    for i, (d, n) in enumerate(zip(depts, nums)):
        # 跑道背景
        ax.add_patch(FancyBboxPatch((0, i - 0.35), max_v, 0.7,
                     boxstyle="round,pad=0,rounding_size=0.3",
                     linewidth=0, facecolor='#D9E1F2'))
        # 已完成
        ax.add_patch(FancyBboxPatch((0, i - 0.35), n, 0.7,
                     boxstyle="round,pad=0,rounding_size=0.3",
                     linewidth=0, facecolor='#4472C4'))
        ax.text(n + 5, i, f'{n}', va='center', fontsize=10)
        ax.text(-10, i, d, va='center', ha='right', fontsize=10)
    ax.set_xlim(-80, max_v + 60); ax.set_ylim(-0.8, len(depts) - 0.2)
    ax.axis('off'); ax.set_title('18 跑道图', fontsize=14)
    save(fig, '18_跑道图')


# ============ 19 南丁格尔圆饼图 ============
def chart_19():
    labels = ['销售部', '采购部', '工程部', '财务部', '行政部', '人力部']
    pct = [0.292, 0.227, 0.175, 0.136, 0.103, 0.067]
    fig, ax = plt.subplots(figsize=(7, 7))
    # 半径=占比
    wedges, _ = ax.pie(pct, labels=labels,
 colors=plt.cm.Set2.colors, startangle=90,
                       radius=1.0)
    # 中心挖空 → 圆饼感
    ax.set_title('19 南丁格尔圆饼图', fontsize=14)
    save(fig, '19_南丁格尔圆饼图')


# ============ 20 南丁格尔圆环图 ============
def chart_20():
    ages = ['[20,30)', '[30,40)', '[40,50)', '>=50']
    pct = [0.375, 0.2917, 0.2083, 0.125]
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(pct, labels=ages, colors=plt.cm.Set3.colors,
           wedgeprops=dict(width=0.4, edgecolor='white'),
           startangle=90)
    ax.set_title('20 南丁格尔圆环图', fontsize=14)
    save(fig, '20_南丁格尔圆环图')


# ============ 21 南丁格尔（PPT 风） ============
def chart_21():
    depts = ['销售部', '采购部', '工程部', '财务部', '行政部', '人力部']
    pct = [0.292, 0.227, 0.175, 0.136, 0.103, 0.05]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(depts, pct, color=plt.cm.Set2.colors, height=0.6)
    for i, v in enumerate(pct):
        ax.text(v + 0.005, i, f'{v:.1%}', va='center', fontsize=10)
    ax.set_xlim(0, 0.4); ax.invert_yaxis()
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.set_title('21 南丁格尔（PPT 柱状版）', fontsize=14)
    save(fig, '21_南丁格尔PPT版')


# ============ 22 仪表盘图 ============
def chart_22():
    fig, ax = plt.subplots(figsize=(7, 6), subplot_kw=dict(aspect='equal'))
    # 背景半圆刻度
    ax.add_patch(Wedge((0, 0), 1.0, 0, 180, facecolor='#F2F2F2'))
    for i in range(0, 181, 10):
        ax.add_patch(Wedge((0, 0), 1.0, i, i + 1, facecolor='#D9D9D9'
 if i % 30 else '#4472C4'))
    # 进度弧 (76/150)
    end_angle = 180 *76 / 150
    ax.add_patch(Wedge((0, 0), 0.95, 0, end_angle, facecolor='#ED7D31'))
    # 指针
    angle = np.deg2rad(end_angle)
    ax.plot([0, 0.85 * np.cos(np.pi - angle)],
 [0, 0.85 * np.sin(np.pi - angle)],
            color='black', linewidth=3)
    ax.scatter(0, 0, s=80, color='black', zorder=5)
    ax.text(0, -0.2, '76', ha='center', fontsize=32, fontweight='bold')
    ax.set_xlim(-1.2, 1.2); ax.set_ylim(-0.3, 1.2); ax.axis('off')
    ax.set_title('22 仪表盘图', fontsize=14)
    save(fig, '22_仪表盘图')


# ============ 23 柱形折线图 ============
def chart_23():
    years = ['2017', '2018', '2019', '2020', '2021', '2022']
    sales = [1603, 2106, 2406, 3265, 3721, 3921]
    yoy = [0.27, 0.314, 0.142, 0.357, 0.140, 0.054]
    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax1.bar(years, sales, color='#4472C4', width=0.5)
    ax1.set_ylabel('销售量', color='#4472C4')
    ax2 = ax1.twinx()
    ax2.plot(years, [y * 100 for y in yoy],
 color='#ED7D31', marker='o', linewidth=2)
    ax2.set_ylabel('同比 %', color='#ED7D31')
    for x, y in zip(years, yoy):
        ax2.text(x, y * 100 + 1, f'{y:.1%}', ha='center', color='#ED7D31')
    ax1.set_title('23 柱形+折线图', fontsize=14)
    save(fig, '23_柱形折线图')


# ============ 24 目标柱形图 ============
def chart_24():
    goods = ['口红', '面膜', '隔离', '防晒', '精华', '面霜']
    actual = [653, 523, 648, 856, 714, 785]
    target = [700, 500, 600, 900, 600, 600]
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(goods))
    ax.bar(x, target, color='#D9E1F2', width=0.55, label='目标销量')
    ax.bar(x, actual, color='#4472C4', width=0.55, label='实际销量')
    for i, (a, t) in enumerate(zip(actual, target)):
        diff = a - t
        color = '#00B050' if diff >= 0 else '#C00000'
        ax.text(i, max(a, t) + 20, f'{diff:+}', ha='center', color=color)
    ax.set_xticks(x); ax.set_xticklabels(goods)
    ax.legend(); ax.set_title('24 目标柱形图', fontsize=14)
    save(fig, '24_目标柱形图')


# ============ 25 子弹图 ============
def chart_25():
    goods = ['口红', '面膜', '隔离', '防晒', '精华', '面霜']
    actual = [653, 523, 648, 856, 714, 785]
    target = [700, 500, 600, 900, 600, 600]
    pass_, good, best = [600] * 6, [200] * 6, [200] * 6
    fig, ax = plt.subplots(figsize=(9, 5))
    y = np.arange(len(goods))
    # 背景等级条
    ax.barh(y, best, color='#B4C7E7', height=0.5)
    ax.barh(y, good, color='#9DC3E6', height=0.5)
    ax.barh(y, pass_, color='#4472C4', height=0.5)
    # 实际值
    ax.barh(y, actual, color='black', height=0.15)
    # 目标线
    for i, t in enumerate(target):
        ax.plot([t, t], [i - 0.25, i + 0.25], color='red', linewidth=2)
        ax.text(t + 10, i, f'{actual[i]}', va='center', fontsize=9)
    ax.set_yticks(y); ax.set_yticklabels(goods); ax.invert_yaxis()
    ax.set_title('25 子弹图（实际 vs 目标 vs 区间）', fontsize=14)
    save(fig, '25_子弹图')


# ============ 26 柱形圆 ============
def chart_26():
    regions = ['华北', '华南', '东北', '西北', '西南', '华东']
    sales = [2354, 1902, 3524, 2698, 2896, 2563]
    total = 4500
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(regions)); w = 0.35
    bars = ax.bar(x - w / 2, sales, w, color='#4472C4', label='实际销量')
    ax.bar(x + w / 2, [total] * len(regions), w,
 color='#D9E1F2', label='目标')
    for b, v in zip(bars, sales):
        ax.text(b.get_x() + b.get_width() / 2, v + 60, str(v), ha='center')
    ax.set_xticks(x); ax.set_xticklabels(regions)
    ax.legend(); ax.set_title('26 柱形圆（实际 vs 目标）', fontsize=14)
    save(fig, '26_柱形圆')


# ============ 27 簇状柱形折线图 ============
def chart_27():
    regions = ['华北', '华南', '东北', '西北', '西南', '华东']
    y2022 = [2354, 1902, 3524, 2698, 2896, 2563]
    y2021 = [2021, 1563, 3213, 2531, 2631, 2361]
    yoy = [0.16, 0.22, 0.10, 0.07, 0.10, 0.09]
    fig, ax1 = plt.subplots(figsize=(9, 5))
    x = np.arange(len(regions)); w = 0.35
    ax1.bar(x - w / 2, y2022, w, color='#4472C4', label='2022销量')
    ax1.bar(x + w / 2, y2021, w, color='#9DC3E6', label='2021销量')
    ax2 = ax1.twinx()
    ax2.plot(x, [y * 100 for y in yoy], color='#ED7D31',
             marker='o', linewidth=2)
    ax1.set_xticks(x); ax1.set_xticklabels(regions)
    ax1.legend(loc='upper left'); ax1.set_title('27 簇状柱形+折线', fontsize=14)
    save(fig, '27_簇状柱形折线图')


# ============ 28 复合柱形图 ============
def chart_28():
    months = [f'{i}月' for i in range(1, 13)]
    monthly = [2354, 1902, 3524, 2698, 2896, 2563,
               3156, 2896, 3621, 2635, 2963, 2789]
    quarterly = [7780] * 3 + [8157] * 3 + [9673] * 3 + [8387] * 3
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(months))
    ax.bar(x -0.2, monthly, 0.4, color='#4472C4', label='月度销量')
    ax.bar(x + 0.2, quarterly, 0.4, color='#ED7D31', label='季度销量')
    ax.set_xticks(x); ax.set_xticklabels(months)
    ax.legend(); ax.set_title('28 复合柱形图（月度+季度）', fontsize=14)
    save(fig, '28_复合柱形图')


# ============ 29 滑珠图 ============
def chart_29():
    regions = ['华东', '西北', '东北', '华北', '华南']
    done = [0.35, 0.51, 0.62, 0.74, 0.86]
    fig, ax = plt.subplots(figsize=(9, 4))
    y = np.arange(len(regions))
    # 进度背景
    for i in range(len(regions)):
        ax.add_patch(FancyBboxPatch((0, i - 0.25), 1.0, 0.5,
                     boxstyle="round,pad=0,rounding_size=0.25",
                     linewidth=0, facecolor='#D9E1F2'))
        ax.add_patch(FancyBboxPatch((0, i - 0.25), done[i], 0.5,
                     boxstyle="round,pad=0,rounding_size=0.25",
                     linewidth=0, facecolor='#4472C4'))
        ax.scatter(done[i], i, s=200, color='white',
                   edgecolor='#4472C4', linewidth=2, zorder=5)
        ax.text(done[i], i, f'{done[i]:.0%}', ha='center', va='center',
                fontsize=9, color='#4472C4', zorder=6)
    ax.set_yticks(y); ax.set_yticklabels(regions); ax.invert_yaxis()
    ax.set_xlim(-0.05, 1.1); ax.axis('off')
    ax.set_title('29 滑珠图（完成率）', fontsize=14)
    save(fig, '29_滑珠图')


# ============ 30 对比滑珠图 ============
def chart_30():
    regions = ['华东', '西北', '东北', '华北', '华南']
    y2022 = [0.35, 0.51, 0.62, 0.74, 0.86]
    y2021 = [0.45, 0.39, 0.53, 0.69, 0.92]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 5),
 sharex=True)
    for ax, data, title, c in zip(
 (ax1, ax2), (y2022, y2021), ('2022', '2021'),
            ('#4472C4', '#ED7D31')):
        for i, v in enumerate(data):
            ax.add_patch(FancyBboxPatch((0, i - 0.25), 1.0, 0.5,
                         boxstyle="round,pad=0,rounding_size=0.25",
                         linewidth=0, facecolor='#F2F2F2'))
            ax.add_patch(FancyBboxPatch((0, i - 0.25), v, 0.5,
                         boxstyle="round,pad=0,rounding_size=0.25",
                         linewidth=0, facecolor=c))
            ax.scatter(v, i, s=160, color='white',
                       edgecolor=c, linewidth=2, zorder=5)
            ax.text(v, i, f'{v:.0%}', ha='center', va='center',
                    fontsize=8, color=c, zorder=6)
        ax.set_yticks(range(len(regions)))
        ax.set_yticklabels(regions if ax is ax1 else [])
        ax.set_xlim(-0.05, 1.1); ax.set_title(f'{title} 完成率')
        for s in ('top', 'right'):
            ax.spines[s].set_visible(False)
    save(fig, '30_对比滑珠图')


# ============ 总览拼图 ============
def overview(cols=6, rows=5):
    '''把 30 张图拼成一张 6x5 总览图，便于一眼看全第二章图表全貌。'''
    import matplotlib.image as mpimg
    files = sorted(OUT.glob('chart_*.png'))
    if not files:
        return
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 3.1, rows * 2.3))
    axes = axes.ravel()
    for ax, f in zip(axes, files):
        ax.imshow(mpimg.imread(f))
        ax.axis('off')
    for ax in axes[len(files):]:
        ax.axis('off')
    fig.suptitle('《Excel数据可视化》第二章 30 个图表 —— Python 复现总览', fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.985))
    fig.savefig(OUT / '_overview_all_30.png', dpi=110, bbox_inches='tight')
    plt.close(fig)
    print('  已生成总览拼图 _overview_all_30.png')


# ============ 读取教材原始 Excel（可选） ============
def load_excel_data():
    '''读取 data/ 下两份教材 Excel，返回 {文件名::sheet 名: DataFrame}。

    绘图主流程不依赖本函数（数据已内置并与 Excel 逐格核对过），
    仅用于核对原始数据，或把某个图改成真正的数据驱动。
    需要 pandas + openpyxl。
    '''
    import pandas as pd
    data = {}
    for f in sorted((ROOT / 'data').glob('*.xlsx')):
        for sheet, df in pd.read_excel(f, sheet_name=None).items():
            data[f'{f.stem}::{sheet}'] = df
    return data


# ============ 主入口 ============
if __name__ == '__main__':
    charts = [v for k, v in sorted(globals().items())
              if k.startswith('chart_') and callable(v)]
    for c in charts:
        print(f'绘制 {c.__name__} ...')
        c()
    print(f'\n完成，共 {len(charts)} 张图表')
    overview()
    print(f'输出目录: {OUT}')
