import logging

from ..model.class_mapping import LABELS, category_for, display_name
from ..model.predictor import Predictor
from ..schemas.prediction import PredictionResponse
from ..utils.image_processing import InferenceError, read_and_validate

log = logging.getLogger("tomatoguard")


def run_inference(predictor: Predictor | None, filename, content_type, data: bytes) -> PredictionResponse:
    if predictor is None:
        raise InferenceError(503, "The analysis model is not available right now. Please try again later.")
    image = read_and_validate(filename, content_type, data)
    try:
        probs = predictor.predict(image)
    except Exception:
        log.exception("Inference failed")
        raise InferenceError(500, "Analysis failed. Please try again with another image.")
    ranked = sorted(range(len(probs)), key=probs.__getitem__, reverse=True)
    top = ranked[0]
    return PredictionResponse(
        predicted_disease=display_name(top),
        original_label=LABELS[top][0],
        category=category_for(top),
        confidence=round(probs[top], 4),
        probabilities={display_name(i): round(probs[i], 4) for i in ranked},
    )
