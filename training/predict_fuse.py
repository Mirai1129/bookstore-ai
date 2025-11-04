import datetime
import json
import os
from collections import defaultdict

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import transforms
from PIL import Image

from training.dataset import BookDataset
from training.model_multiview import MultiViewResNet
from utils.utils import describe_condition

CSV_PATH = "../data/val_booklevel.csv"
IMG_DIR = "../data/images"
MODEL_PATH = "multiview_book_model.pt"
REPORT_PATH = "../results/book_condition_report.json"

TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def predict_single_book(model, device,
                        front_img: Image.Image | None = None,
                        spine_img: Image.Image | None = None,
                        back_img: Image.Image | None = None):
    if not any([front_img, spine_img, back_img]):
        return {"error": "請至少上傳一張圖片"}

    files = {"front": front_img, "spine": spine_img, "back": back_img}
    imgs_tensors = {}

    for view, img in files.items():
        if img:
            imgs_tensors[view] = TRANSFORM(img).unsqueeze(0).to(device)
        else:
            imgs_tensors[view] = torch.zeros(1, 3, 224, 224).to(device)

    model.eval()
    with torch.no_grad():
        outputs = model(imgs_tensors["front"], imgs_tensors["spine"], imgs_tensors["back"])

    pred_scores = {}
    weights = torch.arange(4, device=device, dtype=torch.float) # 假設 num_classes=4

    for attr, logits in outputs.items():
        probs = F.softmax(logits, dim=-1)
        score = torch.sum(probs * weights, dim=-1).item()
        pred_scores[attr] = float(score)

    level, desc, score = describe_condition(pred_scores)

    return {
        "level": level,
        "score": round(score, 2),
        "desc": desc
    }

def _predict_batch(model, dataloader, device, num_classes=4):
    model.eval()
    book_preds = defaultdict(dict)
    weights = torch.arange(num_classes, device=device, dtype=torch.float)

    with torch.no_grad():
        for images_tuple, labels, book_ids in dataloader:
            front_batch = images_tuple[0].to(device)
            spine_batch = images_tuple[1].to(device)
            back_batch = images_tuple[2].to(device)

            outputs = model(front_batch, spine_batch, back_batch)

            scores_by_attr = {}
            for attr in ["corner", "cover", "dirty", "damage"]:
                logits = outputs[attr]
                probs = F.softmax(logits, dim=-1)
                batch_scores = torch.sum(probs * weights, dim=-1)
                scores_by_attr[attr] = batch_scores.cpu().tolist()

            for i, book_id in enumerate(book_ids):
                book_id = str(book_id)
                final_preds = {}
                for attr in scores_by_attr:
                    final_preds[attr] = scores_by_attr[attr][i]
                book_preds[book_id] = final_preds

    return book_preds

def _load_model_for_batch(device):
    """輔助函式：載入模型"""
    model = MultiViewResNet().to(device)
    if os.path.exists(MODEL_PATH):
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
        print(f"✅ 已載入模型權重 {MODEL_PATH}")
    else:
        print(f"⚠️ 未找到 {MODEL_PATH}，使用隨機初始化模型")
    return model

def run_batch_prediction():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"使用設備: {device}")

    if not os.path.exists(CSV_PATH) or not os.path.exists(IMG_DIR):
        raise FileNotFoundError("📂 CSV 或 圖片資料夾不存在")

    # 確保 BookDataset 在內部使用與 API 相同的 TRANSFORM
    dataset = BookDataset(CSV_PATH, IMG_DIR, transform=TRANSFORM)
    dataloader = DataLoader(dataset, batch_size=4, shuffle=False)

    model = _load_model_for_batch(device)

    print("\n開始預測...\n")
    preds = _predict_batch(model, dataloader, device) # 呼叫 Batch 函式
    print(f"\n✅ 預測完成，共 {len(preds)} 本書\n")

    print("=" * 70)
    print("📚 二手書書況分析報告".center(70))
    print("=" * 70)

    reports = {}
    for book_id, attrs in sorted(preds.items(), key=lambda x: str(x[0])):
        level, desc, score = describe_condition(attrs)
        reports[book_id] = {
            "level": level,
            "score": round(float(score), 2),
            "desc": desc,
        }

    os.makedirs("../results", exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)

    print(f"\n📄 已將融合結果輸出至 {REPORT_PATH}")
    print("\n分析完成！")
    return REPORT_PATH

def read_latest_report():
    if not os.path.exists(REPORT_PATH):
        raise FileNotFoundError(f"報告檔案 {REPORT_PATH} 不存在。請先執行 run_batch_prediction()。")

    with open(REPORT_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

if __name__ == "__main__":
    start_time = datetime.datetime.now()
    run_batch_prediction()
    print(f"\nTotal execution time: {datetime.datetime.now() - start_time}")