# train_loop_multiview.py
import torch
from tqdm import tqdm
from torch import nn, optim
from torch.utils.data import DataLoader

from dataset import BookDataset       # ← 你已經有的 dataset.py
from model_multiview import MultiViewResNet  # ← 多視角融合模型

# ------------------------------
# 參數
# ------------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
batch_size = 4
lr = 1e-4
epochs = 10

# ------------------------------
# DataLoader
# ------------------------------
train_ds = BookDataset("data/train_booklevel.csv", "data/images")
val_ds   = BookDataset("data/val_booklevel.csv", "data/images")

train_dl = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=4)
val_dl   = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=4)

# ------------------------------
# 模型、Loss、Optimizer
# ------------------------------
model = MultiViewResNet().to(device)
criterion = nn.CrossEntropyLoss()
opt = optim.Adam(model.parameters(), lr=lr)

# ------------------------------
# 訓練函數
# ------------------------------
def train_loop(dataloader):
    model.train()
    total_loss = 0
    tqdm_train = tqdm(dataloader, desc="Training", leave=False)
    
    for (front, spine, back), labels, _ in tqdm_train:
        front, spine, back = front.to(device), spine.to(device), back.to(device)
        labels = {k: v.to(device) for k, v in labels.items()}

        opt.zero_grad()
        outputs = model(front, spine, back)

        # 計算四個屬性 loss
        losses = {k: criterion(outputs[k], labels[k]) for k in outputs}
        loss = sum(losses.values())
        loss.backward()
        opt.step()

        total_loss += loss.item()
        tqdm_train.set_postfix({k: f"{v.item():.3f}" for k, v in losses.items()})
    
    return total_loss / len(dataloader)

# ------------------------------
# 驗證函數
# ------------------------------
def val_loop(dataloader):
    model.eval()
    total_loss = 0
    tqdm_val = tqdm(dataloader, desc="Validation", leave=False)
    
    with torch.no_grad():
        for (front, spine, back), labels, _ in tqdm_val:
            front, spine, back = front.to(device), spine.to(device), back.to(device)
            labels = {k: v.to(device) for k, v in labels.items()}

            outputs = model(front, spine, back)
            losses = {k: criterion(outputs[k], labels[k]) for k in outputs}
            loss = sum(losses.values())
            total_loss += loss.item()
            tqdm_val.set_postfix({k: f"{v.item():.3f}" for k, v in losses.items()})
    
    return total_loss / len(dataloader)

# ------------------------------
# 主程式
# ------------------------------
if __name__ == "__main__":
    import torch.multiprocessing
    torch.multiprocessing.freeze_support()  # Windows 必須

    for epoch in range(epochs):
        train_loss = train_loop(train_dl)
        val_loss = val_loop(val_dl)
        print(f"Epoch {epoch+1}/{epochs} | Train Loss={train_loss:.4f} | Val Loss={val_loss:.4f}")

    torch.save(model.state_dict(), "multiview_book_model.pt")
    print("✅ 模型訓練完成，已儲存為 multiview_book_model.pt")
