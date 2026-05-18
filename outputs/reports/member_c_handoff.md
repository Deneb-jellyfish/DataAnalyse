# 成员 C 交接说明

本文件面向成员 D，用于快速定位成员 C 已完成的实验结果、聚类误差分析与可直接放入报告的图表。

## 1. 三组模型对比结论

实验结果总表见：

- `outputs/reports/experiment_results.md`
- `outputs/logs/experiment_results.csv`

当前三组模型测试集指标如下：

| 模型 | MSE | RMSE | MAE |
|------|-----|------|-----|
| Physics GNN | 0.3958 | 0.6291 | 0.4513 |
| Base GNN | 0.5293 | 0.7275 | 0.5231 |
| Random Forest | 0.6029 | 0.7765 | 0.5228 |

可直接写入报告的结论：

- Physics GNN 的整体效果最好，说明在图结构基础上继续加入物理先验可以显著提升偶极矩预测精度。
- Base GNN 明显优于 Random Forest，说明保留分子结构信息比仅使用分子指纹更有效。
- Physics GNN 相比 Random Forest 的 RMSE 下降约 18.98%，可作为“结构建模 + 物理先验优于传统基线”的核心证据。

## 2. 聚类误差分析结论

聚类误差分析文档见：

- `outputs/reports/cluster_error_analysis.md`
- `outputs/logs/cluster_error_metrics.csv`
- `outputs/features/cluster_error_metrics.csv`

当前聚类误差分析的核心发现：

- Physics GNN 在 **Cluster 2** 上误差最低，RMSE 为 `0.5187`。
- Physics GNN 在 **Cluster 1** 上误差最高，RMSE 为 `0.7744`。
- **Cluster 4** 的含 F 分子比例最高（`6.74%`），但最差簇并不是 F 比例最高的簇。

建议报告里这样表述：

- 含 F 分子比例更高的簇整体更难预测，说明稀有元素分布不均衡确实会放大模型误差。
- 但最差簇不一定恰好是 F 比例最高的簇，说明误差还受到其它结构因素共同影响，例如局部键极性、分子几何布局和子结构复杂度。
- 因此，“数据不均衡是瓶颈”成立，但不应被简化成“只要含 F 就最难”。

## 3. Demo 图说明

Demo 说明见：

- `outputs/reports/demo_notes.md`
- `outputs/features/demo_selection.csv`
- `outputs/figures/demo/demo_mols.png`

当前 Demo 已经切换为**真实预测**：

- 使用 `outputs/features/predictions.csv` 中的 `y_pred_physics`
- 按 `dataset_index` 与 `split_index.csv` 对齐
- 在测试集真实预测样本中挑选 **5 个误差最小 + 5 个误差最大** 的分子

报告里适合这样使用：

- 放在“案例分析”或“误差可视化”小节
- 展示模型在具体分子上的预测差异
- 结合 `contains_F` 字段辅助解释误差大的样本

## 4. 可直接放入报告的图

推荐优先使用以下 5 张：

- `outputs/figures/results/exp_rmse_bar.png`
- `outputs/figures/results/best_model_scatter.png`
- `outputs/figures/results/gnn_loss_curves.png`
- `outputs/figures/results/cluster_rmse_bar.png`
- `outputs/figures/results/heatmap_model_cluster.png`

如果版面足够，还可以补充：

- `outputs/figures/results/violin_error_dist.png`
- `outputs/figures/results/cluster_mae_bar.png`
- `outputs/figures/demo/demo_mols.png`

## 5. 成员 D 写作建议

`Experiments` 章节建议结构：

1. 先给出三组模型总体指标表  
2. 再说明 Physics GNN 最优、Random Forest 最差  
3. 接着展示预测散点图与训练曲线  
4. 最后引入聚类误差分析，说明不同分子簇存在系统性难度差异  

一句可直接改写进结论的话：

> 实验表明，保留分子图结构可显著优于基于分子指纹的传统随机森林方法，而进一步引入电负性、键极性与空间几何等物理先验后，模型误差继续下降；聚类分析进一步说明，不同分子簇的预测难度存在明显差异，稀有元素与特定结构模式共同构成主要误差来源。
