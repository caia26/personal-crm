from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database.connection import get_db
from app.models.note import Note
from app.models.contact import Contact
from app.schemas.note import Note as NoteSchema, NoteCreate, NoteUpdate, NoteWithContacts

router = APIRouter()

@router.get("/", response_model=List[NoteSchema])
def read_notes(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Retrieve all notes.
    """
    notes = db.query(Note).offset(skip).limit(limit).all()
    return notes

@router.post("/", response_model=NoteSchema)
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    """
    Create a new note and associate it with contacts.
    This will also update the last_contacted timestamp for all associated contacts.
    """
    # Set interaction_date to now if not provided
    if not note.interaction_date:
        note.interaction_date = datetime.utcnow()
    
    # Create the note
    db_note = Note(
        title=note.title,
        content=note.content,
        interaction_type=note.interaction_type,
        interaction_date=note.interaction_date,
        is_group=note.is_group or len(note.contact_ids) > 1
    )
    db.add(db_note)
    db.flush()  # Flush to get the note ID
    
    # Associate contacts with the note
    contacts = db.query(Contact).filter(Contact.id.in_(note.contact_ids)).all()
    if not contacts:
        db.rollback()
        raise HTTPException(status_code=404, detail="No valid contacts found")
    
    # Update each contact's last_contacted time and add the note
    for contact in contacts:
        contact.last_contacted = note.interaction_date
        db_note.contacts.append(contact)
    
    db.commit()
    db.refresh(db_note)
    return db_note

@router.get("/{note_id}", response_model=NoteWithContacts)
def read_note(note_id: int, db: Session = Depends(get_db)):
    """
    Get a specific note by ID.
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Create the response with contact_ids included
    response = NoteWithContacts.from_orm(note)
    response.contact_ids = [contact.id for contact in note.contacts]
    return response

@router.put("/{note_id}", response_model=NoteSchema)
def update_note(note_id: int, note: NoteUpdate, db: Session = Depends(get_db)):
    """
    Update a note.
    """
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Update note fields
    update_data = note.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_note, key, value)
    
    db.commit()
    db.refresh(db_note)
    return db_note

@router.delete("/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    """
    Delete a note.
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(note)
    db.commit()
    return {"message": "Note deleted successfully"}

@router.post("/{note_id}/contacts/{contact_id}")
def add_contact_to_note(note_id: int, contact_id: int, db: Session = Depends(get_db)):
    """
    Associate a contact with a note.
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    if contact in note.contacts:
        return {"message": "Contact already associated with this note"}
    
    note.contacts.append(contact)
    
    # Update contact's last_contacted time if note's interaction_date is more recent
    if contact.last_contacted is None or note.interaction_date > contact.last_contacted:
        contact.last_contacted = note.interaction_date
    
    db.commit()
    return {"message": "Contact added to note successfully"}

@router.delete("/{note_id}/contacts/{contact_id}")
def remove_contact_from_note(note_id: int, contact_id: int, db: Session = Depends(get_db)):
    """
    Remove a contact's association with a note.
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    if contact not in note.contacts:
        return {"message": "Contact is not associated with this note"}
    
    note.contacts.remove(contact)
    db.commit()
    return {"message": "Contact removed from note successfully"}