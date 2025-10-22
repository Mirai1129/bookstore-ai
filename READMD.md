## 初始化專案

```bash
pip install -r requirements.txt
```

## 運行專案

```bash
uvicorn main:app
```

## API 使用

```
POST /checkBook
POST /uploadImage # TODO
```

## 已知問題

1. 預測圖片是用 load csv 的方式，所以圖片會用 csv 寫死的去找檔名


## 一堆屁話

特徵	說明
corner	折角程度
cover	封面磨損
dirty	污漬 / 泛黃
damage	破損或缺角


基本格式
model_multiview.py
dataloader_setup.py


模型訓練執行
├─ split_data.py       # 步驟 1：切分 train/val CSV
├─ convert_to_book_level.py  #修改CSV檔案格式使用
├─ dataloader_setup.py # 步驟 2：建立 Dataset + DataLoader
├─ model_setup.py      # 步驟 3：建立模型、optimizer、loss、device
├─ train_loop.py       # 步驟 4：訓練循環

book_model.pt  # 訓練好的模型

### 預測
├── utils.py          ← 工具函式（融合 + 書況分析）
├── predict_books.py  ← 主程式（載入模型 + 推論 + 輸出）
├── dataset_infer.py  ← 預測階段用 Dataset（不含 label）
