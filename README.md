# 🍅 TomatoGuard AI

AI-powered tomato leaf disease classification using FastAPI, a pretrained Vision Transformer, and a simple HTML/CSS/JavaScript interface.

TomatoGuard AI analyzes an uploaded tomato leaf image, predicts one of **10 disease classes**, and maps the result into one of **3 broader categories**.

---

## ✨ Features

- FastAPI backend with REST API endpoints.
- Pretrained Vision Transformer model.
- 10 tomato leaf disease classes.
- Classification into 3 simplified categories.
- Plain HTML, CSS, and JavaScript frontend.
- Model loaded once during application startup.
- Local model caching to avoid repeated downloads.
- Render deployment configuration included.
- Health-check endpoint for monitoring.

---

## 🧠 Model

TomatoGuard AI uses the following pretrained model:

[`wellCh4n/tomato-leaf-disease-classification-vit`](https://huggingface.co/wellCh4n/tomato-leaf-disease-classification-vit)

The model weights are approximately **343 MB** and are downloaded from Hugging Face during the Render build process.

The downloaded model is stored at:

```text
backend/models/tomato_vit
```

This directory is ignored by Git.

---

## 🔄 How It Works

```text
Upload tomato leaf image
          │
          ▼
FastAPI prediction endpoint
          │
          ▼
Image preprocessing
          │
          ▼
Vision Transformer inference
          │
          ▼
Predict one of 10 disease classes
          │
          ▼
Map result to one of 3 categories
          │
          ▼
Display result in the frontend
```

---

## 📁 Project Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── model/
│   │       └── class_mapping.py
│   ├── models/
│   │   └── tomato_vit/          # Downloaded model files, ignored by Git
│   ├── requirements.txt
│   ├── run.py
│   └── .env.example
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── render.yaml
└── README.md
```

---

## ⚙️ Requirements

- Python 3.10 or newer.
- Git.
- Internet access during the first model download.
- Approximately 1 GB of RAM for model inference.
- Sufficient disk space for the model files.

---

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd <repository-folder>
```

### 2. Navigate to the backend

```bash
cd backend
```

### 3. Create a virtual environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Create the environment file

#### Windows

```bash
copy .env.example .env
```

#### macOS/Linux

```bash
cp .env.example .env
```

The `.env` file is optional.

### 6. Start the application

```bash
python run.py
```

The application will be available at:

```text
http://127.0.0.1:8000
```

---

## 🔌 API Endpoints

### Health Check

Check whether the API is running:

```bash
curl http://127.0.0.1:8000/api/health
```

Example response:

```json
{
  "status": "ok"
}
```

### Disease Prediction

Upload a tomato leaf image:

```bash
curl -F "image=@leaf.jpg" \
  http://127.0.0.1:8000/api/predict
```

The API returns the predicted disease class and its mapped category.

---

## 🗂️ Disease Category Mapping

The model predicts 10 original disease classes. These classes are grouped into 3 broader categories using:

```text
backend/app/model/class_mapping.py
```

This approach keeps the prediction detailed while making the final result easier for users to understand.

---

## 🧩 Environment Variables

| Variable | Description | Example |
|---|---|---|
| `MODEL_ID` | Hugging Face model identifier | `wellCh4n/tomato-leaf-disease-classification-vit` |
| `HOST` | Local server host | `127.0.0.1` |
| `PORT` | Local server port | `8000` |

If the model already exists locally at:

```text
backend/models/tomato_vit
```

TomatoGuard AI uses the local copy. Otherwise, it downloads the model from the value configured in `MODEL_ID`.

---

## ☁️ Deploy on Render

The repository includes a Render Blueprint:

```text
render.yaml
```

The deployment is configured with:

- Plan: `1c-2g`
- One worker.
- Health check endpoint: `/api/health`.
- Model download during the build process.

### Render Start Command

```bash
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Render Deployment Flow

```text
Render build starts
          │
          ▼
Install Python dependencies
          │
          ▼
Download model from Hugging Face
          │
          ▼
Store model in backend/models/tomato_vit
          │
          ▼
Start FastAPI with Uvicorn
          │
          ▼
Run health check at /api/health
```

---

## 🧠 Why Only One Worker?

The model is loaded into RAM by each worker process.

```text
1 worker  → 1 copy of the model
2 workers → 2 copies of the model
3 workers → 3 copies of the model
```

Each copy requires significant memory. TomatoGuard AI intentionally uses **one worker** so the deployment does not unnecessarily duplicate the approximately 1 GB runtime memory requirement.

---

## 🛠️ Troubleshooting

### Model download fails

Check that:

- `MODEL_ID` is correct.
- The Hugging Face repository is available.
- Render has internet access during the build.
- The deployment has enough disk space.
- The build process has enough time to download the model.

### Application runs out of memory

Check that:

- Only one worker is configured.
- Multiple Uvicorn processes are not running.
- The model is loaded once during startup.
- The Render instance has enough available RAM.

### Port errors

For local development, use:

```text
http://127.0.0.1:8000
```

For Render, use the platform-provided port:

```bash
--port $PORT
```

---

## 🧰 Technology Stack

- **Backend:** FastAPI
- **Inference:** Hugging Face Transformers
- **Model:** Vision Transformer
- **Frontend:** HTML, CSS, and JavaScript
- **Application Server:** Uvicorn
- **Deployment:** Render
- **Model Hosting:** Hugging Face

---

## 📄 License

Add the project license here.

Before using TomatoGuard AI in production, review the license and usage terms of the pretrained Hugging Face model.