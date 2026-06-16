import socket
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.routers import items

app = FastAPI(title="Testing CI/CD API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items.router, prefix="/api")

Instrumentator().instrument(app).expose(app)


@app.get("/")
def root():
    return {"message": "API is running", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy", "instance": socket.gethostname()}
