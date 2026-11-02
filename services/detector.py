import os
import json

# Configure temporary writable directory for Ultralytics settings
os.environ.setdefault("YOLO_CONFIG_DIR", "/tmp/ultralytics")

from ultralytics import YOLO

MODEL_PATH = os.path.join("model", "yolo26n.pt")
PRODUCTS_PATH = os.path.join("config", "products.json")

model = YOLO(MODEL_PATH)

# Aliases for common detection variances (e.g. cylindrical bottles/tumblers often detected as cup)
CLASS_ALIASES = {
    "cup": "bottle"
}


def get_target_classes():
    """Returns the set of product classes currently in the catalog."""
    try:
        with open(PRODUCTS_PATH, "r") as file:
            products = json.load(file)
            return set(products.keys())
    except Exception:
        return {"cell phone", "laptop", "bottle", "mouse", "clock", "keyboard", "book"}


def get_allowed_class_ids():
    """
    Returns YOLO class IDs for catalog products only.
    Explicitly excludes 'person' (class 0) and any non-product objects.
    """
    target_names = get_target_classes()
    allowed_names = target_names.union(CLASS_ALIASES.keys())
    return [cid for cid, name in model.names.items() if name in allowed_names]


def detect_product(image_path, confidence_threshold=0.20):
    """
    Runs YOLO detection filtered exclusively to catalog products.
    'person' and background non-catalog objects are completely ignored.
    """
    target_classes = get_target_classes()
    allowed_ids = get_allowed_class_ids()

    # Pass allowed_ids to classes parameter so YOLO NMS ignores person and focuses on items
    results = model.predict(
        source=image_path,
        conf=confidence_threshold,
        classes=allowed_ids,
        imgsz=640,
        verbose=False
    )

    result = results[0]
    detections = []

    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        raw_class_name = model.names[class_id]

        # Map aliases if applicable
        class_name = CLASS_ALIASES.get(raw_class_name, raw_class_name)

        # Ensure class is in the product catalog and exclude any person detection
        if class_name not in target_classes or class_name.lower() == "person":
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

        detections.append({
            "class": class_name,
            "confidence": round(confidence, 3),
            "box": {
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2
            }
        })

    # Sort detections so highest confidence product comes first
    detections.sort(key=lambda d: d["confidence"], reverse=True)

    annotated_path = "data/annotated_result.jpg"
    os.makedirs("data", exist_ok=True)
    result.save(filename=annotated_path)

    return {
        "detections": detections,
        "annotated_image": "/" + annotated_path
    }
