# GNN Notes（成员 B）

## 任务

成员 B 负责实现图神经网络模型，并完成基础 GNN 与物理先验 GNN 的训练、预测和结果导出。预测目标为 QM9 数据集中的偶极矩 `mu`。

## 数据划分

GNN 脚本统一读取成员 A 生成的：

```bash
outputs/features/split_index.csv
```

该文件包含 `dataset_index` 字段，可直接对应 PyG `QM9` 过滤后的样本索引。训练脚本不会再自行生成 split，确保 GNN、指纹、聚类和后续误差分析使用同一批 train/test 划分。

## 模型

基础模型 `MolGNN` 位于 `src/model.py`：

- 3 层 `GCNConv`
- ReLU 激活
- `global_mean_pool` 聚合分子图
- 全连接回归头输出偶极矩预测值

基础 GNN 使用 PyG QM9 默认节点特征。物理先验 GNN 在默认节点特征后额外拼接 10 维物理特征：

- 电负性
- 原子质量
- 共价半径
- 价电子数
- 是否为杂原子
- 节点度
- 局部键极性和
- 局部键极性绝对值和
- 到分子几何中心距离
- 归一化原子数

## 复现命令

当前结果已经生成完毕，成员 C 不需要重新训练，可直接使用：

```bash
outputs/features/predictions.csv
```

下面命令仅用于需要从头复现或覆盖已有结果时运行：

```bash
python src/fingerprints.py
python src/train.py
python src/train_physics.py
python src/predict.py
```

## 输出文件

| 文件 | 内容 |
|------|------|
| `outputs/models/gnn_base.pt` | 基础 GNN 最优权重 |
| `outputs/models/gnn_physics.pt` | 物理先验 GNN 最优权重 |
| `outputs/logs/train_gnn_base_metrics.csv` | 基础 GNN 每轮 `lr/train_mse/test_mse/epoch_seconds` |
| `outputs/logs/train_gnn_physics_metrics.csv` | 物理先验 GNN 每轮 `lr/train_mse/test_mse/epoch_seconds` |
| `outputs/features/predictions.csv` | 测试集真值、两个模型预测值和绝对误差 |

## 当前结果

| 模型 | MSE | RMSE | MAE |
|------|-----|------|-----|
| 基础 GNN | 0.5293 | 0.7275 | 0.5231 |
| 物理先验 GNN | 0.3958 | 0.6291 | 0.4513 |

物理先验 GNN 相比基础 GNN：

- MSE 下降约 25.2%
- RMSE 下降约 13.5%
- MAE 下降约 13.7%

## 报告撰写提示

可以写为：增强物理先验后，模型显式获得了与偶极矩相关的电负性、键极性和空间几何信息，因此测试集误差明显低于仅使用默认图节点特征的基础 GNN。
