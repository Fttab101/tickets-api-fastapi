from sqlalchemy.orm import Session , joinedload
from . import models, schemas
from .utils import hash_password, verify_password
from .models import User



# Crear Usuario
def create_user(db: Session, user_in: schemas.UserCreate):
    hashed_pw = hash_password(user_in.password)
    db_user = models.User(username=user_in.username, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Autenticación credenciales

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

    
# Buscar Usuario por nombre
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

# Crear un nuevo ticket

def create_ticket(db: Session, ticket_in: schemas.TicketCreate, user_id: int) -> models.Ticket:
    ticket = models.Ticket(**ticket_in.model_dump(), user_id=user_id)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


# Obtener un ticket por ID con el usuario anidado
def get_ticket(db: Session, ticket_id: int):
    return (db.query(models.Ticket)
        .options(joinedload(models.Ticket.user))  # precargar el usuario
        .filter(models.Ticket.id == ticket_id)
        .first()
    )


# Obtener listado de ticket paginado
def get_tickets(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Ticket)
        .options(joinedload(models.Ticket.user))  # precarga el usuario
        .offset(skip)
        .limit(limit)
        .all()
    )



# Actualizar un ticket
def update_ticket(db: Session, ticket_id: int, ticket_in: schemas.TicketCreate) -> models.Ticket:
    db_ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not db_ticket:
        return None
    for field, value in ticket_in.model_dump(exclude_unset=True).items():
        setattr(db_ticket, field, value)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


# Actualizar parcialmente un ticket
def patch_ticket(db: Session, ticket_id: int, ticket_in: schemas.TicketUpdate):
    db_ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if db_ticket:
        if ticket_in.title:
            db_ticket.title = ticket_in.title
        if ticket_in.description:
            db_ticket.description = ticket_in.description
        if ticket_in.status:
            db_ticket.status = ticket_in.status
        db.commit()
        db.refresh(db_ticket)
        return db_ticket
    return None


# Eliminar un ticket
def delete_ticket(db: Session, ticket_id: int) -> bool:
    db_ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not db_ticket:
        return False
    db.delete(db_ticket)
    db.commit()
    return True

