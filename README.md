# 分子性质预测（QM9）——图神经网络 + 聚类分析

本项目基于 **QM9** 分子数据集，完成“给定分子原子/化学键结构，预测分子物理性质（以**偶极矩**为主要目标）”的任务；同时结合 **KMeans + 降维可视化** 等方法，对分子进行聚类分析，观察不同分子簇在性质分布与模型误差上的差异。

项目思路（简版）：
- **数据**：QM9（约 13 万个小分子，元素包含 H/C/N/O/F）
- **建模对比**：传统机器学习基线（如随机森林，基于分子指纹） vs 图神经网络（基于分子图）
- **物理先验**：可在节点特征中加入电负性/杂化/芳香性等信息，观察对精度的提升
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

## 目录结构（当前仓库）

- `requirements.txt`：成员 A 流水线主要 Python 依赖（含 PyG / RDKit）
- `data.py`：QM9 数据集下载/读取示例（基于 `torch_geometric.datasets.QM9`）
- `项目说明书_分子性质预测_v2.docx`：项目说明书（更详细的背景、流程与分工）
- `package.json` / `package-lock.json`：用于处理 docx 的 Node 依赖（如需）

## 备注

如你希望 README 里进一步补充：
- 训练脚本用法（如 `train.py`）、模型结构说明（如 `model.py`）
- 评估指标（RMSE/MAE）、可视化输出示例、聚类分析输出

把对应脚本/文件发我或告诉我文件名，我可以把 README 补全成可直接复现实验的版本。

