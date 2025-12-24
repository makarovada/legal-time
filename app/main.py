from fastapi import FastAPI

app = FastAPI(title="LegalTime", version="0.1.0")

@app.get("/")
def root():
    return {"message": "LegalTime API is running!"}

@app.get("/debug-config")
def debug_config():
    return {
        "database_url": settings.DATABASE_URL,
        "google_client_id": settings.GOOGLE_CLIENT_ID,
        "fernet_key_set": settings.FERNET_KEY is not None
    }