from torch_geometric.datasets import QM9
dataset = QM9(root='./data/qm9')

print(f"分子总数: {len(dataset)}")        # 应该输出 130831
print(f"第一个分子: {dataset[0]}")
# 输出类似：Data(x=[5, 11], edge_index=[2, 8], y=[1, 19])
# 意思是：5个原子，11个特征，8条化学键，19个目标性质