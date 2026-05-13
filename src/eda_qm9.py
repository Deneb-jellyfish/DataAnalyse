from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from torch_geometric.datasets import QM9


ATOM_SYMBOLS = {
    1: "H",
    6: "C",
    7: "N",
    8: "O",
    9: "F",
}


def _describe_series(arr: np.ndarray) -> dict[str, float]:
    a = np.asarray(arr, dtype=np.float64)
    return {
        "n": float(a.size),
        "mean": float(np.mean(a)),
        "std": float(np.std(a)),
        "min": float(np.min(a)),
        "p10": float(np.percentile(a, 10)),
        "p25": float(np.percentile(a, 25)),
        "median": float(np.median(a)),
        "p75": float(np.percentile(a, 75)),
        "p90": float(np.percentile(a, 90)),
        "p99": float(np.percentile(a, 99)),
        "max": float(np.max(a)),
    }


def _df_markdown(df: pd.DataFrame) -> str:
    try:
        return df.to_markdown(index=False)
    except ImportError:
        return "```\n" + df.to_string(index=False) + "\n```"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    figure_dir = repo_root / "outputs" / "figures" / "eda"
    report_dir = repo_root / "outputs" / "reports"
    figure_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    dataset = QM9(root=str(repo_root / "data" / "qm9"))

    atom_counts = np.array([data.num_nodes for data in dataset], dtype=np.int32)
    dipole_values = np.array([float(data.y[0, 0]) for data in dataset], dtype=np.float32)

    property_matrix = np.vstack([data.y[0].numpy() for data in dataset]).astype(np.float32)
    property_columns = [f"prop_{i}" for i in range(property_matrix.shape[1])]
    corr_df = pd.DataFrame(property_matrix, columns=property_columns).corr()

    atomic_number_counter: Counter[int] = Counter()
    for data in dataset:
        atomic_numbers = data.z.numpy().astype(int).tolist()
        atomic_number_counter.update(atomic_numbers)

    atom_labels = []
    atom_sizes = []
    for atomic_num in sorted(atomic_number_counter.keys()):
        atom_labels.append(ATOM_SYMBOLS.get(atomic_num, str(atomic_num)))
        atom_sizes.append(atomic_number_counter[atomic_num])

    sns.set_theme(style="whitegrid")

    size_stats = _describe_series(atom_counts.astype(np.float64))
    dipole_stats = _describe_series(dipole_values.astype(np.float64))

    fig, ax = plt.subplots(figsize=(9, 5.5))
    sns.histplot(atom_counts, bins=30, kde=False, color="#4C72B0", ax=ax)
    ax.axvline(size_stats["mean"], color="#C44E52", linestyle="--", linewidth=1.5, label=f"mean={size_stats['mean']:.2f}")
    ax.axvline(size_stats["median"], color="#8172B3", linestyle="-", linewidth=1.5, label=f"median={size_stats['median']:.1f}")
    ax.set_title("Molecule Size Distribution (Num Atoms)")
    ax.set_xlabel("Number of Atoms")
    ax.set_ylabel("Frequency")
    ax.legend(loc="upper right", fontsize=9)
    stat_lines = (
        f"n={int(size_stats['n'])}\n"
        f"mean={size_stats['mean']:.2f}  std={size_stats['std']:.2f}\n"
        f"min={size_stats['min']:.0f}  p25={size_stats['p25']:.0f}  "
        f"p75={size_stats['p75']:.0f}  max={size_stats['max']:.0f}"
    )
    ax.text(
        0.02,
        0.98,
        stat_lines,
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=8,
        family="monospace",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor="#cccccc", alpha=0.92),
    )
    fig.tight_layout()
    fig.savefig(figure_dir / "mol_size_hist.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    sns.histplot(dipole_values, bins=40, kde=True, color="#55A868", ax=ax)
    ax.axvline(dipole_stats["mean"], color="#C44E52", linestyle="--", linewidth=1.5, label=f"mean={dipole_stats['mean']:.3f} D")
    ax.axvline(dipole_stats["median"], color="#8172B3", linestyle="-", linewidth=1.5, label=f"median={dipole_stats['median']:.3f} D")
    ax.set_title("Dipole Moment Distribution (mu, Debye)")
    ax.set_xlabel("Dipole Moment (Debye)")
    ax.set_ylabel("Frequency")
    ax.legend(loc="upper right", fontsize=9)
    stat_lines = (
        f"n={int(dipole_stats['n'])}\n"
        f"mean={dipole_stats['mean']:.4f}  std={dipole_stats['std']:.4f}\n"
        f"p90={dipole_stats['p90']:.3f}  p99={dipole_stats['p99']:.3f}  max={dipole_stats['max']:.3f}"
    )
    ax.text(
        0.98,
        0.98,
        stat_lines,
        transform=ax.transAxes,
        va="top",
        ha="right",
        fontsize=8,
        family="monospace",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor="#cccccc", alpha=0.92),
    )
    fig.tight_layout()
    fig.savefig(figure_dir / "dipole_hist.png", dpi=180)
    plt.close(fig)

    total_atoms = sum(atom_sizes)
    fig, ax = plt.subplots(figsize=(8, 7))
    wedges, texts, autotexts = ax.pie(
        atom_sizes,
        labels=atom_labels,
        autopct=lambda p: f"{p:.1f}%",
        startangle=110,
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
        textprops={"fontsize": 10},
    )
    ax.set_title("Atom Type Ratio in QM9 (count in legend)")
    legend_lines = [f"{lab}: {cnt:,} ({100.0 * cnt / total_atoms:.2f}%)" for lab, cnt in zip(atom_labels, atom_sizes)]
    ax.legend(
        wedges,
        legend_lines,
        title="Atoms",
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(figure_dir / "atom_ratio_pie.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(
        corr_df,
        cmap="coolwarm",
        center=0.0,
        vmin=-1.0,
        vmax=1.0,
        square=True,
        annot=True,
        fmt=".2f",
        annot_kws={"size": 6},
        cbar_kws={"shrink": 0.75},
        linewidths=0.15,
        linecolor="#f0f0f0",
        ax=ax,
    )
    ax.set_title("Correlation Heatmap of 19 QM9 Targets (Pearson r)")
    corr_abs = np.abs(corr_df.to_numpy(dtype=np.float64).copy())
    np.fill_diagonal(corr_abs, 0.0)
    flat = int(np.argmax(corr_abs))
    i_max, j_max = divmod(flat, corr_abs.shape[1])
    r_max = float(corr_df.iloc[i_max, j_max])
    note = (
        f"Strongest |r| (off-diag): {property_columns[i_max]} vs {property_columns[j_max]} = {r_max:.3f}"
    )
    ax.text(
        0.01,
        -0.06,
        note,
        transform=ax.transAxes,
        fontsize=9,
        va="top",
        ha="left",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor="#cccccc", alpha=0.95),
    )
    fig.tight_layout()
    fig.savefig(figure_dir / "properties_corr_heatmap.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    pairs = []
    cols = list(corr_df.columns)
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            pairs.append((cols[i], cols[j], float(corr_df.iloc[i, j])))
    pairs_df = pd.DataFrame(pairs, columns=["prop_a", "prop_b", "r"]).sort_values("r", key=lambda s: s.abs(), ascending=False)
    pairs_df.head(15).to_csv(report_dir / "eda_corr_top_pairs.csv", index=False)

    pd.DataFrame([size_stats]).to_csv(report_dir / "eda_mol_size_stats.csv", index=False)
    pd.DataFrame([dipole_stats]).to_csv(report_dir / "eda_dipole_stats.csv", index=False)
    pd.DataFrame({"element": atom_labels, "count": atom_sizes, "ratio": [s / total_atoms for s in atom_sizes]}).to_csv(
        report_dir / "eda_atom_counts.csv", index=False
    )

    top_pairs_md = _df_markdown(pairs_df.head(8))
    size_md = _df_markdown(pd.DataFrame([size_stats]))
    dipole_md = _df_markdown(pd.DataFrame([dipole_stats]))
    atom_md = _df_markdown(
        pd.DataFrame(
            {"element": atom_labels, "count": atom_sizes, "ratio_pct": [100.0 * s / total_atoms for s in atom_sizes]}
        )
    )

    notes = [
        "# EDA Notes",
        "",
        "数值摘要另见：`eda_summary.md`、`eda_*_stats.csv`、`eda_corr_top_pairs.csv`。",
        "",
        "## mol_size_hist.png",
        "大多数分子集中在较小原子数区间，说明QM9以小分子为主，长尾较短。",
        "样本规模集中有利于模型稳定训练，但对更大分子的外推能力有限。",
        "",
        "### 分子大小（原子数）描述统计",
        size_md,
        "",
        "## dipole_hist.png",
        "偶极矩分布呈明显偏态，低值样本更多，高值样本相对少。",
        "图中标注 mean/median，并在角标给出 p90/p99/max，便于识别长尾极端值。",
        "",
        "### 偶极矩 mu（Debye）描述统计",
        dipole_md,
        "",
        "## atom_ratio_pie.png",
        "H、C是主导原子类型，F占比较低，存在类别不均衡问题。",
        "稀有原子相关样本可能带来更高预测误差，需要在误差分析中单独关注。",
        "",
        "### 原子计数与占比",
        atom_md,
        "",
        "## properties_corr_heatmap.png",
        "热力图单元格内为 Pearson 相关系数；对角线为 1。",
        "强相关对提示多任务/联合建模可能共享信息，但也需注意共线性对线性模型的影响。",
        "",
        "### 相关性最强的若干性质对（|r| 最大，前 8）",
        top_pairs_md,
        "",
    ]
    (report_dir / "eda_notes.md").write_text("\n".join(notes), encoding="utf-8")

    summary_path = report_dir / "eda_summary.md"
    summary_path.write_text(
        "\n".join(
            [
                "# EDA 数值摘要（成员A）",
                "",
                "## 样本规模",
                f"- 分子数（PyG QM9）: **{len(dataset)}**",
                "",
                "## 分子大小（原子数）",
                size_md,
                "",
                "## 目标偶极矩 mu（Debye）",
                dipole_md,
                "",
                "## 原子类型占比",
                atom_md,
                "",
                "## 性质相关性：|r| 最大的前 15 对",
                _df_markdown(pairs_df.head(15)),
                "",
            ]
        ),
        encoding="utf-8",
    )

    print("EDA complete.")
    print(f"Saved figures in: {figure_dir}")
    print(f"Saved notes in: {report_dir / 'eda_notes.md'}")


if __name__ == "__main__":
    main()
