"""Deterministic 10 -> 3 mapping. Edit ONLY this file to change categories.
The order of LABELS must match the checkpoint's class indices (0..9)."""

HEALTHY, FUNGAL, OTHER = "HEALTHY", "FUNGAL", "OTHER_DISEASE"

# index -> (original model label, display name, operational category)
LABELS = [
    ("A healthy tomato leaf", "Healthy", HEALTHY),
    ("A tomato leaf with Leaf Mold", "Leaf Mold", FUNGAL),
    ("A tomato leaf with Target Spot", "Target Spot", FUNGAL),
    ("A tomato leaf with Late Blight", "Late Blight", FUNGAL),
    ("A tomato leaf with Early Blight", "Early Blight", FUNGAL),
    ("A tomato leaf with Bacterial Spot", "Bacterial Spot", OTHER),
    ("A tomato leaf with Septoria Leaf Spot", "Septoria Leaf Spot", FUNGAL),
    ("A tomato leaf with Tomato Mosaic Virus", "Tomato Mosaic Virus", OTHER),
    ("A tomato leaf with Tomato Yellow Leaf Curl Virus", "Tomato Yellow Leaf Curl Virus", OTHER),
    ("A tomato leaf with Spider Mites Two-spotted Spider Mite", "Spider Mites", OTHER),
]
NUM_CLASSES = len(LABELS)


def display_name(idx: int) -> str:
    return LABELS[idx][1]


def category_for(idx: int) -> str:
    return LABELS[idx][2]
