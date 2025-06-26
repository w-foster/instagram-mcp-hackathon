# app/main.py

from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI(title="Instagram MCP Backend")

# Mount API routes under /api prefix
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the Instagram MCP backend!"}
