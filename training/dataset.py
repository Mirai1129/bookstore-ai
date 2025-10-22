# dataset.py
import torch
from torch.utils.data import Dataset
from torchvision import transforms
from PIL import Image
import pandas as pd
import os

class BookDataset(Dataset):
    """一本書三張照片的 Dataset"""
    def __init__(self, csv_file, img_dir, transform=None):
        self.df = pd.read_csv(csv_file)
        self.img_dir = img_dir
        self.transform = transform or transforms.Compose([
            transforms.Resize((224,224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
        ])
    
    def __len__(self):
        return len(self.df)
    
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        book_id = row['book_id']
        
        # 載入三張圖
        images = {}
        for view in ['front', 'spine', 'back']:
            img_name = row[f"{view}_img"]
            if pd.notna(img_name):
                img_path = os.path.join(self.img_dir, img_name)
                img = Image.open(img_path).convert('RGB')
                images[view] = self.transform(img)
            else:
                images[view] = torch.zeros(3,224,224)
        
        # 轉成 tuple
        images_tuple = (images['front'], images['spine'], images['back'])
        
        # 標籤
        labels = {
            'corner': int(row['corner']),
            'cover': int(row['cover']),
            'dirty': int(row['dirty']),
            'damage': int(row['damage'])
        }
        
        return images_tuple, labels, book_id
