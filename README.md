# 分子性质预测（QM9）——图神经网络 + 聚类分析

本项目基于 **QM9** 分子数据集，完成“给定分子原子/化学键结构，预测分子物理性质（以**偶极矩**为主要目标）”的任务；同时结合 **KMeans + 降维可视化** 等方法，对分子进行聚类分析，观察不同分子簇在性质分布与模型误差上的差异。

项目思路（简版）：
- **数据**：QM9（约 13 万个小分子，元素包含 H/C/N/O/F）
- **建模对比**：传统机器学习基线（如随机森林，基于分子指纹） vs 图神经网络（基于分子图）
- **物理先验**：在节点特征中加入电负性、原子质量、价电子数、键极性、空间位置等信息，观察对精度的提升
- **数据挖掘**：对分子指纹或图表示做聚类，并分析簇内性质分布与预测误差差异

## 数据集获取（QM9）

本项目使用 **PyTorch Geometric** 自带的数据集封装，运行时会自动下载 QM9 并缓存到本地目录。

1) 安装依赖（推荐，与成员 A 脚本一致）
```bash
pip install -r requirements.txt
```
若需指定 PyTorch 版本或 GPU 轮子，请先按 [PyTorch 官网](https://pytorch.org/get-started/locally/) 安装 `torch`，再执行 `pip install -r requirements.txt`（可跳过文件中已满足的 `torch` 行）。

2) 一行代码下载并验证（项目已提供示例脚本）
```bash
python data.py
```

默认会把数据下载到 `./data/qm9/`（如需更换位置，可修改 `data.py` 中的 `root` 参数）。

## 快速开始

- 数据下载与读取示例：`data.py`
- 运行后应能打印数据条数，以及一条样本的图结构信息（节点特征、边、标签等）。

### 成员 A：脚本建议执行顺序（自仓库根目录）

1. `python data.py` — 拉取/校验 PyG QM9  
2. `python src/eda_qm9.py` — 四张 EDA 图 + `outputs/reports/eda_notes.md`  
3. `python src/fingerprints.py` — Morgan 指纹与 `X_train.npy` / `X_test.npy` 等  
4. `python src/cluster_kmeans.py` — KMeans(k=5)、聚类图与 `cluster_labels.npy`  
5. `python src/demo_molecules.py` — `demo_mols.png`（若已有 `outputs/features/predictions.csv` 则使用真实预测，否则用占位噪声便于联调）

说明：`outputs/features/` 与 `outputs/figures/` 已在 `.gitignore` 中排除（体积大），克隆仓库后需按上述顺序在本地重新生成。

### 成员 B：GNN 训练与预测（自仓库根目录）

成员 B 负责图神经网络模型、基础 GNN 与物理先验 GNN 的训练，以及测试集预测结果导出。

当前仓库已经生成好 B 成员结果，成员 C 可直接读取：

```text
outputs/features/predictions.csv
outputs/logs/train_gnn_base_metrics.csv
outputs/logs/train_gnn_physics_metrics.csv
outputs/models/gnn_base.pt
outputs/models/gnn_physics.pt
```

其中 `predictions.csv` 是给成员 C 画散点图、计算 RMSE/MAE 的正式交付文件。下面命令仅用于需要从头复现或覆盖已有结果时运行。

运行前需先由成员 A 生成统一划分文件：

```bash
python src/fingerprints.py
```

该命令会生成 `outputs/features/split_index.csv`，后续 GNN 训练和预测都默认读取这个统一 split，不再单独创建划分。

按顺序运行：

```bash
python src/train.py
python src/train_physics.py
python src/predict.py
```

输出文件：

- `outputs/models/gnn_base.pt`：基础 GNN 权重
- `outputs/models/gnn_physics.pt`：物理先验 GNN 权重
- `outputs/logs/train_gnn_base_metrics.csv`：基础 GNN 每轮训练日志
- `outputs/logs/train_gnn_physics_metrics.csv`：物理先验 GNN 每轮训练日志
- `outputs/features/predictions.csv`：测试集真实值、两个模型预测值与误差，交给成员 C 画散点图和计算指标

`predictions.csv` 关键列：

- `y_true`：真实偶极矩
- `y_pred_base`：基础 GNN 预测值
- `y_pred_physics`：物理先验 GNN 预测值
- `abs_err_base`：基础 GNN 绝对误差
- `abs_err_physics`：物理先验 GNN 绝对误差

当前结果摘要：

| 模型 | MSE | RMSE | MAE |
|------|-----|------|-----|
| 基础 GNN | 0.5293 | 0.7275 | 0.5231 |
| 物理先验 GNN | 0.3958 | 0.6291 | 0.4513 |

物理先验模型使用的新增节点特征包括电负性、原子质量、共价半径、价电子数、是否为杂原子、节点度、局部键极性、绝对键极性、到分子几何中心距离和归一化原子数。

## 目录结构（当前仓库）

- `requirements.txt`：成员 A 流水线主要 Python 依赖（含 PyG / RDKit）
- `data.py`：QM9 数据集下载/读取示例（基于 `torch_geometric.datasets.QM9`）
- `src/model.py`：MolGNN 模型结构（GCNConv + global_mean_pool + 回归头）
- `src/train.py`：基础 GNN 训练脚本
- `src/train_physics.py`：物理先验 GNN 训练脚本
- `src/predict.py`：导出测试集预测结果到 `outputs/features/predictions.csv`
- `utils/dataset.py`：QM9 读取、统一 split 读取、物理先验特征构造
- `项目说明书_分子性质预测_v2.docx`：项目说明书（更详细的背景、流程与分工）
- `package.json` / `package-lock.json`：用于处理 docx 的 Node 依赖（如需）

## 备注

GitHub 上传时，`outputs/features/` 中只保留 `split_index.csv` 与 `predictions.csv`；大体积的指纹 `.npy` 文件仍由本地脚本重新生成。

