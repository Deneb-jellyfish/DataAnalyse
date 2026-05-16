# outputs/reports 说明（成员A 产出索引）

本目录存放**可直接写入课程报告**的文字结论、统计表与脚本导出的 CSV。图表文件在 `outputs/figures/` 下，特征与标签在 `outputs/features/` 下。

## 文件一览

| 文件 | 内容 |
|------|------|
| `eda_notes.md` | 四张 EDA 图的解读 + 关键描述统计（与图内标注一致） |
| `eda_summary.md` | EDA 数值摘要汇总（分子数、原子数/偶极矩分位数、原子占比、强相关性质对） |
| `eda_mol_size_stats.csv` | 分子大小（原子数）一行汇总统计 |
| `eda_dipole_stats.csv` | 偶极矩 mu 一行汇总统计 |
| `eda_atom_counts.csv` | 各元素原子计数与占比 |
| `eda_corr_top_pairs.csv` | \|Pearson r\| 最大的性质对（前 15） |
| `feature_notes.md` | 指纹导出约定、`split_index.csv` 字段说明、给成员 B/C 的对接说明 |
| `gnn_notes.md` | 成员 B 的 GNN 模型、训练命令、预测输出与指标汇总 |
| `cluster_notes.md` | KMeans/PCA 方法说明 + 各簇偶极矩数值表 + 箱线图排版说明 |
| `demo_notes.md` | 分子 Demo 图生成逻辑、`predictions.csv` 预测对齐说明 |

## 复现命令（conda 环境 `da`）

当前 B 成员的模型、日志和预测结果已经生成完成。成员 C 做结果图时可直接使用 `outputs/features/predictions.csv`，无需重新训练 GNN。

若需要从头复现全部流程，再运行：

```bash
conda activate da
cd <仓库根目录>
python src/eda_qm9.py
python src/fingerprints.py   # 若尚未生成 outputs/features/*.npy
python src/train.py
python src/train_physics.py
python src/predict.py
python src/cluster_kmeans.py
python src/demo_molecules.py
```
