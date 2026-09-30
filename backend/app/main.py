import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .api.routes import router
from .config import settings
from .model.loader import load_predictor
from .utils.image_processing import InferenceError

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("tomatoguard")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.predictor = load_predictor()  # loaded ONCE
    except Exception:
        log.exception("Model failed to load")
        app.state.predictor = None
    yield


app = FastAPI(title="TomatoGuard AI", lifespan=lifespan)
if settings.origins:  # same-origin by default; set ALLOWED_ORIGINS only for a separate frontend host
    app.add_middleware(CORSMiddleware, allow_origins=settings.origins, allow_methods=["GET", "POST"], allow_headers=["*"])


def _err(status: int, msg: str):
    return JSONResponse(status_code=status, content={"success": False, "error": msg})


@app.exception_handler(InferenceError)
async def _inference_error(_: Request, exc: InferenceError):
    return _err(exc.status, exc.message)


@app.exception_handler(RequestValidationError)
async def _validation_error(_: Request, exc: RequestValidationError):
    return _err(400, "Invalid request. Please upload an image.")


@app.exception_handler(Exception)
async def _unhandled(_: Request, exc: Exception):
    log.exception("Unhandled error")
    return _err(500, "Something went wrong on our side. Please try again.")


app.include_router(router)
app.mount("/", StaticFiles(directory=settings.frontend_dir, html=True), name="frontend")
