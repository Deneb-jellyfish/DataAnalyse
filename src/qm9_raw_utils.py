"""与 `torch_geometric.datasets.QM9` 的 raw 处理保持一致，便于指纹/可视化与 PyG 样本对齐。"""

from __future__ import annotations

from pathlib import Path

# PyG qm9.py: skip = [int(x.split()[0]) - 1 for x in f.read().split('\n')[9:-2]]
_EXPECTED_SKIP_COUNT = 3054


def load_qm9_skip_sdf_indices(uncharacterized_txt: Path) -> frozenset[int]:
    """
    返回应从 gdb9.sdf 枚举顺序中排除的 0-based 索引集合（与 PyG QM9 一致）。

    `uncharacterized.txt` 须为 Figshare 官方文件（由 PyG `QM9.download()` 拉取）；
    若被占位/损坏，本函数会抛出明确错误，避免与 PyG 条数再次不一致。
    """
    if not uncharacterized_txt.is_file():
        raise FileNotFoundError(
            f"缺少 {uncharacterized_txt}。请运行一次 PyG 的 QM9 下载，或从 QM9 官方数据包中放入该文件。"
        )
    text = uncharacterized_txt.read_text(encoding="utf-8", errors="replace")
    lines = text.split("\n")
    body = lines[9:-2]
    skip: set[int] = set()
    for line in body:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        try:
            skip.add(int(parts[0]) - 1)
        except ValueError:
            continue

    if len(skip) < 3000:
        raise ValueError(
            f"{uncharacterized_txt} 解析得到的跳过索引过少（{len(skip)}），"
            f"预期约 {_EXPECTED_SKIP_COUNT}。请删除占位文件后重新执行 `python data.py` 以拉取官方 raw。"
        )
    return frozenset(skip)
