from fastapi import FastAPI
from app.api.routes import router as api_router
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from app.utils.check_pending_chats import run_periodic_check

app = FastAPI(title="Instagram MCP Backend")

origins = [
    "http://localhost:8080",  # React dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the Instagram MCP Hackathon backend!"}

# @app.on_event("startup")
# async def startup_event():
#     # start your periodic check as a background task
#     asyncio.create_task(run_periodic_check())
