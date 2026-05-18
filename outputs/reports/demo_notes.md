# Demo Notes

- Demo图来源: `D:\DataAnalyse\DataAnalyse\outputs\figures\demo\demo_mols.png`。
- 展示10个分子：5个误差最小 + 5个误差最大样本。
- 图例包含真值、预测值、绝对误差，可直接用于答辩展示。
- 建议重点讲解误差较大的样本，并结合 `contains_F` 字段说明稀有原子影响。
- 当前已使用成员 B 的 `outputs/features/predictions.csv` 中 `y_pred_physics` 列，并按 `dataset_index` 与 `split_index.csv` 对齐。
- Demo 候选范围限制在**测试集有真实预测值**的样本上，共 `26167` 条。
