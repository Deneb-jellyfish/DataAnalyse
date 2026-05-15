from pathlib import Path
import sys

import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import Draw

_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
from qm9_raw_utils import load_qm9_skip_sdf_indices


def load_predictions(pred_path: Path, y_true: np.ndarray) -> tuple[np.ndarray, str]:
    if pred_path.exists():
        pred_df = pd.read_csv(pred_path)
        if "pred" in pred_df.columns:
            y_pred = pred_df["pred"].to_numpy(dtype=np.float32)
        elif "prediction" in pred_df.columns:
            y_pred = pred_df["prediction"].to_numpy(dtype=np.float32)
        else:
            raise ValueError("predictions.csv 缺少 pred/prediction 列。")

        if len(y_pred) < len(y_true):
            raise ValueError("predictions.csv 行数少于当前样本数，无法对齐。")
        return y_pred[: len(y_true)], "external"

    rng = np.random.default_rng(42)
    noise = rng.normal(loc=0.0, scale=0.25 * float(np.std(y_true)), size=len(y_true))
    y_pred = (y_true + noise).astype(np.float32)
    return y_pred, "synthetic"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    raw_dir = repo_root / "data" / "qm9" / "raw"
    fig_dir = repo_root / "outputs" / "figures" / "demo"
    report_dir = repo_root / "outputs" / "reports"
    feature_dir = repo_root / "outputs" / "features"
    fig_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    label_df = pd.read_csv(raw_dir / "gdb9.sdf.csv")
    y_true = label_df["mu"].to_numpy(dtype=np.float32)
    mol_ids = label_df["mol_id"].astype(str).to_numpy()

    skip_sdf = load_qm9_skip_sdf_indices(raw_dir / "uncharacterized.txt")

    RDLogger.DisableLog("rdApp.*")
    supplier = Chem.SDMolSupplier(str(raw_dir / "gdb9.sdf"), removeHs=False, sanitize=False)
    mols = []
    valid_indices = []
    for idx, mol in enumerate(supplier):
        if idx >= len(y_true):
            break
        if idx in skip_sdf:
            continue
        if mol is None:
            continue
        mols.append(mol)
        valid_indices.append(idx)

    valid_indices = np.asarray(valid_indices, dtype=np.int64)
    y_true = y_true[valid_indices]
    mol_ids = mol_ids[valid_indices]

    prediction_file = feature_dir / "predictions.csv"
    y_pred, pred_source = load_predictions(prediction_file, y_true)
    y_pred = y_pred[: len(y_true)]
    abs_err = np.abs(y_pred - y_true)

    best_idx = np.argsort(abs_err)[:5]
    worst_idx = np.argsort(abs_err)[-5:]
    selected_idx = np.concatenate([best_idx, worst_idx])

    selected_mols = [mols[i] for i in selected_idx]
    legends = [
        f"{mol_ids[i]} | True={y_true[i]:.3f}, Pred={y_pred[i]:.3f}, Err={abs_err[i]:.3f}"
        for i in selected_idx
    ]

    img = Draw.MolsToGridImage(
        selected_mols,
        molsPerRow=2,
        subImgSize=(550, 360),
        legends=legends,
        useSVG=False,
    )
    demo_path = fig_dir / "demo_mols.png"
    img.save(str(demo_path))

    selected_err_df = pd.DataFrame(
        {
            "mol_id": [mol_ids[i] for i in selected_idx],
            "true_mu": [float(y_true[i]) for i in selected_idx],
            "pred_mu": [float(y_pred[i]) for i in selected_idx],
            "abs_err": [float(abs_err[i]) for i in selected_idx],
            "contains_F": [any(a.GetAtomicNum() == 9 for a in mols[i].GetAtoms()) for i in selected_idx],
        }
    )
    selected_err_df.to_csv(feature_dir / "demo_selection.csv", index=False)

    notes = [
        "# Demo Notes",
        "",
        f"- Demo图来源: `{demo_path}`。",
        "- 展示10个分子：5个误差最小 + 5个误差最大样本。",
        "- 图例包含真值、预测值、绝对误差，可直接用于答辩展示。",
        "- 建议重点讲解误差较大的样本，并结合 `contains_F` 字段说明稀有原子影响。",
    ]
    if pred_source == "synthetic":
        notes.append("- 当前未检测到成员B/C提供的 `outputs/features/predictions.csv`，已使用合成预测值占位生成Demo。")
    (report_dir / "demo_notes.md").write_text("\n".join(notes) + "\n", encoding="utf-8")

    print("demo figure complete")
    print(f"saved figure: {demo_path}")
    print(f"prediction source: {pred_source}")


if __name__ == "__main__":
    main()
