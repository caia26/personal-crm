from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import or_

from app.database.connection import get_db
from app.models.contact import Contact
from app.schemas.contact import Contact as ContactSchema, ContactCreate, ContactUpdate
from app.schemas.note import Note as NoteSchema

router = APIRouter()

@router.get("/", response_model=List[ContactSchema])
def read_contacts(
    search: Optional[str] = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Retrieve contacts with optional search.
    
    Search logic:
    - If one word: search in first_name OR last_name OR nickname
    - If two or more words: assume first word is first_name, second word is last_name
    - Also search the entire term in nickname
    """
    query = db.query(Contact)
    
    # Apply search if provided
    if search and search.strip():
        search_terms = [term.strip() for term in search.split() if term.strip()]
        
        if len(search_terms) == 1:
            # Single word - search in first_name OR last_name OR nickname
            term = search_terms[0]
            query = query.filter(
                or_(
                    Contact.first_name.ilike(f"%{term}%"),
                    Contact.last_name.ilike(f"%{term}%"),
                    Contact.nickname.ilike(f"%{term}%")
                )
            )
        else:
            # Split multiple words into first and second terms
            first_term, second_term = search_terms[:2]
            
            # Create first_name + last_name search
            name_filter = Contact.first_name.ilike(f"%{first_term}%") & Contact.last_name.ilike(f"%{second_term}%")
            
            # Also search the whole phrase in nickname
            query = query.filter(
                or_(
                    name_filter,
                    Contact.nickname.ilike(f"%{search}%")
                )
            )
    
    contacts = query.offset(skip).limit(limit).all()
    return contacts

@router.post("/", response_model=ContactSchema)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    """
    Create a new contact.
    """
    db_contact = Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

@router.get("/{contact_id}", response_model=ContactSchema)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    """
    Get a specific contact by ID.
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.put("/{contact_id}", response_model=ContactSchema)
def update_contact(contact_id: int, contact: ContactUpdate, db: Session = Depends(get_db)):
    """
    Update a contact.
    """
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    for key, value in contact.dict(exclude_unset=True).items():
        setattr(db_contact, key, value)
    
    db.commit()
    db.refresh(db_contact)
    return db_contact

@router.delete("/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    """
    Delete a contact.
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    db.delete(contact)
    db.commit()
    return {"message": "Contact deleted successfully"}

@router.get("/{contact_id}/notes", response_model=List[NoteSchema])
def get_contact_notes(
    contact_id: int, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Get all notes for a specific contact.
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    notes = contact.notes
    # Apply pagination after getting all notes
    # This is not the most efficient for very large datasets but works for this limited use case
    return notes[skip:skip+limit]