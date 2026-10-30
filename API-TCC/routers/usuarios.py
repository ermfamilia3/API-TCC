import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.orm import Session

from database import get_db
from models import Usuario
from schemas import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from services.usuario_service import (
    criar_usuario,
    autenticar_usuario,
    atualizar_usuario,
    excluir_usuario,
)
from utils.auth import get_usuario_atual

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


def _secret_key() -> str:
    if not SECRET_KEY:
        raise HTTPException(
            status_code=500,
            detail="SECRET_KEY não configurada no arquivo .env",
        )
    return SECRET_KEY


@router.post("/", response_model=UsuarioResponse, status_code=201)
def cadastrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    novo_usuario = criar_usuario(db, usuario)
    if novo_usuario is None:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
    return novo_usuario


@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(usuario_atual: Usuario = Depends(get_usuario_atual)):
    # Por segurança, esta rota retorna somente o usuário autenticado.
    # Para listar todos os usuários, implemente permissões de administrador.
    return [usuario_atual]


@router.post("/login")
def login(
    dados: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # OAuth2PasswordRequestForm recebe username/password como form-data.
    # Neste projeto, o campo username deve conter o e-mail.
    usuario = autenticar_usuario(db, dados.username, dados.password)
    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expiracao = datetime.now(timezone.utc) + timedelta(hours=2)
    token = jwt.encode(
        {"sub": str(usuario.id), "exp": expiracao},
        _secret_key(),
        algorithm=ALGORITHM,
    )
    return {"access_token": token, "token_type": "bearer"}


@router.get("/{usuario_id}", response_model=UsuarioResponse)
def buscar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    if usuario_atual.id != usuario_id:
        raise HTTPException(
            status_code=403,
            detail="Você não pode consultar outro usuário",
        )
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@router.put("/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario_rota(
    usuario_id: int,
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    if usuario_atual.id != usuario_id:
        raise HTTPException(
            status_code=403,
            detail="Você não pode alterar outro usuário",
        )

    usuario = atualizar_usuario(db, usuario_id, dados)
    if usuario == "email_duplicado":
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@router.delete("/{usuario_id}")
def excluir_usuario_rota(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    if usuario_atual.id != usuario_id:
        raise HTTPException(
            status_code=403,
            detail="Você não pode excluir outro usuário",
        )

    usuario = excluir_usuario(db, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"mensagem": "Usuário excluído com sucesso"}
