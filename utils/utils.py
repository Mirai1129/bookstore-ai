"""
utils.py - 書況分析輔助函式
包含：
- fuse_with_position_awareness()
- calculate_confidence()
- describe_condition() (改進版，單項門檻)
Author: Team
Date: 2025-10-19
"""
import numpy as np


# ==================================================
# 📘 多圖融合（依部位權重）
# ==================================================
def fuse_with_position_awareness(pred_dict):
    """
    將多視角預測結果融合成單一書況分數
    pred_dict: dict
        {book_id: {"front": {...}, "spine": {...}, "back": {...}}}
    """
    relevance_matrix = {
        "front": {"corner": 1.0, "cover": 1.0, "dirty": 1.0, "damage": 1.0},
        "back": {"corner": 1.0, "cover": 1.0, "dirty": 1.0, "damage": 1.0},
        "spine": {"corner": 0.3, "cover": 1.0, "dirty": 1.0, "damage": 1.0}
    }

    fused = {}
    for book_id, imgs_data in pred_dict.items():
        avg_attrs = {k: 0.0 for k in ["corner", "cover", "dirty", "damage"]}
        total_weights = {k: 0.0 for k in ["corner", "cover", "dirty", "damage"]}

        for img_name, values in imgs_data.items():
            img_lower = str(img_name).lower() if img_name is not None else ""
            if "front" in img_lower:
                photo_type = "front"
            elif "back" in img_lower:
                photo_type = "back"
            elif "spine" in img_lower:
                photo_type = "spine"
            else:
                photo_type = "front"

            for attr, val in values.items():
                weight = relevance_matrix[photo_type][attr]
                avg_attrs[attr] += val * weight
                total_weights[attr] += weight

        for attr in avg_attrs:
            if total_weights[attr] > 0:
                avg_attrs[attr] /= total_weights[attr]

        fused[book_id] = avg_attrs

    return fused


# ==================================================
# 📊 一致性置信度
# ==================================================
def calculate_confidence(pred_dict, book_id):
    """
    計算各屬性一致性置信度
    返回：
    - avg_confidence: 所有屬性的平均置信度
    - confidences: 各屬性置信度 dict
    """
    imgs_data = pred_dict.get(book_id, {})
    confidences = {}

    for attr in ["corner", "cover", "dirty", "damage"]:
        values = [img_vals[attr] for img_vals in imgs_data.values()] if imgs_data else []
        if len(values) > 1:
            std = np.std(values)
            confidence = float(np.exp(-std))  # 標準差越大 → 信心越低
        elif len(values) == 1:
            confidence = 0.5
        else:
            confidence = 0.0
        confidences[attr] = confidence

    avg_confidence = float(np.mean(list(confidences.values()))) if confidences else 0.0
    return avg_confidence, confidences


# ==================================================
# 🧾 改進版書況描述（單項分數門檻）
# ==================================================
def describe_condition(attrs):
    """
    attrs: dict, 各屬性分數 {'corner':0~3, 'cover':0~3, 'dirty':0~3, 'damage':0~3}
    
    返回：
    - level: 整體評級 S/A/B/C
    - desc: 各屬性文字描述
    - score: 綜合加權分數
    """

    desc = []

    # ------------------------------
    # 文字描述閾值
    # ------------------------------
    def get_level_text(value):
        if value >= 2.5:
            return "嚴重"
        elif value >= 1.8:
            return "中度"
        elif value >= 1.0:
            return "輕微"
        else:
            return "良好"

    # 各屬性文字描述
    desc.append(f"書皮摺痕{get_level_text(attrs['corner'])} ({attrs['corner']:.2f})")
    desc.append(f"書皮磨損{get_level_text(attrs['cover'])} ({attrs['cover']:.2f})")
    desc.append(f"污漬程度{get_level_text(attrs['dirty'])} ({attrs['dirty']:.2f})")
    desc.append(f"破損程度{get_level_text(attrs['damage'])} ({attrs['damage']:.2f})")

    # ------------------------------
    # 綜合分數（加權平均）
    # ------------------------------
    weights = {"corner": 0.15, "cover": 0.35, "dirty": 0.30, "damage": 0.20}
    score = sum(attrs[k] * weights[k] for k in weights)

    # ------------------------------
    # 整體評級邏輯（單項限制 + 分數）
    # ------------------------------
    level = "S 級（近全新）"
    max_attr = max(attrs.values())

    # 單項門檻決定整體等級
    if max_attr >= 2.5:
        level = "C 級（嚴重損壞）"
    elif max_attr >= 2.0:
        level = "B 級（中度損壞）"
    elif max_attr >= 1.5:
        # 任一屬性稍高但沒達到 B 門檻，整體至少 A 級
        level = "A 級（輕微使用）"
    else:
        # 如果沒有單項高分，依加權分數決定 S/A
        if score >= 1.5:
            level = "A 級（輕微使用）"
        else:
            level = "S 級（近全新）"

    return level, "，".join(desc), score
