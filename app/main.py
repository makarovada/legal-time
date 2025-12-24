from fastapi import FastAPI

app = FastAPI(title="LegalTime", version="0.1.0")

@app.get("/")
def root():
    return {"message": "LegalTime API is running!"}