"""Build-time step: fetch the model from Hugging Face into MODEL_PATH (skipped if already there)."""
from app.model.loader import ensure_model_dir

print("Model ready at", ensure_model_dir())
