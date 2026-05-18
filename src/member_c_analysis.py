from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import mean_absolute_error, mean_squared_error


def df_markdown(df: pd.DataFrame) -> str:
    try:
        return df.to_markdown(index=False)
    except Exception:
        return "```\n" + df.to_string(index=False) + "\n```"


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def metric_row(model: str, y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float | str]:
    return {
        "model": model,
        "mse": float(mean_squared_error(y_true, y_pred)),
        "rmse": rmse(y_true, y_pred),
        "mae": float(mean_absolute_error(y_true, y_pred)),
    }


def load_predictions(repo_root: Path) -> pd.DataFrame:
    gnn_df = pd.read_csv(repo_root / "outputs" / "features" / "predictions.csv")
    rf_df = pd.read_csv(repo_root / "outputs" / "features" / "predictions_rf.csv")

    merged = gnn_df.merge(
        rf_df.loc[:, ["dataset_index", "y_pred_rf", "abs_err_rf"]],
        on="dataset_index",
        how="inner",
        validate="one_to_one",
    )
    merged["dataset_index"] = merged["dataset_index"].astype(int)
    return merged


def save_experiment_summary(repo_root: Path, pred_df: pd.DataFrame) -> pd.DataFrame:
    y_true = pred_df["y_true"].to_numpy(dtype=np.float32)
    summary_df = pd.DataFrame(
        [
            metric_row("Random Forest", y_true, pred_df["y_pred_rf"].to_numpy(dtype=np.float32)),
            metric_row("Base GNN", y_true, pred_df["y_pred_base"].to_numpy(dtype=np.float32)),
            metric_row("Physics GNN", y_true, pred_df["y_pred_physics"].to_numpy(dtype=np.float32)),
        ]
    )
    summary_df["rank_by_rmse"] = summary_df["rmse"].rank(method="dense").astype(int)
    summary_df = summary_df.sort_values("rmse").reset_index(drop=True)

    logs_dir = repo_root / "outputs" / "logs"
    reports_dir = repo_root / "outputs" / "reports"
    logs_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    summary_df.to_csv(logs_dir / "experiment_results.csv", index=False, encoding="utf-8")

    best = summary_df.iloc[0]
    worst = summary_df.iloc[-1]
    notes = [
        "# Experiment Results",
        "",
        "## Summary",
        df_markdown(summary_df),
        "",
        "## Key Findings",
        f"- Best RMSE: **{best['model']}** = `{best['rmse']:.6f}`",
        f"- Worst RMSE: **{worst['model']}** = `{worst['rmse']:.6f}`",
        f"- Physics GNN vs Random Forest RMSE improvement: `{100 * (summary_df.loc[summary_df['model'] == 'Random Forest', 'rmse'].iloc[0] - summary_df.loc[summary_df['model'] == 'Physics GNN', 'rmse'].iloc[0]) / summary_df.loc[summary_df['model'] == 'Random Forest', 'rmse'].iloc[0]:.2f}%`",
        "",
    ]
    (reports_dir / "experiment_results.md").write_text("\n".join(notes), encoding="utf-8")
    return summary_df


def build_cluster_metrics(repo_root: Path, pred_df: pd.DataFrame) -> pd.DataFrame:
    split_df = pd.read_csv(repo_root / "outputs" / "features" / "split_index.csv")
    cluster_labels = np.load(repo_root / "outputs" / "features" / "cluster_labels.npy")
    test_rows = split_df.loc[split_df["split"] == "test", ["dataset_index", "mol_id", "smiles"]].copy()
    test_rows["dataset_index"] = test_rows["dataset_index"].astype(int)
    test_rows["cluster"] = test_rows["dataset_index"].map(lambda i: int(cluster_labels[i]))

    merged = pred_df.merge(test_rows[["dataset_index", "cluster"]], on="dataset_index", how="left", validate="one_to_one")
    merged["contains_F"] = merged["smiles"].astype(str).str.contains("F")

    rows: list[dict[str, float | int | str]] = []
    for cluster_id, group in merged.groupby("cluster", sort=True):
        y_true = group["y_true"].to_numpy(dtype=np.float32)
        for model_name, pred_col in [
            ("Random Forest", "y_pred_rf"),
            ("Base GNN", "y_pred_base"),
            ("Physics GNN", "y_pred_physics"),
        ]:
            y_pred = group[pred_col].to_numpy(dtype=np.float32)
            rows.append(
                {
                    "cluster": int(cluster_id),
                    "model": model_name,
                    "count": int(len(group)),
                    "contains_F_ratio": float(group["contains_F"].mean()),
                    "mse": float(mean_squared_error(y_true, y_pred)),
                    "rmse": rmse(y_true, y_pred),
                    "mae": float(mean_absolute_error(y_true, y_pred)),
                }
            )
    cluster_metrics = pd.DataFrame(rows).sort_values(["cluster", "rmse", "model"]).reset_index(drop=True)
    cluster_metrics.to_csv(repo_root / "outputs" / "logs" / "cluster_error_metrics.csv", index=False, encoding="utf-8")
    cluster_metrics.to_csv(repo_root / "outputs" / "features" / "cluster_error_metrics.csv", index=False, encoding="utf-8")

    pivot_rmse = cluster_metrics.pivot(index="cluster", columns="model", values="rmse")
    pivot_mae = cluster_metrics.pivot(index="cluster", columns="model", values="mae")
    best_rmse = pivot_rmse["Physics GNN"].idxmin()
    worst_rmse = pivot_rmse["Physics GNN"].idxmax()
    f_ratio = (
        cluster_metrics.loc[cluster_metrics["model"] == "Physics GNN", ["cluster", "contains_F_ratio"]]
        .drop_duplicates()
        .set_index("cluster")["contains_F_ratio"]
    )
    highest_f_cluster = int(f_ratio.idxmax())

    notes = [
        "# Cluster Error Analysis",
        "",
        "## Cluster Metrics",
        df_markdown(cluster_metrics),
        "",
        "## Findings",
        f"- Physics GNN best cluster by RMSE: **Cluster {int(best_rmse)}** = `{pivot_rmse.loc[best_rmse, 'Physics GNN']:.6f}`",
        f"- Physics GNN worst cluster by RMSE: **Cluster {int(worst_rmse)}** = `{pivot_rmse.loc[worst_rmse, 'Physics GNN']:.6f}`",
        f"- Worst cluster F ratio: `{100 * f_ratio.loc[worst_rmse]:.2f}%`",
        f"- Highest F ratio cluster: **Cluster {highest_f_cluster}** = `{100 * f_ratio.loc[highest_f_cluster]:.2f}%`",
        "",
        "## Interpretation",
        "- 当前结果表明：高 F 比例簇整体更难，但**最差簇不一定恰好是 F 比例最高的簇**，说明误差还受其它结构因素共同影响。",
        "- 该分析和成员 A 的聚类图、箱线图一起使用时，能形成“数据分布差异 -> 误差差异”的完整论证链。",
        "",
    ]
    (repo_root / "outputs" / "reports" / "cluster_error_analysis.md").write_text("\n".join(notes), encoding="utf-8")
    return cluster_metrics


def make_figures(repo_root: Path, summary_df: pd.DataFrame, pred_df: pd.DataFrame, cluster_metrics: pd.DataFrame) -> None:
    fig_dir = repo_root / "outputs" / "figures" / "results"
    fig_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        data=summary_df,
        x="model",
        y="rmse",
        hue="model",
        palette=["#CC6B49", "#4C72B0", "#55A868"],
        legend=False,
        ax=ax,
    )
    ax.set_title("RMSE Comparison Across Three Models")
    ax.set_xlabel("")
    ax.set_ylabel("RMSE")
    for idx, row in summary_df.iterrows():
        ax.text(idx, row["rmse"] + 0.01, f"{row['rmse']:.3f}", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    fig.savefig(fig_dir / "exp_rmse_bar.png", dpi=180)
    plt.close(fig)

    violin_df = pd.DataFrame(
        {
            "Absolute Error": np.concatenate(
                [
                    pred_df["abs_err_rf"].to_numpy(dtype=np.float32),
                    pred_df["abs_err_base"].to_numpy(dtype=np.float32),
                    pred_df["abs_err_physics"].to_numpy(dtype=np.float32),
                ]
            ),
            "Model": (
                ["Random Forest"] * len(pred_df)
                + ["Base GNN"] * len(pred_df)
                + ["Physics GNN"] * len(pred_df)
            ),
        }
    )
    violin_order = ["Random Forest", "Base GNN", "Physics GNN"]
    violin_palette = {
        "Random Forest": "#E07070",
        "Base GNN": "#70A0D0",
        "Physics GNN": "#60B87C",
    }
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.violinplot(
        data=violin_df,
        x="Model",
        y="Absolute Error",
        hue="Model",
        order=violin_order,
        palette=violin_palette,
        cut=0,
        inner=None,
        linewidth=1.0,
        legend=False,
        ax=ax,
    )
    sns.boxplot(
        data=violin_df,
        x="Model",
        y="Absolute Error",
        order=violin_order,
        width=0.18,
        showcaps=True,
        showfliers=False,
        boxprops={"facecolor": "white", "zorder": 3},
        whiskerprops={"linewidth": 1.2},
        medianprops={"color": "#ffffff", "linewidth": 2.0},
        ax=ax,
    )
    ax.set_title("Error Distribution Comparison")
    ax.set_xlabel("")
    ax.set_ylabel("Absolute Error (Debye)")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(fig_dir / "violin_error_dist.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    scatter = ax.scatter(
        pred_df["y_true"],
        pred_df["y_pred_physics"],
        s=10,
        alpha=0.45,
        c=pred_df["abs_err_physics"],
        cmap="viridis",
    )
    lim_low = float(min(pred_df["y_true"].min(), pred_df["y_pred_physics"].min()))
    lim_high = float(max(pred_df["y_true"].max(), pred_df["y_pred_physics"].max()))
    ax.plot([lim_low, lim_high], [lim_low, lim_high], linestyle="--", color="#C44E52", linewidth=1.2)
    ax.set_title("Best Model: Physics GNN Predicted vs True")
    ax.set_xlabel("True Dipole Moment")
    ax.set_ylabel("Predicted Dipole Moment")
    cbar = fig.colorbar(scatter, ax=ax)
    cbar.set_label("Absolute Error")
    fig.tight_layout()
    fig.savefig(fig_dir / "best_model_scatter.png", dpi=180)
    plt.close(fig)

    base_log = pd.read_csv(repo_root / "outputs" / "logs" / "train_gnn_base_metrics.csv")
    physics_log = pd.read_csv(repo_root / "outputs" / "logs" / "train_gnn_physics_metrics.csv")
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.plot(base_log["epoch"], base_log["test_mse"], label="Base GNN test_mse", color="#4C72B0")
    ax.plot(base_log["epoch"], base_log["train_mse"], label="Base GNN train_mse", color="#4C72B0", linestyle="--")
    ax.plot(physics_log["epoch"], physics_log["test_mse"], label="Physics GNN test_mse", color="#55A868")
    ax.plot(physics_log["epoch"], physics_log["train_mse"], label="Physics GNN train_mse", color="#55A868", linestyle="--")
    ax.set_title("GNN Training Curves")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("MSE")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(fig_dir / "gnn_loss_curves.png", dpi=180)
    plt.close(fig)

    rmse_plot_df = cluster_metrics.loc[:, ["cluster", "model", "rmse"]]
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    sns.barplot(data=rmse_plot_df, x="cluster", y="rmse", hue="model", palette="Set2", ax=ax)
    ax.set_title("Cluster-wise RMSE Comparison")
    ax.set_xlabel("Cluster")
    ax.set_ylabel("RMSE")
    fig.tight_layout()
    fig.savefig(fig_dir / "cluster_rmse_bar.png", dpi=180)
    plt.close(fig)

    mae_plot_df = cluster_metrics.loc[:, ["cluster", "model", "mae"]]
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    sns.barplot(data=mae_plot_df, x="cluster", y="mae", hue="model", palette="Set2", ax=ax)
    ax.set_title("Cluster-wise MAE Comparison")
    ax.set_xlabel("Cluster")
    ax.set_ylabel("MAE")
    fig.tight_layout()
    fig.savefig(fig_dir / "cluster_mae_bar.png", dpi=180)
    plt.close(fig)

    pivot_rmse = cluster_metrics.pivot(index="model", columns="cluster", values="rmse")
    pivot_mae = cluster_metrics.pivot(index="model", columns="cluster", values="mae")
    heatmap_order = ["Random Forest", "Base GNN", "Physics GNN"]
    pivot_rmse = pivot_rmse.reindex(heatmap_order)
    pivot_mae = pivot_mae.reindex(heatmap_order)

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.2))
    sns.heatmap(
        pivot_rmse,
        ax=axes[0],
        annot=True,
        fmt=".3f",
        cmap="YlOrRd",
        linewidths=0.5,
        linecolor="white",
        cbar_kws={"label": "RMSE (D)"},
    )
    axes[0].set_title("RMSE Heatmap: Model x Cluster")
    axes[0].set_xlabel("Cluster ID")
    axes[0].set_ylabel("Model")

    sns.heatmap(
        pivot_mae,
        ax=axes[1],
        annot=True,
        fmt=".3f",
        cmap="YlOrRd",
        linewidths=0.5,
        linecolor="white",
        cbar_kws={"label": "MAE (D)"},
    )
    axes[1].set_title("MAE Heatmap: Model x Cluster")
    axes[1].set_xlabel("Cluster ID")
    axes[1].set_ylabel("Model")

    plt.suptitle("Per-Cluster Error Analysis Across Models", fontsize=13)
    fig.tight_layout()
    fig.savefig(fig_dir / "heatmap_model_cluster.png", dpi=180)
    plt.close(fig)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    pred_df = load_predictions(repo_root)
    summary_df = save_experiment_summary(repo_root, pred_df)
    cluster_metrics = build_cluster_metrics(repo_root, pred_df)
    make_figures(repo_root, summary_df, pred_df, cluster_metrics)

    print("member C analysis complete")
    print(f"saved experiment summary: {repo_root / 'outputs' / 'reports' / 'experiment_results.md'}")
    print(f"saved cluster analysis: {repo_root / 'outputs' / 'reports' / 'cluster_error_analysis.md'}")
    print(f"saved figures: {repo_root / 'outputs' / 'figures' / 'results'}")


if __name__ == "__main__":
    main()
