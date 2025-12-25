from fastapi import FastAPI
from app.routers import auth
from app.routers import auth, client, contract, matter, time_entry, employee


app = FastAPI(title="LegalTime", version="0.1.0")
app.include_router(auth.router)
app.include_router(auth.router)
app.include_router(client.router)
app.include_router(contract.router)
app.include_router(matter.router)
app.include_router(time_entry.router)
app.include_router(employee.router)

@app.get("/")
def root():
    return {"message": "LegalTime API is running!"}

## @app.get("/debug-config")
## def debug_config():
##    return {
##        "database_url": settings.DATABASE_URL,
##        "google_client_id": settings.GOOGLE_CLIENT_ID,
##        "fernet_key_set": settings.FERNET_KEY is not None
##    }