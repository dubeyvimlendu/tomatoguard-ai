from fastapi import APIRouter, File, Request, Response, UploadFile

from ..schemas.prediction import HealthResponse, PredictionResponse
from ..services.inference_service import run_inference
from ..utils.image_processing import InferenceError

router = APIRouter(prefix="/api")


@router.get("/health", response_model=HealthResponse)
def health(request: Request, response: Response):
    loaded = request.app.state.predictor is not None
    if not loaded:  # non-2xx makes Render treat a deploy without a working model as failed
        response.status_code = 503
    return HealthResponse(status="healthy" if loaded else "degraded", model="tomato-vit", model_loaded=loaded)


@router.post("/predict", response_model=PredictionResponse)
async def predict(request: Request, image: UploadFile = File(None)):
    if image is None:
        raise InferenceError(400, "No image received. Please choose a tomato leaf photo.")
    data = await image.read()
    return run_inference(request.app.state.predictor, image.filename, image.content_type, data)
