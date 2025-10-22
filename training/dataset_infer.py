import torch
from torch.utils.data import Dataset
from torchvision import transforms
from PIL import Image
import pandas as pd
import os

class InferenceBookDataset(Dataset):
    def __init__(self, csv_file, img_dir, transform=None):
        self.df = pd.read_csv(csv_file)
        self.img_dir = img_dir
        self.transform = transform or transforms.Compose([
            transforms.Resize((224,224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
        ])

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        book_id = row["book_id"]
        images = {}
        img_names = {}

        for view in ["front", "spine", "back"]:
            name = row.get(f"{view}_img", None)
            if pd.notna(name):
                path = os.path.join(self.img_dir, name)
                img = Image.open(path).convert("RGB")
                images[view] = self.transform(img)
                img_names[view] = name
            else:
                images[view] = torch.zeros(3,224,224)
                img_names[view] = None

        return images, book_id, img_names

    def __len__(self):
        return len(self.df)
