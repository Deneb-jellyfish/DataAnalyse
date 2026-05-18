from __future__ import annotations

import argparse
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


def _rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train the RandomForest baseline on Morgan fingerprints."
    )
    parser.add_argument("--feature-dir", default="outputs/features")
    parser.add_argument("--split-csv", default="outputs/features/split_index.csv")
    parser.add_argument("--n-estimators", type=int, default=100)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument(
        "--n-jobs",
        type=int,
        default=1,
        help="Use 1 by default to avoid Windows multiprocessing permission issues in restricted shells.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=10,
        help="Grow the forest in chunks so progress can be logged during fit.",
    )
    parser.add_argument("--model-out", default="outputs/models/rf_baseline.joblib")
    parser.add_argument("--pred-out", default="outputs/features/predictions_rf.csv")
    parser.add_argument("--metrics-out", default="outputs/logs/rf_baseline_metrics.csv")
    parser.add_argument("--report-out", default="outputs/reports/rf_baseline_notes.md")
    args = parser.parse_args()

    feature_dir = Path(args.feature_dir)
    split_csv = Path(args.split_csv)

    x_train = np.load(feature_dir / "X_train.npy")
    x_test = np.load(feature_dir / "X_test.npy")
    y_train = np.load(feature_dir / "y_train.npy").astype(np.float32)
    y_test = np.load(feature_dir / "y_test.npy").astype(np.float32)

    print(
        f"[1/5] loaded arrays | "
        f"X_train={x_train.shape} {x_train.dtype} | "
        f"X_test={x_test.shape} {x_test.dtype} | "
        f"y_train={y_train.shape} | y_test={y_test.shape}",
        flush=True,
    )

    split_df = pd.read_csv(split_csv)
    test_rows = split_df.loc[split_df["split"] == "test"].copy()
    if "split_order" in test_rows.columns:
        test_rows = test_rows.sort_values("split_order")
    test_rows = test_rows.reset_index(drop=True)

    print(f"[2/5] loaded split table | test rows={len(test_rows)}", flush=True)

    if len(test_rows) != len(y_test):
        raise ValueError(
            "Test rows in split_index.csv do not match y_test length: "
            f"{len(test_rows)} vs {len(y_test)}"
        )

    model = RandomForestRegressor(
        n_estimators=0,
        random_state=args.random_state,
        n_jobs=args.n_jobs,
        warm_start=True,
    )
    print(
        f"[3/5] training random forest | "
        f"trees={args.n_estimators} | chunk_size={args.chunk_size} | n_jobs={args.n_jobs}",
        flush=True,
    )
    fit_start = time.perf_counter()
    trained_trees = 0
    chunk_size = max(1, args.chunk_size)
    while trained_trees < args.n_estimators:
        next_trees = min(trained_trees + chunk_size, args.n_estimators)
        model.set_params(n_estimators=next_trees)
        chunk_start = time.perf_counter()
        model.fit(x_train, y_train)
        chunk_seconds = time.perf_counter() - chunk_start
        total_seconds = time.perf_counter() - fit_start
        trained_trees = next_trees
        print(
            f"  trained {trained_trees}/{args.n_estimators} trees | "
            f"last_chunk={chunk_seconds:.1f}s | total={total_seconds:.1f}s",
            flush=True,
        )

    print(f"[4/5] predicting on test split", flush=True)
    y_pred = model.predict(x_test).astype(np.float32)

    mse = float(mean_squared_error(y_test, y_pred))
    rmse = _rmse(y_test, y_pred)
    mae = float(mean_absolute_error(y_test, y_pred))

    model_out = Path(args.model_out)
    model_out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_out)

    pred_df = test_rows.loc[:, ["dataset_index", "mol_id", "split", "smiles", "dipole"]].copy()
    pred_df = pred_df.rename(columns={"dipole": "y_true_from_split"})
    pred_df["y_true"] = y_test
    pred_df["y_pred_rf"] = y_pred
    pred_df["abs_err_rf"] = (pred_df["y_pred_rf"] - pred_df["y_true"]).abs()

    pred_out = Path(args.pred_out)
    pred_out.parent.mkdir(parents=True, exist_ok=True)
    pred_df.to_csv(pred_out, index=False, encoding="utf-8")

    metrics_df = pd.DataFrame(
        [
            {
                "model": "random_forest",
                "n_estimators": args.n_estimators,
                "random_state": args.random_state,
                "train_size": int(len(y_train)),
                "test_size": int(len(y_test)),
                "mse": mse,
                "rmse": rmse,
                "mae": mae,
            }
        ]
    )
    metrics_out = Path(args.metrics_out)
    metrics_out.parent.mkdir(parents=True, exist_ok=True)
    metrics_df.to_csv(metrics_out, index=False, encoding="utf-8")

    report_lines = [
        "# RandomForest Baseline Notes",
        "",
        "## Setup",
        f"- Features: `{feature_dir / 'X_train.npy'}` / `{feature_dir / 'X_test.npy'}`",
        f"- Labels: `{feature_dir / 'y_train.npy'}` / `{feature_dir / 'y_test.npy'}`",
        f"- Split alignment: `{split_csv}`",
        f"- Model: `RandomForestRegressor(n_estimators={args.n_estimators}, random_state={args.random_state})`",
        "",
        "## Test Metrics",
        f"- MSE: **{mse:.6f}**",
        f"- RMSE: **{rmse:.6f}**",
        f"- MAE: **{mae:.6f}**",
        "",
        "## Outputs",
        f"- Model: `{model_out}`",
        f"- Predictions: `{pred_out}`",
        f"- Metrics CSV: `{metrics_out}`",
        "",
    ]
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text("\n".join(report_lines), encoding="utf-8")

    print("[5/5] random forest baseline complete", flush=True)
    print(f"saved model: {model_out}", flush=True)
    print(f"saved predictions: {pred_out}", flush=True)
    print(f"saved metrics: {metrics_out}", flush=True)
    print(f"test mse={mse:.6f} | rmse={rmse:.6f} | mae={mae:.6f}", flush=True)


if __name__ == "__main__":
    main()
