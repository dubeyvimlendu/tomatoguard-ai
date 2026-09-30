"""Local convenience launcher. Production uses: uvicorn app.main:app --host 0.0.0.0 --port $PORT"""
import os

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8000")), reload=os.getenv("RELOAD") == "1")
