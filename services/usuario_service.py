from sqlalchemy.orm import Session
from passlib.context import CryptContext

from models import Usuario
from schemas import UsuarioCreate, UsuarioUpdate


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def criar_usuario(db: Session, usuario: UsuarioCreate):

    usuario_existente = db.query(Usuario).filter(
        Usuario.email == usuario.email
    ).first()

    if usuario_existente:
        return None

    senha_hash = pwd_context.hash(usuario.senha)

    novo_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha=senha_hash
    )

    try:
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
    except Exception:
        db.rollback()
        raise

    return novo_usuario


def autenticar_usuario(
    db: Session,
    email: str,
    senha: str
):
    usuario = db.query(Usuario).filter(
        Usuario.email == email
    ).first()

    if not usuario:
        return None

    if not pwd_context.verify(senha, usuario.senha):
        return None

    return usuario



def atualizar_usuario(
    db: Session,
    usuario_id: int,
    dados: UsuarioUpdate
):
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id
    ).first()

    if usuario is None:
        return None

    # Verifica se outro usuário já utiliza o e-mail
    email_existente = db.query(Usuario).filter(
        Usuario.email == dados.email,
        Usuario.id != usuario_id
    ).first()

    if email_existente:
        return "email_duplicado"

    usuario.nome = dados.nome
    usuario.email = dados.email

    try:
        db.add(atualizar_usuario())
        db.commit()
        db.refresh(atualizar_usuario())
    except Exception:
        db.rollback()
        raise
    return usuario



def excluir_usuario(
    db: Session,
    usuario_id: int
):
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id
    ).first()

    if usuario is None:
        return None

    try:
        db.add(excluir_usuario())
        db.commit()
        db.refresh(excluir_usuario())
    except Exception:
        db.rollback()
        raise

    return usuario
