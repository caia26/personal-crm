import pytest
from fastapi import status
from datetime import datetime, UTC

def test_create_note(client):
    # First create a contact to associate with note
    contact_data = {
        "first_name": "John",
        "last_name": "Doe"
    }
    contact_response = client.post("/contacts/", json=contact_data)
    contact_id = contact_response.json()["id"]
    
    # Create note data
    note_data = {
        "title": "Test Note",
        "content": "Had coffee with John",
        "interaction_type": "coffee",
        "contact_ids": [contact_id],
        "interaction_date": datetime.now(UTC).isoformat()
    }
    
    response = client.post("/notes/", json=note_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["title"] == note_data["title"]
    assert data["content"] == note_data["content"]
    assert data["interaction_type"] == note_data["interaction_type"]
    assert "id" in data

def test_create_group_note(client):
    # Create multiple contacts
    contacts_data = [
        {"first_name": "Mark", "last_name": "Taylor"},
        {"first_name": "Sarah", "last_name": "Parker"},
        {"first_name": "James", "last_name": "Wilson"}
    ]
    
    contact_ids = []
    for contact_data in contacts_data:
        response = client.post("/contacts/", json=contact_data)
        assert response.status_code == status.HTTP_200_OK
        contact_ids.append(response.json()["id"])
    
    # Create group note data with multiple contacts
    note_data = {
        "title": "Team Meeting",
        "content": "Quarterly planning session",
        "interaction_type": "meeting",
        "is_group": True,
        "contact_ids": contact_ids,
        "interaction_date": datetime.now(UTC).isoformat()
    }
    
    # Create the group note
    response = client.post("/notes/", json=note_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Verify note was created with the right properties
    assert data["title"] == note_data["title"]
    assert data["content"] == note_data["content"]
    assert data["is_group"] == True
    assert "id" in data
    
    note_id = data["id"]
    
    # Verify the note is associated with all contacts
    for contact_id in contact_ids:
        contact_notes = client.get(f"/contacts/{contact_id}/notes")
        assert contact_notes.status_code == status.HTTP_200_OK
        notes = contact_notes.json()
        assert any(note["id"] == note_id for note in notes)

def test_add_contact_to_note(client):
    # Create two contacts
    contacts = [
        {"first_name": "Alice", "last_name": "Johnson"},
        {"first_name": "Bob", "last_name": "Wilson"}
    ]
    contact_ids = []
    for contact in contacts:
        response = client.post("/contacts/", json=contact)
        contact_ids.append(response.json()["id"])
    
    # Create note with first contact
    note_data = {
        "title": "Group Meeting",
        "content": "Team sync",
        "interaction_type": "meeting",
        "contact_ids": [contact_ids[0]]
    }
    note_response = client.post("/notes/", json=note_data)
    note_id = note_response.json()["id"]
    
    # Add second contact to note
    response = client.post(f"/notes/{note_id}/contacts/{contact_ids[1]}")
    assert response.status_code == status.HTTP_200_OK
    
    # Verify contact was added by checking contact's notes
    contact_notes = client.get(f"/contacts/{contact_ids[1]}/notes")
    assert any(note["id"] == note_id for note in contact_notes.json())

def test_remove_contact_from_note(client):
    # Create contact
    contact_data = {"first_name": "Charlie", "last_name": "Brown"}
    contact_response = client.post("/contacts/", json=contact_data)
    contact_id = contact_response.json()["id"]
    
    # Create note with contact
    note_data = {
        "title": "Initial Meeting",
        "content": "First contact",
        "interaction_type": "meeting",
        "contact_ids": [contact_id]
    }
    note_response = client.post("/notes/", json=note_data)
    note_id = note_response.json()["id"]
    
    # Remove contact from note
    response = client.delete(f"/notes/{note_id}/contacts/{contact_id}")
    assert response.status_code == status.HTTP_200_OK
    
    # Verify contact was removed
    contact_notes = client.get(f"/contacts/{contact_id}/notes")
    assert not any(note["id"] == note_id for note in contact_notes.json())

def test_read_notes(client):
    # Create a contact
    contact_data = {"first_name": "Jane", "last_name": "Smith"}
    contact_response = client.post("/contacts/", json=contact_data)
    contact_id = contact_response.json()["id"]
    
    # Create multiple notes
    notes = [
        {
            "title": "Coffee Chat",
            "content": "Met for coffee",
            "interaction_type": "coffee",
            "contact_ids": [contact_id]
        },
        {
            "title": "Phone Call",
            "content": "Discussed project",
            "interaction_type": "call",
            "contact_ids": [contact_id]
        }
    ]
    
    for note in notes:
        client.post("/notes/", json=note)
    
    response = client.get("/notes/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= len(notes)

def test_delete_note(client):
    # Create contact and note
    contact_data = {"first_name": "David", "last_name": "Lee"}
    contact_response = client.post("/contacts/", json=contact_data)
    contact_id = contact_response.json()["id"]
    
    note_data = {
        "title": "Delete Test",
        "content": "To be deleted",
        "interaction_type": "other",
        "contact_ids": [contact_id]
    }
    note_response = client.post("/notes/", json=note_data)
    note_id = note_response.json()["id"]
    
    # Delete the note
    response = client.delete(f"/notes/{note_id}")
    assert response.status_code == status.HTTP_200_OK
    
    # Verify note is deleted
    contact_notes = client.get(f"/contacts/{contact_id}/notes")
    assert not any(note["id"] == note_id for note in contact_notes.json())