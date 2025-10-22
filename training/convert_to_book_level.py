#修改CSV檔案格式使用

import pandas as pd
import os

def convert_to_book_level(old_csv_path, new_csv_path):
    
    df = pd.read_csv(old_csv_path)

    books = {}
    for _, row in df.iterrows():
        book_id = row["book_id"]
        img_name = os.path.basename(row["image"])  # 只取檔名

        if book_id not in books:
            books[book_id] = {
                "book_id": book_id,
                "front_img": None,
                "spine_img": None,
                "back_img": None,
                "corner": 0,
                "cover": 0,
                "dirty": 0,
                "damage": 0
            }

        # 根據圖片名稱自動分配位置
        name = img_name.lower()
        if "front" in name:
            books[book_id]["front_img"] = img_name
        elif "spine" in name:
            books[book_id]["spine_img"] = img_name
        elif "back" in name:
            books[book_id]["back_img"] = img_name

        # 標籤取三張圖中最嚴重的那個（max）
        for attr in ["corner", "cover", "dirty", "damage"]:
            books[book_id][attr] = max(books[book_id][attr], row[attr])

    # 整理成 DataFrame
    new_df = pd.DataFrame(list(books.values()))
    new_df.to_csv(new_csv_path, index=False)

    print(f"CSV 轉換完成：{old_csv_path} → {new_csv_path}")
    print(f"共 {len(new_df)} 本書")
    print(f"新欄位：{list(new_df.columns)}")

    return new_df


if __name__ == "__main__":
    # 範例用法
    convert_to_book_level("data/train.csv", "data/train_booklevel.csv")
    convert_to_book_level("data/val.csv", "data/val_booklevel.csv")
