import torch
from PIL import Image

from .class_mapping import NUM_CLASSES


class Predictor:
    def __init__(self, model, processor, device: str):
        self.model, self.processor, self.device = model, processor, device

    def predict(self, image: Image.Image) -> list[float]:
        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            logits = self.model(**inputs).logits
        probs = torch.softmax(logits, dim=-1)[0].cpu().tolist()
        assert len(probs) == NUM_CLASSES
        return probs
