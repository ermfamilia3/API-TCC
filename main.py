from fastapi import FastAPI

from database import Base, engine
from models import Usuario
from routers import usuarios

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Minha API",
    description="API do meu TCC",
    version="1.0.0"
)

app.include_router(usuarios.router)


@app.get("/")
def inicio():
    return {
        "mensagem": "API funcionando!"
    }
