from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import gridspec
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


def _df_markdown(df: pd.DataFrame) -> str:
    try:
        return df.to_markdown(index=False)
    except Exception:
        return "```\n" + df.to_string(index=False) + "\n```"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    feature_dir = repo_root / "outputs" / "features"
    figure_dir = repo_root / "outputs" / "figures" / "clusters"
    report_dir = repo_root / "outputs" / "reports"
    figure_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    x_all = np.load(feature_dir / "X_all.npy")
    y_all = np.load(feature_dir / "y_all.npy")

    rng = np.random.default_rng(42)
    fit_sample_size = min(50000, x_all.shape[0])
    fit_indices = rng.choice(x_all.shape[0], size=fit_sample_size, replace=False)
    x_fit = x_all[fit_indices].astype(np.float32)

    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    kmeans.fit(x_fit)

    labels = np.empty(x_all.shape[0], dtype=np.int64)
    batch_size = 20000
    for start in range(0, x_all.shape[0], batch_size):
        end = min(start + batch_size, x_all.shape[0])
        labels[start:end] = kmeans.predict(x_all[start:end].astype(np.float32))
        print(f"predicted labels: {end}/{x_all.shape[0]}")

    np.save(feature_dir / "cluster_labels.npy", labels)

    viz_sample_size = min(20000, x_all.shape[0])
    viz_indices = rng.choice(x_all.shape[0], size=viz_sample_size, replace=False)
    x_viz = x_all[viz_indices].astype(np.float32)
    labels_viz = labels[viz_indices]

    pca = PCA(n_components=2, random_state=42)
    x_2d = pca.fit_transform(x_viz)

    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(9, 7))
    scatter = plt.scatter(
        x_2d[:, 0],
        x_2d[:, 1],
        c=labels_viz,
        cmap="tab10",
        s=10,
        alpha=0.7,
    )
    plt.title("KMeans Clusters on Morgan Fingerprints (PCA 2D)")
    plt.xlabel("PCA-1")
    plt.ylabel("PCA-2")
    plt.legend(*scatter.legend_elements(), title="Cluster", loc="best")
    plt.tight_layout()
    plt.savefig(figure_dir / "kmeans_pca_scatter.png", dpi=180)
    plt.close()

    box_df = pd.DataFrame({"cluster": labels.astype(int), "dipole": y_all.astype(float)})
    order = sorted(box_df["cluster"].unique().tolist())
    clip_hi = float(np.percentile(box_df["dipole"], 99))
    clip_hi = max(clip_hi * 1.05, 1e-6)

    rows = []
    for cl in order:
        s = box_df.loc[box_df["cluster"] == cl, "dipole"]
        rows.append(
            {
                "cluster": int(cl),
                "count": int(s.shape[0]),
                "mean": float(s.mean()),
                "std": float(s.std(ddof=0)),
                "median": float(s.median()),
                "q1": float(s.quantile(0.25)),
                "q3": float(s.quantile(0.75)),
                "p99": float(s.quantile(0.99)),
                "max_d": float(s.max()),
            }
        )
    cluster_stats = pd.DataFrame(rows)
    summary = cluster_stats.set_index("cluster")

    fig = plt.figure(figsize=(11.5, 7.4))
    gs = gridspec.GridSpec(2, 1, height_ratios=[2.55, 1.0], hspace=0.22)
    ax_box = fig.add_subplot(gs[0])
    sns.boxplot(
        data=box_df,
        x="cluster",
        y="dipole",
        order=order,
        hue="cluster",
        hue_order=order,
        palette="Set2",
        dodge=False,
        legend=False,
        showfliers=False,
        linewidth=1.0,
        ax=ax_box,
    )
    ax_box.set_ylim(0.0, clip_hi)
    ax_box.set_title("Dipole per Cluster (box + whisker; outliers omitted for y-scale)")
    ax_box.set_xlabel("Cluster")
    ax_box.set_ylabel("Dipole Moment (Debye)")
    for xpos, cl in enumerate(order):
        row = summary.loc[cl]
        ax_box.text(
            xpos,
            clip_hi * 0.97,
            f"n={int(row['count'])}\nmd={row['median']:.2f}",
            ha="center",
            va="top",
            fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#bbbbbb", alpha=0.9),
        )
    ax_box.text(
        0.01,
        0.02,
        f"y-axis capped at global p99={clip_hi:.2f} D; full range max={float(box_df['dipole'].max()):.2f} D",
        transform=ax_box.transAxes,
        fontsize=8.5,
        va="bottom",
        ha="left",
        color="#333333",
    )

    ax_tbl = fig.add_subplot(gs[1])
    ax_tbl.axis("off")
    table_rows = []
    for cl in order:
        row = summary.loc[cl]
        table_rows.append(
            [
                str(int(cl)),
                f"{int(row['count']):,}",
                f"{row['median']:.3f}",
                f"{row['mean']:.3f}",
                f"{row['q1']:.3f}",
                f"{row['q3']:.3f}",
                f"{row['p99']:.3f}",
                f"{row['max_d']:.3f}",
            ]
        )
    col_labels = ["Cluster", "N", "Median", "Mean", "Q1", "Q3", "p99", "Max"]
    table = ax_tbl.table(
        cellText=table_rows,
        colLabels=col_labels,
        loc="center",
        cellLoc="center",
        colWidths=[0.09] * len(col_labels),
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.55)

    fig.savefig(figure_dir / "cluster_dipole_boxplot.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    cluster_stats.to_csv(feature_dir / "cluster_stats.csv", index=False)

    notes = [
        "# Cluster Notes",
        "",
        "## 方法",
        "- 聚类: KMeans(k=5, random_state=42, n_init=10)。",
        "- 为控制训练开销，在 50,000 条指纹上拟合质心，再对全量样本分批预测标签。",
        "- 可视化: PCA 在 20,000 条抽样上做二维投影（仅用于直观展示分离趋势）。",
        "",
        "## 偶极矩箱线图（排版说明）",
        "- 主图 y 轴截断到**全局 p99**，并关闭箱线图离群点绘制，避免少数极大偶极矩把箱体压扁。",
        "- 箱体上方标注 **n（簇内样本数）** 与 **md（中位数）**；底部附表给出分位数与 Max，便于报告引用。",
        "- 若需观察极端值，可直接使用 `outputs/features/cluster_stats.csv` 中的 p99/Max。",
        "",
        "## 各簇偶极矩数值摘要",
        _df_markdown(cluster_stats),
        "",
        "## 解读提示",
        "- 若各簇中位数接近但 p99/Max 差异大，说明长尾/极端分子分布不同，后续可结合含 F 比例做误差归因。",
        "- 成员 C 可将 `cluster_labels.npy` 与模型逐样本误差对齐，做簇内 RMSE/MAE 对比。",
        "",
    ]
    (report_dir / "cluster_notes.md").write_text("\n".join(notes), encoding="utf-8")

    print("cluster analysis complete")
    print(f"saved figures to: {figure_dir}")
    print(f"saved labels to: {feature_dir / 'cluster_labels.npy'}")


if __name__ == "__main__":
    main()
