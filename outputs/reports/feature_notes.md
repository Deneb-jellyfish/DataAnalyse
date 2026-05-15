# Feature Export Notes

- Morgan fingerprint: radius=2, n_bits=2048。
- 指纹来源: `data/qm9/raw/gdb9.sdf` + `uncharacterized.txt` 跳过列表，与 **PyG `QM9` 条数一致**（约 130,831）；SDF 读取使用 `sanitize=False`（与 PyG 一致）。
- 数据切分: train/test = 8:2，random_state=42。
- `split_index.csv` 提供 index/source_index/mol_id/split/smiles/dipole 对齐信息。
- 聚类与随机森林建议使用 `X_all.npy` 或 `X_train.npy` 视任务而定。
