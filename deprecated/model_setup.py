import torch
import torch.nn as nn
import torch.optim as optim

from model_multiview import MultiViewResNet

device = "cuda" if torch.cuda.is_available() else "cpu"
model = MultiViewResNet().to(device)
opt = optim.Adam(model.parameters(), lr=1e-4)
criterion = nn.CrossEntropyLoss()

print(f"模型已建立，使用設備：{device}")
