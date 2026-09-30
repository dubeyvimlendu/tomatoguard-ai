from pydantic import BaseModel


class PredictionResponse(BaseModel):
    success: bool = True
    predicted_disease: str
    original_label: str
    category: str
    confidence: float
    probabilities: dict[str, float]


class HealthResponse(BaseModel):
    status: str
    model: str
    model_loaded: bool
