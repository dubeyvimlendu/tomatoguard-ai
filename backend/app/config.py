import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _path(value: str) -> Path:
    p = Path(value)
    return (p if p.is_absolute() else BASE_DIR / p).resolve()


class Settings:
    # Model source: local folder first (MODEL_PATH), else download MODEL_ID from Hugging Face.
    model_path = _path(os.getenv("MODEL_PATH", "models/tomato_vit"))
    model_id = os.getenv("MODEL_ID", "wellCh4n/tomato-leaf-disease-classification-vit")
    model_revision = os.getenv("MODEL_REVISION") or None  # optional commit hash to pin the exact weights
    hf_token = os.getenv("HF_TOKEN") or None  # only needed if the model repo is private

    max_upload_bytes = int(float(os.getenv("MAX_UPLOAD_MB", "8")) * 1024 * 1024)
    max_pixels = 40_000_000
    allowed_ext = {".jpg", ".jpeg", ".png", ".webp"}
    allowed_mime = {"image/jpeg", "image/png", "image/webp"}
    # Frontend is served by this same app, so CORS is only needed for a separately hosted frontend.
    origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]
    frontend_dir = BASE_DIR.parent / "frontend"


settings = Settings()
