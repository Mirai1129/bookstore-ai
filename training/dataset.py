# dataset.py
import os

import pandas as pd
import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms


class BookDataset(Dataset):
    def __init__(self, csv_file, img_dir, transform=None, line_id=None):
        self.df = pd.read_csv(csv_file)
        self.img_dir = img_dir
        self.transform = transform or transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        self.line_id = line_id

    def __len__(self):
        return len(self.df)

    # torch Dataset has to implement __getitem__
    def __getitem__(self, idx):
        row = self.df.iloc[idx] # 可以理解成二維的資料，然後 [列, 欄] 的抓資料
        book_id = row['book_id']
        book_views = ['front', 'spine', 'back']

        images = {}

        # if self.line_id is not None:
        #     for view in book_views:
        #         img_name = f"{self.line_id}_{view}"
        #         img_path = os.path.join(self.img_dir, img_name)
        #
        #         if img_name not in os.listdir(self.img_dir):
        #             continue
        #
        #         img = Image.open(img_path).convert('RGB')
        #         images[view] = self.transform(img)
        # else:
        #     for view in book_views:
        #         img_name = row[f"{view}_img"]
        #
        #         if pd.notna(img_name):
        #             img_path = os.path.join(self.img_dir, img_name)
        #             img = Image.open(img_path).convert('RGB')
        #             images[view] = self.transform(img)
        #         else:
        #             images[view] = torch.zeros(3, 224, 224)

        # TODO: 先看資料怎麼來的，csv 的 corner 這種欄位怎麼來的，如果沒有圖片要怎麼處理
        # TODO: 現在知道資料是從 label studio 出來的，意味著圖片目前需要先標記
        for view in book_views:
            img_name = row[f"{view}_img"]

            # if dataframe has name -> pd.notna will return a bool to represent there is data in there
            if pd.notna(img_name):
                img_path = os.path.join(self.img_dir, img_name)
                img = Image.open(img_path).convert('RGB')
                images[view] = self.transform(img)
            else:
                images[view] = torch.zeros(3, 224, 224)

        images_tuple = (images['front'], images['spine'], images['back'])

        labels = {
            'corner': int(row['corner']),
            'cover': int(row['cover']),
            'dirty': int(row['dirty']),
            'damage': int(row['damage'])
        }

        return images_tuple, labels, book_id
