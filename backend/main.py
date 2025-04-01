from fastapi import FastAPI
from dotenv import load_dotenv
from app.api.endpoints import contact, note

# Load environment variables
load_dotenv()

# Create FastAPI instance
app = FastAPI(title="Personal CRM API")

# Include contact routes
app.include_router(contact.router, prefix="/contacts", tags=["contacts"])
app.include_router(note.router, prefix="/notes", tags=["notes"])

@app.get("/")
async def root():
    return {"message": "Welcome to Personal CRM API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)