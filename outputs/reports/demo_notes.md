# Demo Notes（分子结构示意）

## 产出

- **图片路径（相对仓库根目录）**: `outputs/figures/demo/demo_mols.png`
- **挑选规则**: 在可对齐的样本上，按绝对误差 \(|\\hat{\\mu}-\\mu|\) 排序，取 **5 个最小误差 + 5 个最大误差** 共 10 个分子；结构由 RDKit 绘制，图例含 `mol_id`、真值、预测值与绝对误差。
- **辅助表**: `outputs/features/demo_selection.csv`（含 `contains_F` 字段，便于答辩时讨论数据不均衡）

## 预测值来源

1. **优先**: 若存在 `outputs/features/predictions.csv`，正式预测结果应读取其中的 `y_pred_physics` 列，并用 `dataset_index` 与 `split_index.csv` 对齐。
2. **占位**: 若文件不存在，则使用基于真值加高斯噪声的**合成预测**，仅用于版式与流程演示；正式答辩前应替换为成员 B 的真实 `predictions.csv` 后重新运行：

```bash
conda activate da
python src/demo_molecules.py
```

## 报告撰写提示

- 对误差大的分子，结合 `contains_F` 与簇标签（`cluster_labels.npy`）讨论是否为**稀有元素 / 特定子结构**导致难学。
- Demo 图适合放在「案例分析」或「误差可视化」小节，不宜替代整体 RMSE/MAE 指标。
