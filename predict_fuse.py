import os
import torch
import json
from torch.utils.data import DataLoader
from collections import defaultdict

from training.dataset import BookDataset
from training.model_multiview import MultiViewResNet
from utils.utils import fuse_with_position_awareness, calculate_confidence, describe_condition
import torch.nn.functional as F


CSV_PATH = "data/val_booklevel.csv"
IMG_DIR = "data/raw"


def predict(model, dataloader, device, num_classes=4):
    """
    改進版預測流程：
    - 將模型的 softmax 機率轉為連續分數 (0~3)
    - 保留 front/spine/back 三個視角的預測結果
    """
    model.eval()
    book_preds = defaultdict(dict)

    with torch.no_grad():
        for images_tuple, labels, book_ids in dataloader:
            front, spine, back = [x.to(device) for x in images_tuple]

            # 對三張圖分別計算預測
            for view_name, view_tensor in zip(["front", "spine", "back"], [front, spine, back]):
                outputs = model(view_tensor, view_tensor, view_tensor)
                for i, bid in enumerate(book_ids):
                    bid = str(bid)
                    preds = {}
                    for attr in ["corner", "cover", "dirty", "damage"]:
                        probs = F.softmax(outputs[attr][i], dim=-1)
                        score = float(torch.sum(probs * torch.arange(num_classes, device=device)))
                        preds[attr] = score
                    book_preds[bid][view_name] = preds
    return book_preds

def _predict_data():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"使用設備: {device}")

    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"📂 CSV 檔案不存在：{CSV_PATH}")
    if not os.path.exists(IMG_DIR):
        raise FileNotFoundError(f"📂 圖片資料夾不存在：{IMG_DIR}")

    dataset = BookDataset(CSV_PATH, IMG_DIR)
    dataloader = DataLoader(dataset, batch_size=4, shuffle=False)

    # === 載入模型 ===
    model = MultiViewResNet().to(device)
    if os.path.exists("multiview_book_model.pt"):
        model.load_state_dict(torch.load("multiview_book_model.pt", map_location=device))
        print("✅ 已載入模型權重 multiview_book_model.pt")
    else:
        print("⚠️ 未找到 multiview_book_model.pt，使用隨機初始化模型（示範）")

    # === 預測 ===
    print("\n開始預測...\n")
    preds = predict(model, dataloader, device)
    print(f"\n✅ 預測完成，共 {len(preds)} 本書\n")

    # === 融合與報告 ===
    fused = fuse_with_position_awareness(preds)

    print("=" * 70)
    print("📚 二手書書況分析報告".center(70))
    print("=" * 70)

    reports = {}

    for bid, attrs in sorted(fused.items(), key=lambda x: str(x[0])):
        # 改進後的 describe_condition
        level, desc, score = describe_condition(attrs)

        # 置信度計算
        avg_confidence, attr_confidences = calculate_confidence(preds, bid)

        reports[bid] = {
            "level": level,
            "score": round(float(score), 2),
            "confidence": round(float(avg_confidence), 4),
            "desc": desc,
            "attr_confidences": {k: round(v, 4) for k, v in attr_confidences.items()}
        }

        print(f"\n📖 Book ID: {bid}")
        print(f"   整體評級：{level}")
        print(f"   綜合分數：{score:.2f}/3.0")
        print(f"   預測置信度：{avg_confidence:.1%}")
        print(f"   詳細狀況：{desc}")
        print("-" * 70)

    # === 儲存結果 ===
    os.makedirs("results", exist_ok=True)
    out_path = "results/book_condition_report.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)

    print(f"\n📄 已將融合結果輸出至 {out_path}")
    print("\n分析完成！")
    return out_path

def get_predict_data():
    _predict_data()
    with open('results/book_condition_report.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data

# ==================================================
# 📖 主程式
# ==================================================
if __name__ == "__main__":
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"使用設備: {device}")

    # === 載入資料 ===
    csv_path = "data/val_booklevel.csv"
    img_dir = "data/images"

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"📂 CSV 檔案不存在：{csv_path}")
    if not os.path.exists(img_dir):
        raise FileNotFoundError(f"📂 圖片資料夾不存在：{img_dir}")

    dataset = BookDataset(csv_path, img_dir)
    dataloader = DataLoader(dataset, batch_size=4, shuffle=False)

    # === 載入模型 ===
    model = MultiViewResNet().to(device)
    if os.path.exists("multiview_book_model.pt"):
        model.load_state_dict(torch.load("multiview_book_model.pt", map_location=device))
        print("✅ 已載入模型權重 multiview_book_model.pt")
    else:
        print("⚠️ 未找到 multiview_book_model.pt，使用隨機初始化模型（示範）")

    # === 預測 ===
    print("\n開始預測...\n")
    preds = predict(model, dataloader, device)
    print(f"\n✅ 預測完成，共 {len(preds)} 本書\n")

    # === 融合與報告 ===
    fused = fuse_with_position_awareness(preds)

    print("=" * 70)
    print("📚 二手書書況分析報告".center(70))
    print("=" * 70)

    reports = {}

    for bid, attrs in sorted(fused.items(), key=lambda x: str(x[0])):
        # 改進後的 describe_condition
        level, desc, score = describe_condition(attrs)

        # 置信度計算
        avg_confidence, attr_confidences = calculate_confidence(preds, bid)

        reports[bid] = {
            "level": level,
            "score": round(float(score), 2),
            "confidence": round(float(avg_confidence), 4),
            "desc": desc,
            "attr_confidences": {k: round(v, 4) for k, v in attr_confidences.items()}
        }

        print(f"\n📖 Book ID: {bid}")
        print(f"   整體評級：{level}")
        print(f"   綜合分數：{score:.2f}/3.0")
        print(f"   預測置信度：{avg_confidence:.1%}")
        print(f"   詳細狀況：{desc}")
        print("-" * 70)

    # === 儲存結果 ===
    os.makedirs("results", exist_ok=True)
    out_path = "results/book_condition_report.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)

    print(f"\n📄 已將融合結果輸出至 {out_path}")
    print("\n分析完成！")
