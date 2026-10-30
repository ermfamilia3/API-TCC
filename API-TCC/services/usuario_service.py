from passlib.context import CryptContext
from sqlalchemy.orm import Session

from models import Usuario
from schemas import UsuarioCreate, UsuarioUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def criar_usuario(db: Session, usuario: UsuarioCreate):
    usuario_existente = (
        db.query(Usuario)
        .filter(Usuario.email == str(usuario.email).lower())
        .first()
    )
    if usuario_existente:
        return None

    novo_usuario = Usuario(
        nome=usuario.nome.strip(),
        email=str(usuario.email).lower(),
        senha=pwd_context.hash(usuario.senha),
    )

    try:
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
    except Exception:
        db.rollback()
        raise

    return novo_usuario


def autenticar_usuario(db: Session, email: str, senha: str):
    usuario = (
        db.query(Usuario)
        .filter(Usuario.email == email.strip().lower())
        .first()
    )
    if usuario is None or not pwd_context.verify(senha, usuario.senha):
        return None
    return usuario


def atualizar_usuario(db: Session, usuario_id: int, dados: UsuarioUpdate):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        return None

    email = str(dados.email).lower()
    email_existente = (
        db.query(Usuario)
        .filter(Usuario.email == email, Usuario.id != usuario_id)
        .first()
    )
    if email_existente:
        return "email_duplicado"

    usuario.nome = dados.nome.strip()
    usuario.email = email

    try:
        # O objeto já está associado à sessão; não chamar a própria função.
        db.commit()
        db.refresh(usuario)
    except Exception:
        db.rollback()
        raise

    return usuario


def excluir_usuario(db: Session, usuario_id: int):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        return None

    try:
        db.delete(usuario)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return usuario
