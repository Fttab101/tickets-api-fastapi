from enum import Enum as PyEnum
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional
from datetime import datetime, timezone
#
#***** TICKETS **************************
#
# Enumeración para el estado del ticket
class StatusEnum(str, PyEnum):
    open = "open"
    closed = "closed"
    in_progress = "in_progress"

# Token
class Token(BaseModel):
    access_token: str
    token_type: str

# Crear Usuario
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


# Crear UserOut esquema limpio para las respuestas

class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True  # necesario para extraer desde modelos ORM

# Base común para Ticket
class TicketBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=5)
    status: Optional[StatusEnum] = StatusEnum.open

    @field_validator("title")
    def title_must_not_be_just_whitespace(cls, v):
        if not v.strip():
            raise ValueError("El título no puede estar vacío o solo espacios")
        return v


# Crear Ticket (POST)
class TicketCreate(TicketBase):
    model_config = ConfigDict(from_attributes=True)


# Actualizar Ticket (PATCH)
class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=5)
    status: Optional[StatusEnum] = None

    @field_validator("title")
    def title_must_not_be_just_whitespace(cls, v):
        if v is not None and not v.strip():
            raise ValueError("El título no puede estar vacío o solo espacios")
        return v


# Leer Ticket (GET)
class TicketRead(BaseModel):
    id: int
    title: str
    description: str
    status: StatusEnum

    model_config = ConfigDict(from_attributes=True)


# Crear TicketOut esquema limpio para las respuestas
class TicketOut(BaseModel):
    id: int
    title: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
    user_id: int  # opcional: lo puedes omitir si no quieres mostrarlo
    user: "UserOut"  # anidado

    class Config:
        from_attributes = True  # Necesario para usar con ORM (Pydantic v2)

#
#***** USERS **************************
#



# Al final del archivo:
TicketOut.model_rebuild()