import pandas as pd
from sklearn.model_selection import train_test_split

# 讀取 CSV
df = pd.read_csv("data/books.csv")

# 取得所有書的唯一 ID
book_ids = df["book_id"].unique()

# 按書切分 train / val
train_ids, val_ids = train_test_split(book_ids, test_size=0.2, random_state=42)

# 選出對應圖片
train_df = df[df["book_id"].isin(train_ids)]
val_df = df[df["book_id"].isin(val_ids)]

train_df.to_csv("data/train.csv", index=False)
val_df.to_csv("data/val.csv", index=False)

print("已完成 train/val CSV 分割")
