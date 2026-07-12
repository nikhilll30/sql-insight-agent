"""Static server for the showcase site (docs/index.html).

This is what the sql-insight-ui service on Render runs. The site is a single
self-contained HTML file, so all this needs to do is serve it — plus a /health
endpoint so uptime checks and Render's port scan get a fast 200.

Run locally:
    uvicorn ui_server:app --port 8501
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

BASE_DIR = Path(__file__).resolve().parent
INDEX = BASE_DIR / "docs" / "index.html"

app = FastAPI(title="SQL Insight Agent — showcase site", docs_url=None, redoc_url=None)


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "showcase site is up"}


@app.get("/")
def index():
    return FileResponse(INDEX, media_type="text/html")
