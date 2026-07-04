# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import research, pdf, discord

app = FastAPI(title="Company Research AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(research.router, prefix="/api")
app.include_router(pdf.router, prefix="/api")
app.include_router(discord.router, prefix="/api")


@app.get("/")
def root():
    return {"status": "ok", "message": "Company Research AI backend is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}
