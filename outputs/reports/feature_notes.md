# Feature Export Notes（指纹与切分）

## 产出文件（`outputs/features/`）

| 文件 | 说明 |
|------|------|
| `X_train.npy` / `X_test.npy` | Morgan 指纹，形状 `(N, 2048)`，`uint8` 0/1 |
| `y_train.npy` / `y_test.npy` | 偶极矩 `mu`（Debye），与指纹行一一对应 |
| `X_all.npy` / `y_all.npy` | 全量对齐后的指纹与标签（用于聚类或全量训练） |
| `split_index.csv` | 每行对应一个有效分子样本的索引与元数据 |
| `cluster_labels.npy` | 与 `X_all.npy` / `y_all.npy` 行顺序一致的簇编号 0–4 |

## 指纹定义

- **算法**: RDKit Morgan fingerprint（等价于 ECFP 类圆形指纹）
- **参数**: `radius=2`, `nBits=2048`
- **分子来源**: `data/qm9/raw/gdb9.sdf`（`sanitize=True`）
- **标签来源**: `data/qm9/raw/gdb9.sdf.csv` 中的 `mu` 列，按 SDF 顺序与成功解析的分子对齐

## `split_index.csv` 字段

| 列名 | 含义 |
|------|------|
| `index` | 0…N-1，与 `X_all.npy` 第 `index` 行对齐 |
| `source_index` | 原始 CSV/SDF 中的行序（0-based），便于回溯原始记录 |
| `mol_id` | 如 `gdb_1`，与 QM9 命名一致 |
| `split` | `train` 或 `test` |
| `smiles` | RDKit 导出的 SMILES（异构保留） |
| `dipole` | 真值偶极矩 mu（Debye） |

## 训练/测试切分

- **比例**: 80% / 20%
- **随机种子**: `random_state=42`（`sklearn.model_selection.train_test_split`）

## 给成员 C 的对接建议

1. 随机森林基线：可直接 `np.load("X_train.npy")` / `y_train.npy` 训练，在 `X_test.npy` 上评估。
2. 若需要簇内误差：用 `cluster_labels.npy` 与**同一顺序**的预测误差向量对齐（长度与 `X_all.npy` 一致）。
3. 若需从 `mol_id` 对齐其他表：优先用 `split_index.csv` 的 `mol_id` 或 `source_index`。
