# 大数据分析及数据可视化

本仓库用于存放大数据分析与数据可视化相关的代码、数据集与笔记。

## 目录结构

```
.
├── README.md
├── .gitignore
├── data/          # 数据集（按实验分子文件夹）
│   └── experiment_01/
├── notebooks/     # Jupyter Notebook 分析文件
├── src/           # 分析与可视化源码
│   └── experiment_01.py
└── output/        # 图表输出（按实验分子文件夹）
    └── experiment_01/
```

> 数据、代码、输出三者均按 `experiment_XX` 编号一一对应，便于后续实验扩展。

## 环境

- Python 3.13
- 常用库：pandas、numpy、matplotlib、seaborn、pyecharts

```bash
pip install pandas numpy matplotlib seaborn pyecharts
```

## 说明

首次初始化仓库，后续内容持续补充。

## 实验目录

| 编号 | 主题 | 代码 | 数据 | 输出 | 依赖库 |
| --- | --- | --- | --- | --- | --- |
| 01 | 《Excel数据可视化》第二章 30 个图表 Python 复现 | `src/experiment_01.py` | `data/experiment_01/` | `output/experiment_01/` | matplotlib / numpy |

### experiment_01 复现的 30 个图表

```
01 渐变柱形图            11 平滑折线图          21 南丁格尔（PPT 风）
02 带均值柱形图          12 菱形走势图          22 仪表盘图
03 渐变圆角柱形图        13 对比折线图          23 柱形折线图
04 标注柱形图            14 单值圆环图          24 目标柱形图
05 层叠柱形图            15 水球图              25 子弹图
06 蝴蝶图                16 波浪水球图          26 柱形圆
07 蝴蝶图（百分比）      17 玉玦图              27 簇状柱形折线图
08 数值百分比            18 跑道图              28 复合柱形图
09 对比柱形图            19 南丁格尔圆饼图      29 滑珠图
10 甘特图                20 南丁格尔圆环图      30 对比滑珠图
```

运行：

```bash
cd 项目根目录
python src/experiment_01.py
# 30 张图会输出到 ./output/experiment_01/chart_XX_名称.png
```

若环境里缺少依赖，改用项目自带的虚拟环境：

```bash
# Windows
.venv\Scripts\python.exe src\experiment_01.py

# macOS / Linux
.venv/bin/python src/experiment_01.py
```

### VS Code 配置

项目已附带 `.vscode/settings.json`，把解释器指向项目自带的 `.venv`，并修复了中文输出乱码。
首次打开项目时确认一下解释器是否正确：

1. `Ctrl+Shift+P` → 输入 `Python: Select Interpreter`
2. 选择 **`.venv`**（显示为 `Python 3.13.x ('.venv': venv)`）
3. 打开 `src/experiment_01.py` → 右上角 ▶ 运行

> 若修改后仍报错 `ModuleNotFoundError`，重启 VS Code 让新配置生效。
> `.gitignore` 忽略了 `.vscode/`，换电脑时需重新配置。

原始数据（两份 Excel，共 30 个工作表，每个 sheet 对应一个图表）：

```
data/
└── experiment_01/
    ├── 第二章 图表(前15).xlsx   # 图表 01 ~ 15
    └── 第二章 图表(后15).xlsx   # 图表 16 ~ 30
```

输出按实验分子文件夹存放，便于后续实验扩展：

```
output/
└── experiment_01/          # 实验01 的全部图表
    ├── chart_01_渐变柱形图.png
    ├── ...
    ├── chart_30_对比滑珠图.png
    └── _overview_all_30.png   # 30 图 6×5 总览拼图
```

### 读取原始 Excel

30 个绘图函数使用内置数据（已与 Excel 逐格核对），不装 pandas 也能出图。
如需核对原始数据或改成数据驱动，可调用脚本内的 `load_excel_data()`：

```python
import sys; sys.path.insert(0, 'src')
from experiment_01 import load_excel_data

data = load_excel_data()                       # 返回 30 个 sheet
print(data['第二章 图表(前15)::1 渐变柱形图'])   # 单看某个图表的数据
```

> 该函数需要 `pandas` + `openpyxl`，绘图主流程不依赖它们。
