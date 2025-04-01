from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Note schemas
class NoteBase(BaseModel):
    title: Optional[str] = None
    content: str
    interaction_type: str = "meeting"
    interaction_date: Optional[datetime] = None
    is_group: bool = False

class NoteCreate(NoteBase):
    contact_ids: List[int]  # IDs of contacts associated with this note

class NoteUpdate(NoteBase):
    content: Optional[str] = None
    title: Optional[str] = None
    interaction_type: Optional[str] = None
    interaction_date: Optional[datetime] = None
    is_group: Optional[bool] = None
    
class Note(NoteBase):
    id: int
    refined_content: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Schema for returning a note with associated contacts
class NoteWithContacts(Note):
    contact_ids: List[int] = []
    
    class Config:
        orm_mode = True