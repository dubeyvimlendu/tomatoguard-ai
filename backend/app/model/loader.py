import logging
from pathlib import Path

import torch
from transformers import AutoImageProcessor, ViTForImageClassification

from ..config import settings
from .class_mapping import NUM_CLASSES
from .predictor import Predictor

log = logging.getLogger("tomatoguard")
WEIGHT_FILES = ["config.json", "preprocessor_config.json", "model.safetensors"]


def ensure_model_dir() -> Path:
    """Use the local MODEL_PATH if it holds a model; otherwise download MODEL_ID from
    Hugging Face INTO MODEL_PATH (only the 3 needed files). Runs at build time on Render
    and, as a fallback, once at startup. Never per request."""
    local = settings.model_path
    if (local / "config.json").exists() and (local / "model.safetensors").exists():
        return local
    from huggingface_hub import snapshot_download

    log.info("Downloading %s from Hugging Face", settings.model_id)
    snapshot_download(
        repo_id=settings.model_id, revision=settings.model_revision, token=settings.hf_token,
        local_dir=str(local), allow_patterns=WEIGHT_FILES,
    )
    return local


def _load_processor(model_dir: Path):
    """Same PIL-based ViT preprocessing either way. transformers 5.x gates AutoImageProcessor
    behind torchvision, which we deliberately don't install, so fall back to the identical
    ViTImageProcessor class that preprocessor_config.json names."""
    try:
        return AutoImageProcessor.from_pretrained(str(model_dir), backend="pil")
    except ImportError:
        from transformers import ViTImageProcessor

        log.info("AutoImageProcessor needs torchvision; using ViTImageProcessor (PIL backend)")
        return ViTImageProcessor.from_pretrained(str(model_dir))


def load_predictor() -> Predictor:
    """Load the fixed checkpoint once. Fails loudly if the trained classifier
    head (classifier.weight / classifier.bias) is not found in the weights."""
    model_dir = ensure_model_dir()
    processor = _load_processor(model_dir)
    model, info = ViTForImageClassification.from_pretrained(
        str(model_dir), num_labels=NUM_CLASSES, output_loading_info=True
    )
    missing = set(info.get("missing_keys", []))
    if {"classifier.weight", "classifier.bias"} & missing:
        raise RuntimeError("Trained classifier head missing from checkpoint; refusing to use a random head.")
    if tuple(model.classifier.weight.shape) != (NUM_CLASSES, 768):
        raise RuntimeError(f"Unexpected classifier shape {tuple(model.classifier.weight.shape)}")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device).eval()
    log.info("Model loaded on %s", device)
    return Predictor(model, processor, device)
