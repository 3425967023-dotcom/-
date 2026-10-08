# 商业数据分析 & Excel 数据可视化 —— Python 迁移实验

把两门课程的教材内容从 **Power BI / Excel** 迁移到 **Python** 实现，每个实验独立可运行、
自带数据与产出，便于交作业与复现。

| 课程 | 教材 | 实验数 | 迁移方向 |
| --- | --- | --- | --- |
| 课程一 | 《CDA 一级认证教材：商业数据分析》 | 12 | Power BI / Excel / MySQL → Python |
| 课程二 | 《Excel数据可视化——从图表到数据大屏》 | 5 | Excel 图表 → matplotlib / plotly |

---

## 一、目录结构

```
.
├── README.md                     本文件
├── requirements.txt              依赖清单
├── run_all.py                    一键运行全部实验（自动发现实验目录）
├── common/                       公共模块
│   ├── utils.py                  数据读取（自动识别 GBK/UTF-8）、出图与结果表保存
│   └── style.py                  图表修饰规范（配色 / 字体 / 三级文本体系）
├── datasets/
│   └── kdd/                      A09、A10 共用的 KDD 银行行为数据集（8 张表）
├── course_a_business_analysis/   《商业数据分析》
│   ├── a01_dimensional_model/
│   │   ├── main.py               实验脚本
│   │   ├── data/                 本实验原始数据
│   │   └── output/               本实验产出（图表 / 结果表）
│   ├── a02_basic_paradigms/
│   └── ... a12
├── course_b_excel_visualization/ 《Excel数据可视化》
│   ├── b01_chart_structure/
│   ├── b02_styling/
│   ├── b03_gallery/
│   ├── b04_dynamic/
│   └── b05_dashboard/
└── notebooks/                    Jupyter Notebook 备用目录
```

**约定**：实验目录一律命名为 `course_*/<课程字母><两位编号>_<英文短名>/`，
入口固定为 `main.py`，数据放同目录 `data/`，产出写同目录 `output/`。
新增实验只要按此约定建目录，`run_all.py` 会自动发现，无需改任何配置。

**关于 `datasets/`**：KDD 银行数据集（`trans.csv` 单文件 61 MB / 105 万行）
被 A09（SQL）与 A10（用户画像）两个实验共用，放在仓库根统一存放，
避免在两个实验目录里各存一份（122 MB）。`load()` 找不到文件时会自动回退到这里。

---

## 二、实验清单

### 课程一《商业数据分析》A01–A12

| 编号 | 目录 | 教材章节 | 迁移的知识点 | 主要产出 |
| --- | --- | --- | --- | --- |
| A01 | `a01_dimensional_model` | 第1章 数据分析思维 | 维度建模：事实表 / 维度表、星型与雪花模型、`CALCULATE(ALL())` 与筛选上下文 | 1 图 + 1 表 |
| A02 | `a02_basic_paradigms` | 第2章-1 基础范式 | 六大范式：波士顿矩阵、RFM、忠诚度、同期群、漏斗、相关分析 | 6 图 + 1 表 |
| A03 | `a03_extended_methods` | 第2章-2 引申方法 | 六类分析方法：趋势、对比、构成、分布、关系、桑基图 | 5 图 + 1 交互 html |
| A04 | `a04_etl` | 第2章-5 Power Query | ETL 四件套：拆分列、数据清洗、横向合并（JOIN）、纵向合并（追加） | 1 表 |
| A05 | `a05_sales_star_model` | 第2章-5 案例1 | 分省销售星型模型 + 6 类 DAX 度量值（SUM / DIVIDE / RANKX / 同比） | 1 图 |
| A06 | `a06_retail_dashboard` | 第2章-5 案例2 | 服装零售 12 表多维看板、KPI 卡片、店铺目标达成率 | 1 图 + 1 表 |
| A07 | `a07_framework` | 第3章 分析框架 | 收入趋势、财务费用三层下钻、电商精准营销客群画像 | 3 图 + 2 表 |
| A08 | `a08_bank_dashboard` | 第5章 业务数据分析 | 银行理财看板（29 日时点外推、2500 万目标预警）、渠道归因量效应/结构效应分解 | 2 图 + 1 表 |
| A09 | `a09_sql` | 第8章 SQL 与 MySQL | 用 sqlite3 迁移：建表导入、GROUP BY/HAVING、多表 JOIN、子查询、窗口函数 | 7 结果表 |
| A10 | `a10_user_profile` | 第9章 用户标签与画像 | 5 类标签构建、用户画像宽表、高价值客群提取 | 1 图 + 2 表 |
| A11 | `a11_time_series` | 第10章 效应分解预报 | 时间序列 T×S×R 分解、乘法季节因子、趋势外推 12 期预报 | 1 图 + 1 表 |
| A12 | `a12_indicator_system` | 第7/13章 指标体系 | 指标字典结构化、原子/派生/复合指标口径自动化校验 | 2 表 |

### 课程二《Excel数据可视化》B01–B05

| 编号 | 目录 | 教材章节 | 迁移的知识点 | 主要产出 |
| --- | --- | --- | --- | --- |
| B01 | `b01_chart_structure` | 第二章 图表基础 | 「系列值数量 × 轴标签数量」→ 图表类型决策表；五大关系选图 | 2 图 |
| B02 | `b02_styling` | 第二章 修饰 | 修饰三要素：合理配色（≤3 色）、正确字体、删非必要元素；三级文本体系 | 3 图 |
| B03 | `b03_gallery` | 第二章 图表(前15/后15) | **30 个图表完整复现**：渐变柱形、蝴蝶图、甘特图、水球图、玉玦图、南丁格尔玫瑰、仪表盘、子弹图、滑珠图…… | 30 图 + 总览拼图 |
| B04 | `b04_dynamic` | 第三章 动态图表 | Excel 控件 + VBA → matplotlib 动画（gif）与 plotly 交互播放（html） | 2 gif + 1 html |
| B05 | `b05_dashboard` | 第四章 数据大屏 | 栅格布局数据大屏（matplotlib 静态版）+ streamlit 可交互版 | 1 图 + `app.py` |

---

## 三、环境与运行

```bash
pip install -r requirements.txt
```

逐实验运行：

```bash
python course_a_business_analysis/a01_dimensional_model/main.py
python course_b_excel_visualization/b03_gallery/main.py
```

一键运行全部（自动发现，约 70 秒）：

```bash
python run_all.py              # 全部实验
python run_all.py A06 B05      # 只运行指定编号
python run_all.py --list       # 只列出实验清单
```

交互式大屏（可选，需要 streamlit）：

```bash
streamlit run course_b_excel_visualization/b05_dashboard/app.py
```

产出位置：每个实验的 `output/` 目录。共 **81 个产出文件**：
58 张 png 图表、19 张结果 csv、2 个 gif 动图、2 个交互 html。

---

## 四、环境说明与常见问题

**Python 版本**：3.13

| 库 | 用途 |
| --- | --- |
| pandas / openpyxl | 读取教材 xlsx / csv，做数据聚合 |
| matplotlib | 全部静态图表与动态 gif |
| plotly | 桑基图、动态交互图 |
| streamlit | 可交互数据大屏（B05 可选） |

**中文与编码**（已在 `common/utils.py` 统一处理，无需在各实验里重复配置）：

- matplotlib 中文字体：`Microsoft YaHei` → `SimHei` → `DejaVu Sans` 逐级回退，负号正常显示；
- 教材 csv 编码混用：`订单表.csv` 等为 **GBK**，`商品类型表.csv` 等为 **UTF-8**，
  `load()` 会按 `utf-8-sig → gbk → utf-8` 顺序自动重试，不会抛 `UnicodeDecodeError`；
- B03 的 30 个图表使用**内置数据**（已与 Excel 逐格核对），不装 pandas 也能出图；
  如需核对原始数据，可调用 `b03_gallery/main.py` 里的 `load_excel_data()`。

**重跑后 git 显示 2 个 html 被修改？** 属正常现象。plotly 导出的 html 里含有每次生成都不同的
随机 `div id`（`A03_extended_methods/output/A03_06_sankey.html`、
`b04_dynamic/output/B04_plotly_dynamic.html`），内容语义不变，提交时一并提交即可。

---

## 五、与教材的差异说明

1. **教材缺章**：课程一教材目录含 13 章中的 11 章，缺 **第 4 章、第 6 章**，
   实验清单按实际存在的章节编排。
2. **Power BI 图表插件包**：教材 `第2章/5、PowerBI基本操作/图表安装文件--用于本地增加图表/`
   下的约 90 个 `.pbix` 是图表插件安装包，不是教学内容，未做迁移；
   真正的教学内容（8 个业务模型）已覆盖在 A01–A08。
3. **成品图表文件**：`第2章/2、由基础分析范式引申出的分析方法/data-无答案/` 下 5 个 xlsx
   是成品图表（数据嵌在图表对象里，`read_excel` 读不到数据区），
   A03 中已用等价结构数据重建；仅 `6桑吉图.xlsx` 直接读取了教材原表。
4. **MySQL → sqlite3**：A09 用 Python 内置 `sqlite3` 替代 MySQL，
   零安装、可随仓库分发，SQL 语法结构一致（差异见该实验文件头注释）。
