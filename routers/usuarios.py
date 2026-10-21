from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt
import os
from datetime import datetime, timedelta

from database import get_db
from models import Usuario

from schemas import (
    UsuarioCreate,
    UsuarioLogin,
    UsuarioUpdate,
    UsuarioResponse
)

from services.usuario_service import (
    criar_usuario,
    autenticar_usuario,
    atualizar_usuario,
    excluir_usuario
)

from utils.auth import get_usuario_atual


router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"]
)


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


# =========================
# CADASTRAR USUÁRIO
# =========================

@router.post("/", response_model=UsuarioResponse)
def cadastrar_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):
    novo_usuario = criar_usuario(
        db,
        usuario
    )

    if novo_usuario is None:
        raise HTTPException(
            status_code=409,
            detail="E-mail já cadastrado"
        )

    return novo_usuario


# =========================
# LISTAR USUÁRIOS
# =========================

@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(
    db: Session = Depends(get_db)
):
    usuarios = db.query(Usuario).all()

    return usuarios


# =========================
# LOGIN
# =========================

@router.post("/login")
def login(
    dados: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    usuario = autenticar_usuario(
        db,
        dados.username,
        dados.password
    )

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha incorretos"
        )

    expiracao = datetime.utcnow() + timedelta(hours=2)

    token = jwt.encode(
        {
            "sub": str(usuario.id),
            "exp": expiracao
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# =========================
# BUSCAR USUÁRIO
# =========================


@router.get("/{usuario_id}", response_model=UsuarioResponse)
def buscar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual)
):
    # Impede consultar os dados de outro usuário
    if usuario_atual.id != usuario_id:
        raise HTTPException(
            status_code=403,
            detail="Você não pode consultar outro usuário"
        )

    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_atual.id
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    return usuario



# =========================
# ATUALIZAR USUÁRIO
# =========================

@router.put(
    "/{usuario_id}",
    response_model=UsuarioResponse
)
def atualizar_usuario_rota(
    usuario_id: int,
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual)
):
    if usuario_atual.id != usuario_id:
        raise HTTPException(
            status_code=403,
            detail="Você não pode alterar outro usuário"
        )

    usuario = atualizar_usuario(
        db,
        usuario_id,
        dados
    )
    if usuario == "email_duplicado":
        raise HTTPException(
            status_code=409,
            detail="E-mail já cadastrado"
        )
    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    return usuario


# =========================
# EXCLUIR USUÁRIO
# =========================

@router.delete("/{usuario_id}")
def excluir_usuario_rota(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual)
):
    if usuario_atual.id != usuario_id:
        raise HTTPException(
            status_code=403,
            detail="Você não pode excluir outro usuário"
        )

    usuario = excluir_usuario(
        db,
        usuario_id
    )

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    return {
        "mensagem": "Usuário excluído com sucesso"
    }