"""
一键运行全部实验

用法：
    python run_all.py              # 顺序运行全部实验
    python run_all.py A03 B05      # 只运行指定编号的实验
    python run_all.py --list       # 只列出实验清单

实验脚本按 `course_*/<编号>_<名称>/main.py` 的约定自动发现，
新增实验只要建好目录即可，无需修改本文件。
每个实验独立成进程，任一实验失败不影响其余实验继续执行。
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# 编号形如 a01 / b05，取前 3 位作为实验编号（A01 / B05）
LAB_DIR_RE = re.compile(r"^([abAB]\d{2})_")


def discover() -> dict[str, Path]:
    """扫描 course_* 目录，返回 {实验编号: main.py 路径}。"""
    labs: dict[str, Path] = {}
    for course in sorted(ROOT.glob("course_*")):
        if not course.is_dir():
            continue
        for lab in sorted(course.iterdir()):
            if not lab.is_dir():
                continue
            m = LAB_DIR_RE.match(lab.name)
            entry = lab / "main.py"
            if m and entry.exists():
                labs[m.group(1).upper()] = entry
    return dict(sorted(labs.items()))


def main() -> int:
    labs = discover()
    if not labs:
        print("未发现任何实验（约定：course_*/<编号>_<名称>/main.py）")
        return 1

    args = [a.upper() for a in sys.argv[1:]]
    if "--LIST" in args:
        print(f"共发现 {len(labs)} 个实验：")
        for code, path in labs.items():
            print(f"  {code}  {path.relative_to(ROOT)}")
        return 0

    todo = {k: v for k, v in labs.items() if not args or k in args}
    unknown = [a for a in args if a not in labs and not a.startswith("--")]
    if unknown:
        print("未匹配到实验编号：", ", ".join(unknown))
    if not todo:
        print("没有需要运行的实验。可选编号：", ", ".join(labs))
        return 1

    print(f"共 {len(todo)} 个实验待运行\n")
    summary: list[tuple[str, str, float]] = []

    for code, entry in todo.items():
        rel = entry.relative_to(ROOT)
        print("=" * 64)
        print(f"[{code}] {rel}")
        print("=" * 64)
        start = time.time()
        proc = subprocess.run([sys.executable, str(entry)],
                              cwd=ROOT, capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
        cost = time.time() - start
        if proc.returncode == 0:
            print(f"[{code}] 运行成功（{cost:.1f}s）")
            summary.append((code, "成功", cost))
        else:
            print(f"[{code}] 运行失败（{cost:.1f}s）")
            print("-" * 64)
            print((proc.stderr or proc.stdout or "")[-2000:])
            summary.append((code, "失败", cost))
        print()

    print("=" * 64)
    print("运行汇总")
    print("=" * 64)
    print(f"{'编号':<6}{'状态':<6}{'耗时(s)':>8}")
    for code, status, cost in summary:
        print(f"{code:<6}{status:<6}{cost:>8.1f}")

    failed = [c for c, s, _ in summary if s == "失败"]
    if failed:
        print(f"\n失败实验：{', '.join(failed)}")
        return 1
    print("\n全部通过。图表与结果表已按实验输出到各自的 output/ 目录。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
