from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Shared properties
class ContactBase(BaseModel):
    first_name: str
    last_name: str
    nickname: Optional[str] = None
    city: Optional[str] = None
    how_we_met: Optional[str] = None
    linkedin_url: Optional[str] = None

# Properties to receive on contact creation
class ContactCreate(ContactBase):
    pass

# Properties to receive on contact update
class ContactUpdate(ContactBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

# Properties shared by models returned from API
class ContactInDBBase(ContactBase):
    id: int
    last_contacted: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Forward reference for Note schema
from app.schemas.note import Note

# Properties shared by models returned from API
class ContactInDBBase(ContactBase):
    id: int
    last_contacted: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Properties to return to client
class Contact(ContactInDBBase):
    class Config:
        orm_mode = True