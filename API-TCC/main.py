import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Carrega .env antes de importar módulos que usam as configurações.
load_dotenv(Path(__file__).resolve().parent / ".env")

from database import Base, engine  # noqa: E402
from models import Usuario  # noqa: E402,F401
from routers import usuarios  # noqa: E402

app = FastAPI(
    title="Clínica PSICO API",
    description="API do sistema Clínica PSICO",
    version="1.0.1",
)

# Em desenvolvimento, permite o React local. Em produção, configure FRONTEND_ORIGINS.
origens = os.getenv(
    "FRONTEND_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origem.strip() for origem in origens.split(",") if origem.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios.router)

# Conveniente para desenvolvimento. Em produção, prefira migrações (Alembic).
Base.metadata.create_all(bind=engine)


@app.get("/")
def inicio():
    return {"mensagem": "API Clínica PSICO funcionando!"}


@app.get("/health")
def health():
    return {"status": "ok"}
