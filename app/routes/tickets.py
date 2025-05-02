
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app import crud, schemas, models
from typing import List
from app.dependencies import get_db, get_current_user


router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
)

@router.post("/", response_model=schemas.TicketOut)
def create_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_ticket(db, ticket, user_id=current_user.id)

@router.get("/tickets/", response_model=List[schemas.TicketOut])
def read_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db)
):
    return crud.get_tickets(db=db, skip=skip, limit=limit)

@router.get("/my", response_model=list[schemas.TicketOut])
def read_my_tickets(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Ticket).filter(models.Ticket.user_id == current_user.id).all()
