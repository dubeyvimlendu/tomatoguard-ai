# TomatoGuard AI

FastAPI + pretrained ViT (`wellCh4n/tomato-leaf-disease-classification-vit`, unchanged) + plain HTML/CSS/JS.
10 disease classes -> 3 categories (`backend/app/model/class_mapping.py`).

## Where things live
- Code + config: GitHub. Model weights (~343 MB): Hugging Face, downloaded at Render *build* time into `backend/models/tomato_vit` (git-ignored), loaded into RAM once at startup.

## Run locally
    cd backend
    python -m venv .venv && .venv\Scripts\activate        # macOS/Linux: source .venv/bin/activate
    pip install -r requirements.txt
    copy .env.example .env                                  # optional
    python run.py                                           # http://127.0.0.1:8000  (HOST / PORT env vars respected)
Model source: if `backend/models/tomato_vit` already holds the model it is used; otherwise it is downloaded from `MODEL_ID`.

## Test
    curl http://127.0.0.1:8000/api/health
    curl -F "image=@leaf.jpg" http://127.0.0.1:8000/api/predict

## Deploy on Render
Blueprint in `render.yaml` (plan `1c-2g`, 1 worker, health check `/api/health`). Start command:
`cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
One worker on purpose: every worker process would hold its own ~1 GB copy of the model.
