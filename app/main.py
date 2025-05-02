from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List
from sqlalchemy.orm import Session
from . import schemas, crud, models, database, utils
from app.routes import tickets
from app.dependencies import get_db, get_current_user
from app.routes import auth
import datetime


models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.include_router(tickets.router, prefix="/api", tags=["Tickets"])
app.include_router(auth.router)

# OAuth2PasswordBearer es el esquema de seguridad para la autenticación.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Endpoint de login
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
        )

    # Crear un JWT token
    access_token_expires = datetime.timedelta(minutes=15)
    access_token = utils.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint para crear un nuevo ticket (POST)
@app.post("/tickets/", response_model=schemas.TicketRead)
def create_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    return crud.create_ticket(db, ticket)


# Endpoint para obtener un ticket por ID (GET)
@app.get("/tickets/{ticket_id}", response_model=schemas.TicketRead)
def read_ticket(ticket_id: int, db: Session = Depends(get_db)):
    db_ticket = crud.get_ticket(db, ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    return db_ticket


# Endpoint para obtener una lista de tickets (GET)
@app.get("/tickets/", response_model=List[schemas.TicketRead])
def read_tickets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lista tickets con paginación:
    - skip: cuántos omitir (offset)
    - limit: cuántos devolver como máximo
    """
    return crud.get_tickets(db, skip=skip, limit=limit)


#Endpoint para listar tickets de un usuario
@app.get("/users/me/tickets/")
def read_my_tickets(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Ticket).filter(models.Ticket.user_id == current_user.id).all()


# Endpoint para reemplazar un ticket completo (PUT)
@app.put("/tickets/{ticket_id}", response_model=schemas.TicketRead)
def replace_ticket(ticket_id: int, ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    updated = crud.update_ticket(db, ticket_id, ticket)
    if not updated:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    return updated


# Endpoint para actualizar parcialmente un ticket (PATCH)
@app.patch("/tickets/{ticket_id}", response_model=schemas.TicketRead)
def patch_ticket(
    ticket_id: int,
    ticket: schemas.TicketUpdate,  # <- cambia aquí
    db: Session = Depends(get_db)
):
    updated = crud.update_ticket(db, ticket_id, ticket)
    if not updated:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    return updated

# Endpoint para eliminar un ticket (DELETE)
@app.delete("/tickets/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    success = crud.delete_ticket(db, ticket_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    return

# Asumimos que models.Base.metadata.create_all(...) ya está


# Endpoint para crear usuario
@app.post("/users/", status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    new_user = crud.create_user(db, user)
    return {"id": new_user.id, "username": new_user.username}
