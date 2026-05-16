# Feature Export Notes

- Morgan fingerprint: radius=2, n_bits=2048.
- Fingerprints are read from `data/qm9/raw/gdb9.sdf` with `sanitize=False` and the QM9 `uncharacterized.txt` skip list, matching the PyG QM9 filtered dataset.
- Split: train/test = 8:2, random_state=42.
- `split_index.csv` provides dataset_index/index/source_index/mol_id/split/split_order/smiles/dipole alignment fields.
- `dataset_index` matches the PyG QM9 dataset index used by the GNN scripts.
- `split_order` matches the row order inside `X_train.npy` or `X_test.npy` for each split.
