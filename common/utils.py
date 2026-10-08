"""
common/utils.py —— 全仓库公共工具

【目录约定】
    仓库根/
      common/                     公共模块（本文件）
      datasets/                   多个实验共用的数据集（如 kdd 银行数据）
      course_a_business_analysis/aNN_xxx/
          main.py                 实验脚本
          data/                   本实验专用原始数据
          output/                 本实验产出的图表与结果表
      course_b_excel_visualization/bNN_xxx/   同上

【路径解析规则】
    实验目录 = 启动脚本所在目录（`python .../main.py` 时自动识别，无需配置）
    load('x.xlsx')  先找 <实验目录>/data/x.xlsx，
                    找不到再找 <仓库根>/datasets/x.xlsx（多实验共用数据）。
    save_fig(...)   一律写入 <实验目录>/output/

职责：
    1) 统一数据读取（自动识别 csv 编码，教材里 GBK / UTF-8 混用）
    2) 统一出图保存（png 静态图 + html 交互图 + csv 结果表）
    3) 打印小标题，让批量运行时输出分层清晰
"""

from __future__ import annotations

import os
import sys

import matplotlib

matplotlib.use("Agg")  # 无界面环境也能出图，便于批量运行
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

# 仓库根目录 = common/ 的上一级
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASETS_DIR = os.path.join(ROOT, "datasets")

# 实验目录，由 init_exp() 显式指定，或由 _guess_exp_dir() 自动推断
_EXP_DIR: str | None = None

# ---------------- 全局绘图基础设置 ----------------
# 等价 Excel 里的「主题字体 + 主题色」：无衬线中文字体、负号正常显示
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 120
plt.rcParams["savefig.dpi"] = 120
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.25
plt.rcParams["grid.color"] = "#B4B2A9"
plt.rcParams["grid.linestyle"] = "--"
plt.rcParams["axes.edgecolor"] = "#B4B2A9"
plt.rcParams["axes.linewidth"] = 0.8
plt.rcParams["axes.labelcolor"] = "#444441"
plt.rcParams["xtick.color"] = "#5F5E5A"
plt.rcParams["ytick.color"] = "#5F5E5A"


# ---------------- 实验目录定位 ----------------
def init_exp(script_file: str) -> str:
    """显式指定实验目录（脚本传 __file__ 即可）。

    一般不需要调用：直接 `python <实验>/main.py` 时能自动识别。
    仅当入口不是普通脚本时需要，例如 `streamlit run app.py`。
    """
    global _EXP_DIR
    _EXP_DIR = os.path.dirname(os.path.abspath(script_file))
    return _EXP_DIR


def exp_dir() -> str:
    """当前实验目录。"""
    global _EXP_DIR
    if _EXP_DIR:
        return _EXP_DIR
    argv0 = sys.argv[0] if sys.argv else ""
    if argv0.endswith(".py"):
        _EXP_DIR = os.path.dirname(os.path.abspath(argv0))
    else:  # 交互式 / notebook 场景，退回当前工作目录
        _EXP_DIR = os.getcwd()
    return _EXP_DIR


def data_dir() -> str:
    """当前实验的 data/ 目录。"""
    return os.path.join(exp_dir(), "data")


def out_dir() -> str:
    """当前实验的 output/ 目录，不存在则创建。"""
    d = os.path.join(exp_dir(), "output")
    os.makedirs(d, exist_ok=True)
    return d


# ---------------- 数据读取 ----------------
def data_path(relpath: str) -> str:
    """把相对路径解析成绝对路径。

    查找顺序：本实验 data/ → 仓库 datasets/（共用数据）。
    两处都没有时给出明确报错，避免 pandas 抛难懂的 FileNotFoundError。
    """
    for base in (data_dir(), DATASETS_DIR):
        p = os.path.join(base, relpath)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(
        "找不到数据文件 {0}\n  已尝试：\n    {1}\n    {2}".format(
            relpath, os.path.join(data_dir(), relpath),
            os.path.join(DATASETS_DIR, relpath))
    )


def load(relpath: str, sheet=0, **kw) -> pd.DataFrame:
    """按扩展名自动选择读取器；csv 自动尝试 utf-8-sig / gbk / utf-8 三种编码。

    教材数据实测：`案例1/订单表.csv` 是 GBK 编码，
    而 `商品类型表.csv`、`雇员表.csv` 是 UTF-8。
    不做编码兜底会随机抛 UnicodeDecodeError。
    """
    path = data_path(relpath)
    if relpath.lower().endswith(".csv"):
        last_err: Exception | None = None
        for enc in ("utf-8-sig", "gbk", "utf-8"):
            try:
                return pd.read_csv(path, encoding=enc, **kw)
            except UnicodeDecodeError as e:  # 换下一种编码重试
                last_err = e
        raise last_err  # type: ignore[misc]
    return pd.read_excel(path, sheet_name=sheet, **kw)


def load_sheets(relpath: str) -> dict:
    """一次把 xlsx 所有 sheet 读成 dict。
    等价 Power BI 里「一次导入多张表」。"""
    return pd.read_excel(data_path(relpath), sheet_name=None)


# ---------------- 结果保存 ----------------
def _rel(out: str) -> str:
    try:
        return os.path.relpath(out, ROOT)
    except ValueError:  # 跨盘符时 relpath 会失败
        return out


def save_fig(fig, filename: str) -> str:
    """保存 matplotlib 图到本实验 output/，并关闭图形释放内存。"""
    out = os.path.join(out_dir(), filename)
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  [图] " + _rel(out))
    return out


def save_html(fig, filename: str) -> str:
    """保存 plotly 交互图到本实验 output/。
    交互图放 GitHub Pages 上可直接点开查看，比 png 更适合展示。"""
    out = os.path.join(out_dir(), filename)
    fig.write_html(out, include_plotlyjs="cdn")
    print("  [图] " + _rel(out))
    return out


def save_table(df: pd.DataFrame, filename: str) -> str:
    """把中间结果（如标签宽表、指标字典）导出到本实验 output/ 供查看。"""
    out = os.path.join(out_dir(), filename)
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print("  [表] " + _rel(out))
    return out


# ---------------- 控制台输出 ----------------
def title(text: str) -> None:
    """控制台小节标题，让批量运行时输出分层清晰。"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def report_head(df: pd.DataFrame, n: int = 5, name: str = "") -> None:
    """打印 DataFrame 的形状与前若干行，便于快速核对数据。"""
    if name:
        print(f"-- {name} --")
    print(f"形状: {df.shape}")
    if not df.empty:
        print(df.head(n).to_string())
