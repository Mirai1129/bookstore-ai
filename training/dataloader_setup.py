import torch
from torch.utils.data import DataLoader
from dataset import BookDataset

train_ds = BookDataset("data/train_booklevel.csv", "data/images")
val_ds = BookDataset("data/val_booklevel.csv", "data/images")

train_dl = DataLoader(train_ds, batch_size=16, shuffle=True, num_workers=4)
val_dl = DataLoader(val_ds, batch_size=16, num_workers=4)

print("Dataset 與 DataLoader 已建立")
