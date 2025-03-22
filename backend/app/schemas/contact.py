from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Shared properties
class ContactBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

# Properties to receive on contact creation
class ContactCreate(ContactBase):
    pass

# Properties to receive on contact update
class ContactUpdate(ContactBase):
    pass

# Properties shared by models returned from API
class ContactInDBBase(ContactBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Properties to return to client
class Contact(ContactInDBBase):
    pass