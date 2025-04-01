import pytest
from datetime import datetime, UTC
from fastapi import status

def test_create_contact(client):
    contact_data = {
        "first_name": "John",
        "last_name": "Doe",
        "nickname": "Johnny",
        "city": "New York",
        "how_we_met": "Work",
        "linkedin_url": "https://linkedin.com/in/johndoe"
    }
    
    response = client.post("/contacts/", json=contact_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["first_name"] == contact_data["first_name"]
    assert data["last_name"] == contact_data["last_name"]
    assert data["nickname"] == contact_data["nickname"]
    assert data["city"] == contact_data["city"]
    assert data["how_we_met"] == contact_data["how_we_met"]
    assert data["linkedin_url"] == contact_data["linkedin_url"]
    assert "id" in data
    assert "created_at" in data

def test_read_contact(client):
    # First create a contact
    contact_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "nickname": "Jenny"
    }
    create_response = client.post("/contacts/", json=contact_data)
    contact_id = create_response.json()["id"]
    
    # Then read it
    response = client.get(f"/contacts/{contact_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["first_name"] == contact_data["first_name"]
    assert data["last_name"] == contact_data["last_name"]
    assert data["nickname"] == contact_data["nickname"]

def test_read_contact_not_found(client):
    response = client.get("/contacts/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_read_contacts(client):
    # Create multiple contacts
    contacts = [
        {"first_name": "Alice", "last_name": "Johnson"},
        {"first_name": "Bob", "last_name": "Wilson"},
        {"first_name": "Charlie", "last_name": "Brown"}
    ]
    
    for contact in contacts:
        client.post("/contacts/", json=contact)
    
    response = client.get("/contacts/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= len(contacts)

def test_search_contacts(client):
    # Create contacts with different names and nicknames
    contacts = [
        {"first_name": "John", "last_name": "Smith"},
        {"first_name": "Johnny", "last_name": "Doe", "nickname": "JD"},
        {"first_name": "Jane", "last_name": "Smith", "nickname": "The Amazing Jane Smith"},
        {"first_name": "James", "last_name": "Wilson", "nickname": "Jimmy"}
    ]
    
    for contact in contacts:
        client.post("/contacts/", json=contact)
    
    # Test single word first name search
    response = client.get("/contacts/?search=John")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2  # Should find both John and Johnny
    
    # Test full name search
    response = client.get("/contacts/?search=John Smith")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1  # Should find John Smith
    
    # Test single word nickname search
    response = client.get("/contacts/?search=JD")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1  # Should find Johnny Doe
    
    # Test three word nickname search
    response = client.get("/contacts/?search=Amazing Jane Smith")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1  # Should find Jane Smith

def test_update_contact(client):
    # First create a contact
    contact_data = {
        "first_name": "Mike",
        "last_name": "Johnson"
    }
    create_response = client.post("/contacts/", json=contact_data)
    contact_id = create_response.json()["id"]
    
    # Update the contact
    update_data = {
        "nickname": "Mikey",
        "city": "San Francisco"
    }
    response = client.put(f"/contacts/{contact_id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["first_name"] == contact_data["first_name"]  # Unchanged
    assert data["last_name"] == contact_data["last_name"]    # Unchanged
    assert data["nickname"] == update_data["nickname"]
    assert data["city"] == update_data["city"]

def test_delete_contact(client):
    # First create a contact
    contact_data = {
        "first_name": "David",
        "last_name": "Lee"
    }
    create_response = client.post("/contacts/", json=contact_data)
    contact_id = create_response.json()["id"]
    
    # Delete the contact
    response = client.delete(f"/contacts/{contact_id}")
    assert response.status_code == status.HTTP_200_OK
    
    # Verify it's deleted
    get_response = client.get(f"/contacts/{contact_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND 